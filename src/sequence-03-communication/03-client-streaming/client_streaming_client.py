import grpc
import time
import proto.client_streaming_pb2 as client_streaming_pb2
import proto.client_streaming_pb2_grpc as client_streaming_pb2_grpc


def generate_messages():
    """Generator function to create a stream of messages"""
    messages = [
        "First message",
        "Second message",
        "Third message",
        "Fourth message",
        "Fifth message"
    ]
    
    for msg in messages:
        print(f"Sending: {msg}")
        yield client_streaming_pb2.Message(message=msg)
        time.sleep(0.5)  # Simulate time between messages


class ClientStreamingClient:
    """Client for Client Streaming gRPC"""

    def __init__(self):
        self.host = 'localhost'
        self.port = 50053
        
        # Create a channel
        self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        
        # Create a stub
        self.stub = client_streaming_pb2_grpc.ClientStreamingStub(self.channel)

    def send_messages(self):
        """
        Send a stream of messages and receive a single response
        """
        print("Sending stream of messages:\n")
        
        # Send stream and get single response
        response = self.stub.GetServerResponse(generate_messages())
        
        print(f"\nServer response:")
        print(f"  {response.message}")
        print(f"  Messages received by server: {response.messages_received}")


if __name__ == '__main__':
    client = ClientStreamingClient()
    client.send_messages()
