import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Service
    SERVICE_PORT = int(os.getenv('SERVICE_PORT', 50051))
    SERVICE_NAME = 'auth-service'
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))  # 1 heure
    REFRESH_TOKEN_EXPIRATION = 604800  # 7 jours
    
    # API Key
    API_KEY = os.getenv('API_KEY', 'auth-service-api-key')
    
    # Database (pour la production)
    # DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://...')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

config = Config()