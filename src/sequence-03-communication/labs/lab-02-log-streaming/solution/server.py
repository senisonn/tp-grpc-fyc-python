import grpc
from concurrent import futures
import logs_pb2
import logs_pb2_grpc
import time
from datetime import datetime
import random

class LogServiceServicer(logs_pb2_grpc.LogServiceServicer):
    def StreamLogs(self, request, context):
        # Liste de messages d'exemple
        messages = [
            "Connexion utilisateur réussie",
            "Requête API traitée",
            "Erreur de connexion à la base de données",
            "Cache mis à jour",
            "Timeout sur le service externe"
        ]
        
        services = ["api-gateway", "auth-service", "database", "cache-service"]
        
        end_time = time.time() + request.duration
        
        while time.time() < end_time:
            # Générer un log aléatoire
            log = logs_pb2.LogEntry(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                level=request.level,
                message=random.choice(messages),
                service=random.choice(services)
            )
            
            yield log 
            time.sleep(1) 

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logs_pb2_grpc.add_LogServiceServicer_to_server(LogServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("🚀 Serveur de logs démarré sur le port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()