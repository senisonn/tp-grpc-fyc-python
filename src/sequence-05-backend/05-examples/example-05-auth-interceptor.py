"""Example 5: JWT Authentication Interceptor"""
import grpc, jwt

class AuthInterceptor(grpc.ServerInterceptor):
    PUBLIC_METHODS = ['/user.UserService/Login']
    
    def __init__(self, jwt_secret):
        self.jwt_secret = jwt_secret
    
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        if method in self.PUBLIC_METHODS:
            return continuation(handler_call_details)
        
        metadata = dict(handler_call_details.invocation_metadata)
        auth_header = metadata.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            def unauthenticated(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing token")
            return grpc.unary_unary_rpc_method_handler(
                unauthenticated, lambda x: x, lambda x: x
            )
        
        token = auth_header[7:]
        try:
            jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return continuation(handler_call_details)
        except jwt.InvalidTokenError:
            def invalid(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
            return grpc.unary_unary_rpc_method_handler(
                invalid, lambda x: x, lambda x: x
            )
