import requests
from src.config import config

class AuthClient:
    """Client pour communiquer avec l'Auth Service"""
    
    @staticmethod
    def validate_token(token: str) -> dict:
        """Valider un token via l'Auth Service"""
        try:
            response = requests.post(
                f"{config.AUTH_SERVICE_URL}/auth/validate",
                json={'token': token},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'valid': False, 'error': 'Invalid token'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}