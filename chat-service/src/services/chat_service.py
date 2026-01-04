import time
import grpc
import proto.chat_pb2 as chat_pb2
import proto.chat_pb2_grpc as chat_pb2_grpc
import proto.common_pb2 as common_pb2
from src.models import RoomStore, MessageStore
from src.utils import RoomManager
from src.clients import LoggingClient
from src.config import config
import queue
import threading

class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    """Implémentation du service de chat"""
    
    def __init__(self):
        self.room_store = RoomStore()
        self.message_store = MessageStore()
        self.room_manager = RoomManager()
        self.logger = LoggingClient()
        
        print(f"✅ Chat Service initialisé")
        self.logger.info("Chat Service démarré", service="chat-service")
    
    def CreateRoom(self, request, context):
        """Créer une nouvelle room de chat"""
        try:
            room = self.room_store.create_room(
                name=request.name,
                description=request.description,
                created_by=request.created_by
            )
            
            # Logger la création
            self.logger.info(
                f"Room créée: {room.name}",
                room_id=room.id,
                created_by=request.created_by
            )
            
            return chat_pb2.Room(
                id=room.id,
                name=room.name,
                description=room.description,
                created_by=room.created_by,
                created_at=room.created_at,
                member_count=0
            )
        
        except Exception as e:
            self.logger.error(f"Erreur création room: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def ListRooms(self, request, context):
        """Lister toutes les rooms disponibles"""
        try:
            rooms = self.room_store.list_rooms()
            
            room_list = [
                chat_pb2.Room(
                    id=room.id,
                    name=room.name,
                    description=room.description,
                    created_by=room.created_by,
                    created_at=room.created_at,
                    member_count=room.get_member_count()
                )
                for room in rooms
            ]
            
            self.logger.info(f"Liste rooms récupérée: {len(room_list)} rooms")
            
            return chat_pb2.ListRoomsResponse(
                rooms=room_list,
                total=len(room_list)
            )
        
        except Exception as e:
            self.logger.error(f"Erreur liste rooms: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def JoinRoom(self, request, context):
        """Rejoindre une room de chat"""
        try:
            room = self.room_store.get_room(request.room_id)
            
            if not room:
                self.logger.warning(f"Room non trouvée: {request.room_id}")
                return chat_pb2.JoinRoomResponse(
                    success=False,
                    message="Room not found"
                )
            
            # Vérifier la limite de membres
            if room.get_member_count() >= config.MAX_ROOM_MEMBERS:
                self.logger.warning(
                    f"Room pleine: {request.room_id}",
                    room_name=room.name
                )
                return chat_pb2.JoinRoomResponse(
                    success=False,
                    message="Room is full"
                )
            
            # Ajouter le membre
            room.add_member(request.user_id)
            
            # Message système
            join_message = self.message_store.add_message(
                room_id=request.room_id,
                user_id="system",
                username="System",
                content=f"{request.username} a rejoint la room",
                message_type=2  # JOIN
            )
            
            # Broadcast le message de join
            msg = chat_pb2.ChatMessage(
                id=join_message.id,
                room_id=join_message.room_id,
                user_id=join_message.user_id,
                username=join_message.username,
                content=join_message.content,
                timestamp=join_message.timestamp,
                type=chat_pb2.MessageType.JOIN
            )
            self.room_manager.broadcast_to_room(request.room_id, msg)
            
            # Logger
            self.logger.info(
                f"Utilisateur {request.username} a rejoint {room.name}",
                room_id=request.room_id,
                user_id=request.user_id
            )
            
            return chat_pb2.JoinRoomResponse(
                success=True,
                message="Successfully joined room",
                room=chat_pb2.Room(
                    id=room.id,
                    name=room.name,
                    description=room.description,
                    created_by=room.created_by,
                    created_at=room.created_at,
                    member_count=room.get_member_count()
                )
            )
        
        except Exception as e:
            self.logger.error(f"Erreur join room: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def LeaveRoom(self, request, context):
        """Quitter une room"""
        try:
            room = self.room_store.get_room(request.room_id)
            
            if not room:
                return common_pb2.Status(
                    success=False,
                    message="Room not found",
                    code=404
                )
            
            # Retirer le membre
            room.remove_member(request.user_id)
            
            # Message système
            leave_message = self.message_store.add_message(
                room_id=request.room_id,
                user_id="system",
                username="System",
                content=f"Un utilisateur a quitté la room",
                message_type=3  # LEAVE
            )
            
            # Broadcast
            msg = chat_pb2.ChatMessage(
                id=leave_message.id,
                room_id=leave_message.room_id,
                user_id=leave_message.user_id,
                username=leave_message.username,
                content=leave_message.content,
                timestamp=leave_message.timestamp,
                type=chat_pb2.MessageType.LEAVE
            )
            self.room_manager.broadcast_to_room(request.room_id, msg)
            
            # Logger
            self.logger.info(
                f"Utilisateur quitté room",
                room_id=request.room_id,
                user_id=request.user_id
            )
            
            return common_pb2.Status(
                success=True,
                message="Successfully left room",
                code=200
            )
        
        except Exception as e:
            self.logger.error(f"Erreur leave room: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def StreamMessages(self, request_iterator, context):
        message_queue = queue.Queue()
        room_id = None
        user_id = None
        username = None
        stop_event = threading.Event()

        def read_client():
            nonlocal room_id, user_id, username
            try:
                for msg in request_iterator:
                    if msg.type == chat_pb2.MessageType.JOIN:
                        room_id = msg.room_id
                        user_id = msg.user_id
                        username = msg.username

                        self.room_manager.add_stream(room_id, user_id, message_queue)

                        self.logger.info("Stream ouvert", room_id=room_id, user_id=user_id)

                    elif msg.type == chat_pb2.MessageType.TEXT:
                        stored = self.message_store.add_message(
                            room_id=room_id,
                            user_id=user_id,
                            username=username,
                            content=msg.content,
                            message_type=0
                        )

                        out = chat_pb2.ChatMessage(
                            id=stored.id,
                            room_id=room_id,
                            user_id=user_id,
                            username=username,
                            content=stored.content,
                            timestamp=stored.timestamp,
                            type=chat_pb2.MessageType.TEXT
                        )

                        self.room_manager.broadcast_to_room(room_id, out)

            except grpc.RpcError:
                pass
            finally:
                stop_event.set()

        threading.Thread(target=read_client, daemon=True).start()

        try:
            while context.is_active() and not stop_event.is_set():
                try:
                    msg = message_queue.get(timeout=1)
                    yield msg
                except queue.Empty:
                    continue
        finally:
            if room_id and user_id:
                self.room_manager.remove_stream(room_id, user_id)
                self.logger.info("Stream fermé", room_id=room_id, user_id=user_id)

    
    def GetRoomHistory(self, request, context):
        """Récupérer l'historique d'une room (streaming serveur)"""
        try:
            messages = self.message_store.get_room_history(
                room_id=request.room_id,
                limit=request.limit if request.limit > 0 else 100
            )
            
            self.logger.info(
                f"Historique récupéré",
                room_id=request.room_id,
                count=len(messages)
            )
            
            for msg in messages:
                yield chat_pb2.ChatMessage(
                    id=msg.id,
                    room_id=msg.room_id,
                    user_id=msg.user_id,
                    username=msg.username,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    type=msg.message_type
                )
        
        except Exception as e:
            self.logger.error(f"Erreur historique: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetRoomMembers(self, request, context):
        """Obtenir la liste des membres d'une room"""
        try:
            room = self.room_store.get_room(request.room_id)
            
            if not room:
                context.abort(grpc.StatusCode.NOT_FOUND, "Room not found")
            
            members = [
                chat_pb2.RoomMember(
                    user_id=user_id,
                    username=f"User-{user_id[:8]}",
                    joined_at=room.created_at
                )
                for user_id in room.members
            ]
            
            return chat_pb2.RoomMembersResponse(members=members)
        
        except Exception as e:
            self.logger.error(f"Erreur membres room: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
