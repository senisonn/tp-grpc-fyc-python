"""Example 4: Logging Interceptor"""
import grpc, logging, time

class LoggingInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        self.logger.info(f"📥 Request: {method}")
        
        start = time.time()
        handler = continuation(handler_call_details)
        
        if handler and handler.unary_unary:
            original = handler.unary_unary
            def wrapper(request, context):
                response = original(request, context)
                duration = time.time() - start
                self.logger.info(f"✅ Completed in {duration:.3f}s")
                return response
            
            return grpc.unary_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )
        return handler

# Usage:
# server = grpc.server(
#     futures.ThreadPoolExecutor(max_workers=10),
#     interceptors=[LoggingInterceptor()]
# )
