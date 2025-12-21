import grpc
from proto import logging_pb2, logging_pb2_grpc
from src.config import config
import uuid
import time

class LoggingClient:
    """Client gRPC pour envoyer des logs au service de logging"""
    
    def __init__(self):
        self.host = config.LOGGING_SERVICE_HOST
        self.port = config.LOGGING_SERVICE_PORT
        self.api_key = config.LOGGING_API_KEY
        self.channel = None
        self.stub = None
        self._connect()
    
    def _connect(self):
        """Établir la connexion avec le service de logging"""
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            self.stub = logging_pb2_grpc.LoggingServiceStub(self.channel)
            print(f"✅ Connecté au Logging Service: {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Erreur de connexion au Logging Service: {str(e)}")
    
    def log(self, level, message, metadata=None, trace_id=None):
        """
        Envoyer un log au service de logging
        
        Args:
            level: Niveau de log (INFO, WARNING, ERROR, etc.)
            message: Message du log
            metadata: Dictionnaire de métadonnées optionnelles
            trace_id: ID de trace pour le suivi
        """
        try:
            log_entry = logging_pb2.LogEntry(
                id=str(uuid.uuid4()),
                service_name=config.SERVICE_NAME,
                level=self._get_level_value(level),
                message=message,
                timestamp=int(time.time()),
                metadata=metadata or {},
                trace_id=trace_id or str(uuid.uuid4())
            )
            
            # Créer les metadata avec l'API key
            metadata_list = [('x-api-key', self.api_key)]
            
            # Envoyer le log via streaming
            def log_generator():
                yield log_entry
            
            response = self.stub.StreamLogs(log_generator(), metadata=metadata_list)
            return response.success
        
        except grpc.RpcError as e:
            print(f"❌ Erreur gRPC lors de l'envoi du log: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du log: {str(e)}")
            return False
    
    def info(self, message, **kwargs):
        """Log de niveau INFO"""
        return self.log('INFO', message, kwargs)
    
    def warning(self, message, **kwargs):
        """Log de niveau WARNING"""
        return self.log('WARNING', message, kwargs)
    
    def error(self, message, **kwargs):
        """Log de niveau ERROR"""
        return self.log('ERROR', message, kwargs)
    
    def debug(self, message, **kwargs):
        """Log de niveau DEBUG"""
        return self.log('DEBUG', message, kwargs)
    
    def critical(self, message, **kwargs):
        """Log de niveau CRITICAL"""
        return self.log('CRITICAL', message, kwargs)
    
    def _get_level_value(self, level_name):
        """Convertir le nom du niveau en valeur"""
        levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
        return levels.get(level_name.upper(), 1)
    
    def close(self):
        """Fermer la connexion"""
        if self.channel:
            self.channel.close()