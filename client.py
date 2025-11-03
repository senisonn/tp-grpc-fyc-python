import grpc
import client_pb2
import client_pb2_grpc

def get_client(client_id):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = client_pb2_grpc.ClientServiceStub(channel)
        request = client_pb2.ClientRequest(id=client_id)
        response = stub.GetClient(request)
        if response.error:
            print(f"Erreur: {response.error}")
        else:
            print(f"Client récupéré: {response.client.nom} ({response.client.email})")

if __name__ == '__main__':
    get_client(1)  # Exemple avec ID = 1
