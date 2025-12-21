from dataclasses import dataclass
from typing import List
import time
import uuid

@dataclass
class Message:
    """Modèle d'un message de chat"""
    id: str
    room_id: str
    user_id: str
    username: str
    content: str
    timestamp: int
    message_type: int = 0  # 0=TEXT, 1=SYSTEM, 2=JOIN, 3=LEAVE

class MessageStore:
    """Stockage en mémoire des messages"""
    
    def __init__(self, max_history=1000):
        self.messages = {}  # {room_id: [Message]}
        self.max_history = max_history
    
    def add_message(self, room_id: str, user_id: str, username: str, 
                   content: str, message_type: int = 0) -> Message:
        """Ajouter un message"""
        message = Message(
            id=str(uuid.uuid4()),
            room_id=room_id,
            user_id=user_id,
            username=username,
            content=content,
            timestamp=int(time.time()),
            message_type=message_type
        )
        
        if room_id not in self.messages:
            self.messages[room_id] = []
        
        self.messages[room_id].append(message)
        
        # Limiter l'historique
        if len(self.messages[room_id]) > self.max_history:
            self.messages[room_id] = self.messages[room_id][-self.max_history:]
        
        return message
    
    def get_room_history(self, room_id: str, limit: int = 100) -> List[Message]:
        """Récupérer l'historique d'une room"""
        messages = self.messages.get(room_id, [])
        return messages[-limit:] if limit > 0 else messages
    
    def clear_room_history(self, room_id: str):
        """Effacer l'historique d'une room"""
        if room_id in self.messages:
            self.messages[room_id] = []