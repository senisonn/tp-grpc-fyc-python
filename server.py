import grpc
from concurrent import futures
import client_pb2
import client_pb2_grpc

class ClientServiceServicer(client_pb2_grpc.ClientServiceServicer):
    def GetClient(self, request, context):
        # Exemple de gestion des erreurs
        if request.id <= 0:
            return client_pb2.ClientResponse(error="ID invalide")
        # Exemple de retour d'un client
        client = client_pb2.Client(id=request.id, nom="Dupont", email="dupont@example.com")
        return client_pb2.ClientResponse(client=client, error="")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    client_pb2_grpc.add_ClientServiceServicer_to_server(ClientServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Serveur gRPC démarré sur le port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
