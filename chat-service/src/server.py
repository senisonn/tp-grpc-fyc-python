import grpc
from concurrent import futures
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from proto import chat_pb2_grpc
from src.services.chat_service import ChatServiceServicer
from src.interceptors.api_key_interceptor import APIKeyInterceptor
from src.config import config

def serve():
    """Démarrer le serveur gRPC"""
    
    # Créer l'intercepteur d'API Key
    api_key_interceptor = APIKeyInterceptor(config.API_KEY)
    
    # Créer le serveur avec intercepteurs
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(api_key_interceptor,)
    )
    
    # Ajouter le service
    chat_pb2_grpc.add_ChatServiceServicer_to_server(
        ChatServiceServicer(),
        server
    )
    
    # Démarrer le serveur
    server.add_insecure_port(f'[::]:{config.SERVICE_PORT}')
    server.start()
    
    print(f"🚀 Chat Service démarré sur le port {config.SERVICE_PORT}")
    print(f"🔑 API Key requise: {config.API_KEY}")
    print(f"📡 Logging Service: {config.LOGGING_SERVICE_HOST}:{config.LOGGING_SERVICE_PORT}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        server.stop(0)

if __name__ == '__main__':
    serve()