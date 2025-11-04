import grpc
from concurrent import futures
import proto.client_streaming_pb2 as client_streaming_pb2
import proto.client_streaming_pb2_grpc as client_streaming_pb2_grpc


class ClientStreamingService(client_streaming_pb2_grpc.ClientStreamingServicer):
    """Implementation of Client Streaming service"""

    def GetServerResponse(self, request_iterator, context):
        """
        Receives a stream of messages from client and returns a single response
        """
        messages = []
        
        # Read all messages from the stream
        for message in request_iterator:
            print(f"Server received: {message.message}")
            messages.append(message.message)
        
        # Send single response after receiving all messages
        count = len(messages)
        result = f"Server processed {count} messages: {', '.join(messages)}"
        
        return client_streaming_pb2.MessageResponse(
            message=result,
            messages_received=count
        )


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    client_streaming_pb2_grpc.add_ClientStreamingServicer_to_server(
        ClientStreamingService(), server
    )
    server.add_insecure_port('[::]:50053')
    print("Client Streaming Server started on port 50053...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
