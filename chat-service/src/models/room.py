from dataclasses import dataclass, field
from typing import List, Set
import time
import uuid

@dataclass
class Room:
    """Modèle d'une room de chat"""
    id: str
    name: str
    description: str
    created_by: str
    created_at: int
    members: Set[str] = field(default_factory=set)
    
    def add_member(self, user_id: str) -> bool:
        """Ajouter un membre à la room"""
        if user_id not in self.members:
            self.members.add(user_id)
            return True
        return False
    
    def remove_member(self, user_id: str) -> bool:
        """Retirer un membre de la room"""
        if user_id in self.members:
            self.members.remove(user_id)
            return True
        return False
    
    def has_member(self, user_id: str) -> bool:
        """Vérifier si un utilisateur est membre"""
        return user_id in self.members
    
    def get_member_count(self) -> int:
        """Obtenir le nombre de membres"""
        return len(self.members)
    
class RoomStore:
    """Stockage en mémoire des rooms"""
    
    def __init__(self):
        self.rooms = {}
    
    def create_room(self, name: str, description: str, created_by: str) -> Room:
        """Créer une nouvelle room"""
        room = Room(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_by=created_by,
            created_at=int(time.time())
        )
        self.rooms[room.id] = room
        return room
    
    def get_room(self, room_id: str) -> Room:
        """Récupérer une room par son ID"""
        return self.rooms.get(room_id)
    
    def list_rooms(self) -> List[Room]:
        """Lister toutes les rooms"""
        return list(self.rooms.values())
    
    def delete_room(self, room_id: str) -> bool:
        """Supprimer une room"""
        if room_id in self.rooms:
            del self.rooms[room_id]
            return True
        return False
