"""Example 1: Simple gRPC Service"""
import grpc
from concurrent import futures
from generated import user_pb2, user_pb2_grpc

class SimpleUserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_pb2.User(
            id=request.user_id,
            name="John Doe",
            email="john@example.com",
            created_at=1234567890,
            updated_at=1234567890
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(SimpleUserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server running on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
