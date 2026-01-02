import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    SECRET_KEY = os.getenv('SECRET_KEY', 'gateway-secret-key-change-me')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
    JWT_ALGORITHM = 'HS256'
    
    # Services
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:5001')
    CHAT_SERVICE_HOST = os.getenv('CHAT_SERVICE_HOST', 'chat-service')
    CHAT_SERVICE_PORT = int(os.getenv('CHAT_SERVICE_PORT', 50052))
    CHAT_API_KEY = os.getenv('CHAT_API_KEY', 'chat-service-api-key-456')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

config = Config()