"""Example 2: Input Validation"""
import grpc, re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")

class UserServiceWithValidation(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        if not request.name:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "name is required")
        if not request.email:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "email is required")
        
        try:
            validate_email(request.email)
        except ValueError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        
        return user_pb2.User(id="123", name=request.name, email=request.email)
