import grpc
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../proto'))

import chat_pb2
import chat_pb2_grpc
from src.config import config

class ChatClient:
    """Client gRPC pour le Chat Service"""
    
    def __init__(self):
        self.channel = grpc.insecure_channel(
            f'{config.CHAT_SERVICE_HOST}:{config.CHAT_SERVICE_PORT}'
        )
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.metadata = [('x-api-key', config.CHAT_API_KEY)]
    
    def create_room(self, name: str, description: str, created_by: str):
        """Créer une room"""
        request = chat_pb2.CreateRoomRequest(
            name=name,
            description=description,
            created_by=created_by
        )
        response = self.stub.CreateRoom(request, metadata=self.metadata)
        return {
            'id': response.id,
            'name': response.name,
            'description': response.description,
            'created_by': response.created_by,
            'created_at': response.created_at,
            'member_count': response.member_count
        }
    
    def list_rooms(self, page: int = 1, limit: int = 10):
        """Lister les rooms"""
        request = chat_pb2.ListRoomsRequest(page=page, limit=limit)
        response = self.stub.ListRooms(request, metadata=self.metadata)
        return {
            'rooms': [
                {
                    'id': r.id,
                    'name': r.name,
                    'description': r.description,
                    'created_by': r.created_by,
                    'member_count': r.member_count
                }
                for r in response.rooms
            ],
            'total': response.total
        }
    
    def join_room(self, room_id: str, user_id: str, username: str):
        """Rejoindre une room"""
        request = chat_pb2.JoinRoomRequest(
            room_id=room_id,
            user_id=user_id,
            username=username
        )
        response = self.stub.JoinRoom(request, metadata=self.metadata)
        return {
            'success': response.success,
            'message': response.message
        }
    
    def leave_room(self, room_id: str, user_id: str):
        """Quitter une room"""
        request = chat_pb2.LeaveRoomRequest(
            room_id=room_id,
            user_id=user_id
        )
        response = self.stub.LeaveRoom(request, metadata=self.metadata)
        return {
            'success': response.success,
            'message': response.message
        }