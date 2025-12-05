import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server
    HOST = os.getenv('SERVER_HOST', '[::]')
    PORT = os.getenv('SERVER_PORT', '50051')
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'grpc_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @classmethod
    def get_server_address(cls):
        return f"{cls.HOST}:{cls.PORT}"
    
    @classmethod
    def get_db_url(cls):
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

settings = Settings()
