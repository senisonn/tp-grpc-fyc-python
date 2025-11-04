import grpc
import proto.server_streaming_pb2 as server_streaming_pb2
import proto.server_streaming_pb2_grpc as server_streaming_pb2_grpc


class ServerStreamingClient:
    """Client for Server Streaming gRPC"""

    def __init__(self):
        self.host = 'localhost'
        self.port = 50052
        
        # Create a channel
        self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        
        # Create a stub
        self.stub = server_streaming_pb2_grpc.ServerStreamingStub(self.channel)

    def get_server_response(self, message):
        """
        Send a single message and receive a stream of responses
        """
        request = server_streaming_pb2.Message(message=message)
        print(f"Sending request: {request.message}\n")
        
        # Get stream of responses
        responses = self.stub.GetServerResponse(request)
        
        print("Receiving responses:")
        for response in responses:
            print(f"  [{response.sequence}] {response.message}")


if __name__ == '__main__':
    client = ServerStreamingClient()
    client.get_server_response("Hello from Server Streaming client!")
