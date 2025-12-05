"""Example 3: Error Handling with Custom Errors"""
import grpc

class NotFoundError(Exception):
    pass

class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.users = {}
    
    def GetUser(self, request, context):
        try:
            if request.user_id not in self.users:
                raise NotFoundError(f"User {request.user_id} not found")
            return self.users[request.user_id]
        except NotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, "Internal error")
