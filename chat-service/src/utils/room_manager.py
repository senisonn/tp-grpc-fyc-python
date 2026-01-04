from typing import Dict, Set
import threading

class RoomManager:
    """Gestionnaire des connexions actives par room"""
    
    def __init__(self):
        self.active_streams = {}  # {room_id: {user_id: queue}}
        self.lock = threading.Lock()
        print("✅ RoomManager initialisé")
    
    def add_stream(self, room_id: str, user_id: str, queue):
        """Ajouter un stream actif pour une room"""
        with self.lock:
            if room_id not in self.active_streams:
                self.active_streams[room_id] = {}
                print(f"📁 Nouvelle room créée dans RoomManager: {room_id}")
            
            self.active_streams[room_id][user_id] = queue
            print(f"➕ Stream ajouté: room={room_id}, user={user_id}")
            print(f"   👥 Total streams dans room {room_id}: {len(self.active_streams[room_id])}")
    
    def remove_stream(self, room_id: str, user_id: str):
        """Retirer un stream actif"""
        with self.lock:
            if room_id in self.active_streams:
                if user_id in self.active_streams[room_id]:
                    del self.active_streams[room_id][user_id]
                    print(f"➖ Stream retiré: room={room_id}, user={user_id}")
                    print(f"   👥 Streams restants dans room {room_id}: {len(self.active_streams[room_id])}")
                
                # Nettoyer la room si vide
                if not self.active_streams[room_id]:
                    del self.active_streams[room_id]
                    print(f"🗑️ Room supprimée (vide): {room_id}")
    
    def broadcast_to_room(self, room_id: str, message):
        """Diffuser un message à tous les membres actifs d'une room"""
        with self.lock:
            if room_id not in self.active_streams:
                print(f"⚠️ Broadcast impossible: room {room_id} non trouvée dans active_streams")
                print(f"   Rooms disponibles: {list(self.active_streams.keys())}")
                return
            
            streams = self.active_streams[room_id]
            print(f"📣 Broadcasting à {len(streams)} stream(s) dans room {room_id}")
            
            success_count = 0
            for uid, msg_queue in streams.items():
                try:
                    msg_queue.put(message)
                    success_count += 1
                    print(f"   ✅ Message envoyé à user {uid}")
                except Exception as e:
                    print(f"   ❌ Erreur envoi à user {uid}: {str(e)}")
            
            print(f"📊 Broadcast terminé: {success_count}/{len(streams)} succès")
    
    def get_active_users(self, room_id: str) -> Set[str]:
        """Obtenir les utilisateurs actifs dans une room"""
        with self.lock:
            if room_id in self.active_streams:
                users = set(self.active_streams[room_id].keys())
                print(f"👥 Utilisateurs actifs dans room {room_id}: {users}")
                return users
            print(f"⚠️ Room {room_id} non trouvée (pas d'utilisateurs actifs)")
            return set()
    
    def debug_state(self):
        """Afficher l'état actuel du RoomManager (pour debug)"""
        with self.lock:
            print("\n" + "="*60)
            print("🔍 DEBUG RoomManager State")
            print("="*60)
            for room_id, streams in self.active_streams.items():
                print(f"Room: {room_id}")
                for user_id in streams.keys():
                    print(f"  └─ User: {user_id}")
            if not self.active_streams:
                print("(Aucune room active)")
            print("="*60 + "\n")