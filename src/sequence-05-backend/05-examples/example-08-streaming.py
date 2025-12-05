"""Example 8: Server Streaming"""
import grpc, time

class UserService(user_pb2_grpc.UserServiceServicer):
    def StreamUsers(self, request, context):
        """Server streaming - send users one by one"""
        users = [
            user_pb2.User(id="1", name="User 1", email="user1@example.com"),
            user_pb2.User(id="2", name="User 2", email="user2@example.com"),
            user_pb2.User(id="3", name="User 3", email="user3@example.com"),
        ]
        
        for user in users:
            if context.is_active():
                yield user
                time.sleep(0.5)  # Simulate delay
            else:
                return

# Client side:
# stub = user_pb2_grpc.UserServiceStub(channel)
# for user in stub.StreamUsers(request):
#     print(f"Received: {user.name}")
