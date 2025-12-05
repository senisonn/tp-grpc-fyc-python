"""Example 9: gRPC Client"""
import grpc
from generated import user_pb2, user_pb2_grpc

def run_client():
    # Connect to server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        # Create user
        print("Creating user...")
        request = user_pb2.CreateUserRequest(
            name="Alice",
            email="alice@example.com",
            password="SecurePass123"
        )
        user = stub.CreateUser(request)
        print(f"Created user: {user.id}")
        
        # Get user
        print("Getting user...")
        request = user_pb2.GetUserRequest(user_id=user.id)
        user = stub.GetUser(request)
        print(f"User: {user.name} ({user.email})")
        
        # List users
        print("Listing users...")
        request = user_pb2.ListUsersRequest(page=1, page_size=10)
        response = stub.ListUsers(request)
        print(f"Found {response.total_count} users")
        for u in response.users:
            print(f"  - {u.name}")

if __name__ == '__main__':
    run_client()
