from typing import Dict, Set
import threading

class RoomManager:
    """Gestionnaire des connexions actives par room"""
    
    def __init__(self):
        self.active_streams = {}  # {room_id: {user_id: queue}}
        self.lock = threading.Lock()
    
    def add_stream(self, room_id: str, user_id: str, queue):
        """Ajouter un stream actif pour une room"""
        with self.lock:
            if room_id not in self.active_streams:
                self.active_streams[room_id] = {}
            self.active_streams[room_id][user_id] = queue
    
    def remove_stream(self, room_id: str, user_id: str):
        """Retirer un stream actif"""
        with self.lock:
            if room_id in self.active_streams:
                if user_id in self.active_streams[room_id]:
                    del self.active_streams[room_id][user_id]
                
                # Nettoyer la room si vide
                if not self.active_streams[room_id]:
                    del self.active_streams[room_id]
    
    def broadcast_to_room(self, room_id: str, message):
        """Diffuser un message à tous les membres actifs d'une room"""
        with self.lock:
            if room_id in self.active_streams:
                for queue in self.active_streams[room_id].values():
                    try:
                        queue.put(message)
                    except:
                        pass
    
    def get_active_users(self, room_id: str) -> Set[str]:
        """Obtenir les utilisateurs actifs dans une room"""
        with self.lock:
            if room_id in self.active_streams:
                return set(self.active_streams[room_id].keys())
            return set()