from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import threading
import grpc
import sys
import os
import time
from queue import Empty, Queue
import eventlet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../proto'))

import chat_pb2
import chat_pb2_grpc
from src.config import config
from src.clients.auth_client import AuthClient

socketio = None
chat_stub = None
metadata = None
active_streams = {} 
STOP = object()

def init_socketio(app):
    """Initialiser SocketIO avec l'app Flask"""
    global socketio, chat_stub, metadata
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Créer le stub gRPC pour Chat Service
    channel = grpc.insecure_channel(
        f'{config.CHAT_SERVICE_HOST}:{config.CHAT_SERVICE_PORT}'
    )
    chat_stub = chat_pb2_grpc.ChatServiceStub(channel)
    metadata = [('x-api-key', config.CHAT_API_KEY)]
    
    print("✅ WebSocket Handler initialisé")
    register_handlers()
    
    return socketio

def register_handlers():
    """Enregistrer tous les événements WebSocket"""
    
    @socketio.on('connect')
    def handle_connect():
        """Client WebSocket connecté"""
        print(f"🔌 WebSocket connecté: {request.sid}")
        emit('connected', {'session_id': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Client WebSocket déconnecté"""
        session_id = request.sid
        print(f"🔌 WebSocket déconnecté: {session_id}")
        
        # Arrêter le stream gRPC si actif
        if session_id in active_streams:
            stream = active_streams[session_id]
            stream['running'] = False
            stream['message_queue'].put(STOP)
            del active_streams[session_id]

    
    @socketio.on('authenticate')
    def handle_authenticate(data):
        """Authentifier l'utilisateur avec son JWT"""
        token = data.get('token')
        
        if not token:
            emit('error', {'message': 'Token manquant'})
            return
        
        try:
            # Valider le token via Auth Service
            auth_client = AuthClient()
            result = auth_client.validate_token(token)
            
            # Vérifier que result n'est pas None
            if result and result.get('valid'):
                username = result.get('user', {}).get('username', 'Unknown')
                print(f"✅ Utilisateur authentifié: {username}")
                emit('authenticated', {'user': result.get('user')})
            else:
                print(f"❌ Token invalide ou result None")
                emit('error', {'message': 'Token invalide'})
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            emit('error', {'message': f'Erreur: {str(e)}'})
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Rejoindre une room et démarrer le streaming bidirectionnel"""
        session_id = request.sid
        room_id = data.get('room_id')
        user_info = data.get('user')
        
        if not room_id or not user_info:
            emit('error', {'message': 'room_id et user requis'})
            return
        
        print(f"📥 {user_info['username']} rejoint room {room_id}")
        
        try:
            # Rejoindre la room via gRPC
            join_request = chat_pb2.JoinRoomRequest(
                room_id=room_id,
                user_id=user_info['user_id'],
                username=user_info['username']
            )
            
            response = chat_stub.JoinRoom(join_request, metadata=metadata)
            
            if not response.success:
                emit('error', {'message': response.message})
                return
            
            join_room(room_id)
            print(f"✅ Session {session_id} a rejoint la room SocketIO {room_id}")
            emit('joined_chat', {'room_id': room_id, 'message': response.message})
            # Démarrer le streaming gRPC bidirectionnel
            start_grpc_stream(session_id, room_id, user_info)
            
        except Exception as e:
            print(f"❌ Erreur join_chat: {str(e)}")
            import traceback
            traceback.print_exc()
            emit('error', {'message': f'Erreur: {str(e)}'})
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Envoyer un message via le stream bidirectionnel"""
        session_id = request.sid
        
        if session_id not in active_streams:
            emit('error', {'message': 'Vous n\'êtes pas dans un chat actif'})
            return
        
        content = data.get('content', '').strip()
        if not content:
            return
        
        stream_info = active_streams[session_id]
        
        # Créer le message gRPC
        message = chat_pb2.ChatMessage(
            room_id=stream_info['room_id'],
            user_id=stream_info['user_info']['user_id'],
            username=stream_info['user_info']['username'],
            content=content,
            timestamp=int(time.time()),
            type=chat_pb2.MessageType.TEXT
        )
        

        stream_info['message_queue'].put(message)
        print(f"📤 Message ajouté à la queue de {stream_info['user_info']['username']}: {content[:50]}")
    
    @socketio.on('leave_chat')
    def handle_leave_chat():
        """Quitter le chat et arrêter le streaming"""
        session_id = request.sid
        
        if session_id not in active_streams:
            emit('error', {'message': 'Vous n\'êtes pas dans un chat'})
            return
        
        stream_info = active_streams[session_id]
        room_id = stream_info['room_id']
        
        print(f"📤 {stream_info['user_info']['username']} quitte room {room_id}")
        
        # Quitter la room gRPC
        try:
            leave_request = chat_pb2.LeaveRoomRequest(
                room_id=room_id,
                user_id=stream_info['user_info']['user_id']
            )
            chat_stub.LeaveRoom(leave_request, metadata=metadata)
        except:
            pass
        
        # Arrêter le stream
        stream_info['running'] = False
        stream_info['message_queue'].put(STOP)
        
        # ✅ QUITTER LA ROOM SOCKETIO
        leave_room(room_id)
        print(f"✅ Session {session_id} a quitté la room SocketIO {room_id}")
        
        # Nettoyer
        del active_streams[session_id]
        
        emit('left_chat', {'status': 'ok'})

def start_grpc_stream(session_id, room_id, user_info):
    """
    Démarrer le streaming bidirectionnel gRPC pour un utilisateur dans une room.
    """
    # Créer UNE SEULE queue
    message_queue = Queue()
    
    stream_info = {
        'running': True,
        'room_id': room_id,
        'user_info': user_info,
        'message_queue': message_queue
    }
    active_streams[session_id] = stream_info 

    def message_generator():
        """Générateur de messages pour le stream gRPC"""
        # Message JOIN initial
        yield chat_pb2.ChatMessage(
            room_id=room_id,
            user_id=user_info['user_id'],
            username=user_info['username'],
            type=chat_pb2.JOIN,
            timestamp=int(time.time())
        )
        
        # Boucle des messages
        while stream_info['running']:
            try:
                message = message_queue.get(timeout=0.5)
                if message is STOP:
                    return
                print(f"📨 Envoi message vers gRPC: {message.content[:50]}")
                yield message
            except Empty: 
                continue
            
    # Thread de réception (messages entrants)
    def receive_messages():
        try:
            print(f"🚀 Démarrage du stream gRPC pour {user_info['username']}")
            response_iterator = chat_stub.StreamMessages(
                message_generator(),
                metadata=metadata
            )

            for message in response_iterator:
                if not stream_info['running']:
                    break

                # Type lisible
                message_type = ['TEXT', 'SYSTEM', 'JOIN', 'LEAVE'][message.type]

                message_data = {
                    'id': message.id,
                    'room_id': message.room_id,
                    'user_id': message.user_id,
                    'username': message.username,
                    'content': message.content,
                    'timestamp': message.timestamp,
                    'type': message_type
                }

                # ✅✅✅ SOLUTION FINALE : Émettre à la room SocketIO ✅✅✅
                print(f"📡 Émission vers room SocketIO: {room_id}")
                socketio.emit(
                    'new_message',
                    message_data,
                    room=room_id
                )

                print(f"📩 Message émis à room {room_id}: [{message_type}] {message.username}: {message.content[:50]}")

        except grpc.RpcError as e:
            print(f"❌ Erreur gRPC stream: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"❌ Erreur stream: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Nettoyage du stream
            stream_info['running'] = False
            if session_id in active_streams:
                del active_streams[session_id]
            print(f"🛑 Stream gRPC fermé pour {user_info['username']}")

    # Démarrer le thread de réception
    thread = threading.Thread(target=receive_messages, daemon=True)
    thread.start()
    stream_info['thread'] = thread

    print(f"✅ Stream bidirectionnel démarré pour {user_info['username']} dans room {room_id}")