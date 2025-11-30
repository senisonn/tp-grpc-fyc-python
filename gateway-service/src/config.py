import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Service
    SERVICE_PORT = int(os.getenv('GATEWAY_PORT', 50050))
    SERVICE_NAME = 'gateway-service'
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
    JWT_ALGORITHM = 'HS256'
    
    # Services endpoints
    AUTH_SERVICE_HOST = os.getenv('AUTH_SERVICE_HOST', 'localhost')
    AUTH_SERVICE_PORT = int(os.getenv('AUTH_SERVICE_PORT', 50051))
    
    CHAT_SERVICE_HOST = os.getenv('CHAT_SERVICE_HOST', 'localhost')
    CHAT_SERVICE_PORT = int(os.getenv('CHAT_SERVICE_PORT', 50052))
    
    LOGGING_SERVICE_HOST = os.getenv('LOGGING_SERVICE_HOST', 'localhost')
    LOGGING_SERVICE_PORT = int(os.getenv('LOGGING_SERVICE_PORT', 50053))
    
    # API Keys for inter-service communication
    AUTH_API_KEY = os.getenv('AUTH_API_KEY', 'auth-service-api-key')
    CHAT_API_KEY = os.getenv('CHAT_API_KEY', 'chat-service-api-key')
    LOGGING_API_KEY = os.getenv('LOGGING_API_KEY', 'logging-service-api-key')
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # secondes
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

config = Config()