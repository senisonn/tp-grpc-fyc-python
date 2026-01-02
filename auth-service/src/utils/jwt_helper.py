import jwt
import time
from src.config import config

class JWTHelper:
    """Helper pour gérer les JWT"""
    
    @staticmethod
    def generate_token(user_id: str, username: str) -> str:
        """Générer un token JWT"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': int(time.time()) + config.JWT_EXPIRATION,
            'iat': int(time.time())
        }
        
        token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Décoder et valider un token JWT"""
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expiré")
        except jwt.InvalidTokenError:
            raise ValueError("Token invalide")