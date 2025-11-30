import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Service
    SERVICE_PORT = int(os.getenv('SERVICE_PORT', 50052))
    SERVICE_NAME = 'chat-service'
    
    # API Key
    API_KEY = os.getenv('API_KEY', 'chat-service-api-key')
    
    # Logging Service
    LOGGING_SERVICE_HOST = os.getenv('LOGGING_SERVICE_HOST', 'localhost')
    LOGGING_SERVICE_PORT = int(os.getenv('LOGGING_SERVICE_PORT', 50053))
    LOGGING_API_KEY = os.getenv('LOGGING_API_KEY', 'logging-service-api-key')
    
    # Chat Configuration
    MAX_ROOM_MEMBERS = int(os.getenv('MAX_ROOM_MEMBERS', 100))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 1000))
    MESSAGE_HISTORY_LIMIT = int(os.getenv('MESSAGE_HISTORY_LIMIT', 100))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

config = Config()