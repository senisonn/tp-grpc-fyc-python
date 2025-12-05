"""Example 10: Decorator for Error Handling"""
from functools import wraps
import grpc, logging

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Decorator to handle gRPC errors uniformly"""
    @wraps(func)
    def wrapper(self, request, context, *args, **kwargs):
        try:
            return func(self, request, context, *args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except KeyError as e:
            logger.warning(f"Not found: {e}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Resource not found: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    return wrapper

class UserService(user_pb2_grpc.UserServiceServicer):
    @handle_errors
    def CreateUser(self, request, context):
        if not request.email:
            raise ValueError("email is required")
        # Implementation...
        return user_pb2.User(...)
    
    @handle_errors
    def GetUser(self, request, context):
        if request.user_id not in self.users:
            raise KeyError(request.user_id)
        return self.users[request.user_id]
