import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    SECRET_KEY = os.getenv('SECRET_KEY', 'auth-secret-key-change-me')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-key')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))
    
    # Service
    SERVICE_NAME = 'auth-service'
    
    # Logging Service configuration
    LOGGING_SERVICE_HOST = os.getenv('LOGGING_SERVICE_HOST', 'localhost')
    LOGGING_SERVICE_PORT = int(os.getenv('LOGGING_SERVICE_PORT', 50053))
    LOGGING_API_KEY = os.getenv('LOGGING_API_KEY', 'logging-service-api-key-123')

config = Config()
