import grpc
from concurrent import futures
import time
import proto.server_streaming_pb2 as server_streaming_pb2
import proto.server_streaming_pb2_grpc as server_streaming_pb2_grpc


class ServerStreamingService(server_streaming_pb2_grpc.ServerStreamingServicer):
    """Implementation of Server Streaming service"""

    def GetServerResponse(self, request, context):
        """
        Receives a single request and yields multiple responses as a stream
        """
        message = request.message
        print(f"Server received: {message}")
        
        # Send multiple responses back to client
        for i in range(1, 6):
            response = server_streaming_pb2.MessageResponse(
                message=f"Response {i}: Processing '{message}'",
                sequence=i
            )
            print(f"Sending response {i}")
            yield response
            time.sleep(1)  # Simulate processing time


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_streaming_pb2_grpc.add_ServerStreamingServicer_to_server(
        ServerStreamingService(), server
    )
    server.add_insecure_port('[::]:50052')
    print("Server Streaming Server started on port 50052...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
