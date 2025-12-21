import grpc
from src.config import config

class APIKeyInterceptor(grpc.ServerInterceptor):
    """Intercepteur pour valider l'API Key des requêtes entrantes"""
    
    def __init__(self, valid_api_key):
        self.valid_api_key = valid_api_key
    
    def intercept_service(self, continuation, handler_call_details):
        """Vérifie l'API key dans les metadata"""
        metadata = dict(handler_call_details.invocation_metadata)
        
        # Récupérer l'API key depuis les metadata
        api_key = metadata.get('x-api-key', '')
        
        if api_key != self.valid_api_key:
            def abort(request, context):
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    'Invalid API Key'
                )
            return grpc.unary_unary_rpc_method_handler(abort)
        
        return continuation(handler_call_details)