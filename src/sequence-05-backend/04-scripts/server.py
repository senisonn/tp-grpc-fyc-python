import grpc
from concurrent import futures
import logging
import signal
import sys

from generated import user_pb2_grpc
from services.user_service import UserService
from interceptors.logging_interceptor import LoggingInterceptor
from settings import settings

def configure_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/server.log')
        ]
    )

def serve():
    configure_logging()
    logger = logging.getLogger(__name__)
    
    # Create interceptors
    interceptors = [
        LoggingInterceptor(),
    ]
    
    # Create server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS),
        interceptors=interceptors
    )
    
    # Add services
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server
    )
    
    # Enable reflection
    from grpc_reflection.v1alpha import reflection
    SERVICE_NAMES = (
        user_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Start server
    server_address = settings.get_server_address()
    server.add_insecure_port(server_address)
    server.start()
    
    logger.info(f"🚀 Server started on {server_address}")
    logger.info(f"⚙️  Environment: {settings.ENVIRONMENT}")
    logger.info(f"📝 Log level: {settings.LOG_LEVEL}")
    logger.info("Press Ctrl+C to stop")
    
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        server.stop(grace=5)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
