import grpc
from proto import chat_pb2, chat_pb2_grpc, common_pb2
from src.models.room import RoomStore
from src.models.message import MessageStore
from src.utils.room_manager import RoomManager
from src.clients.logging_client import LoggingClient
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
        """
        Streaming bidirectionnel pour le chat temps réel
        """
        message_queue = queue.Queue()
        room_id = None
        user_id = None
        
        def receive_messages():
            """Thread pour recevoir les messages du client"""
            nonlocal room_id, user_id
            
            try:
                for message in request_iterator:
                    room_id = message.room_id
                    user_id = message.user_id
                    
                    # Vérifier que l'utilisateur est membre de la room
                    room = self.room_store.get_room(room_id)
                    if not room or not room.has_member(user_id):
                        self.logger.warning(
                            f"Tentative d'envoi message sans être membre",
                            room_id=room_id,
                            user_id=user_id
                        )
                        continue
                    
                    # Vérifier la longueur du message
                    if len(message.content) > config.MAX_MESSAGE_LENGTH:
                        self.logger.warning(
                            f"Message trop long",
                            room_id=room_id,
                            user_id=user_id,
                            length=len(message.content)
                        )
                        continue
                    
                    # Stocker le message
                    stored_msg = self.message_store.add_message(
                        room_id=room_id,
                        user_id=user_id,
                        username=message.username,
                        content=message.content,
                        message_type=0  # TEXT
                    )
                    
                    # Créer le message gRPC
                    chat_msg = chat_pb2.ChatMessage(
                        id=stored_msg.id,
                        room_id=stored_msg.room_id,
                        user_id=stored_msg.user_id,
                        username=stored_msg.username,
                        content=stored_msg.content,
                        timestamp=stored_msg.timestamp,
                        type=chat_pb2.MessageType.TEXT
                    )
                    
                    # Broadcast à tous les membres de la room
                    self.room_manager.broadcast_to_room(room_id, chat_msg)
                    
                    # Logger
                    self.logger.info(
                        f"Message envoyé dans {room.name}",
                        room_id=room_id,
                        user_id=user_id,
                        username=message.username
                    )
            
            except Exception as e:
                self.logger.error(f"Erreur réception messages: {str(e)}")
        
        # Démarrer le thread de réception
        receive_thread = threading.Thread(target=receive_messages, daemon=True)
        receive_thread.start()
        
        # Attendre d'avoir le room_id et user_id
        import time
        for _ in range(50):  # Attendre max 5 secondes
            if room_id and user_id:
                break
            time.sleep(0.1)
        
        if room_id and user_id:
            # Enregistrer le stream
            self.room_manager.add_stream(room_id, user_id, message_queue)
            
            try:
                # Envoyer les messages de la queue
                while context.is_active():
                    try:
                        message = message_queue.get(timeout=1.0)
                        yield message
                    except queue.Empty:
                        continue
            finally:
                # Nettoyer à la déconnexion
                self.room_manager.remove_stream(room_id, user_id)
                self.logger.info(
                    f"Stream fermé",
                    room_id=room_id,
                    user_id=user_id
                )
    
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