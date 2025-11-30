import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Service
    SERVICE_PORT = int(os.getenv('SERVICE_PORT', 50053))
    SERVICE_NAME = 'logging-service'
    
    # API Key
    API_KEY = os.getenv('API_KEY', 'logging-service-api-key')
    
    # Storage
    LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', '/app/logs')
    MAX_LOG_FILE_SIZE = int(os.getenv('MAX_LOG_FILE_SIZE', 10485760))  # 10MB
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 30))
    
    # Performance
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
    FLUSH_INTERVAL = int(os.getenv('FLUSH_INTERVAL', 5))  # secondes
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

config = Config()