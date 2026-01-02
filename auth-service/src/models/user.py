import bcrypt
import uuid
from typing import Optional, Dict

class User:
    """Modèle utilisateur"""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
    
    def check_password(self, password: str) -> bool:
        """Vérifier le mot de passe"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self) -> dict:
        """Convertir en dictionnaire"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email
        }

class UserStore:
    """Stockage en mémoire des utilisateurs"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.usernames: Dict[str, str] = {}  # username -> user_id
        
        # Créer un utilisateur de test
        self.create_user("admin", "admin@test.com", "admin123")
        self.create_user("alice", "alice@test.com", "alice123")
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Créer un utilisateur"""
        if username in self.usernames:
            return None
        
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(user_id, username, email, password_hash)
        self.users[user_id] = user
        self.usernames[username] = user_id
        
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupérer un utilisateur par son username"""
        user_id = self.usernames.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Récupérer un utilisateur par son ID"""
        return self.users.get(user_id)
