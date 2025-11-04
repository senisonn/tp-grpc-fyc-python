import grpc
import time
import proto.bidirectional_pb2 as bidirectional_pb2
import proto.bidirectional_pb2_grpc as bidirectional_pb2_grpc


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
        print(f"Client sending: {msg}")
        yield bidirectional_pb2.Message(message=msg)
        time.sleep(1)


class BidirectionalClient:
    """Client for Bidirectional Streaming gRPC"""

    def __init__(self):
        self.host = 'localhost'
        self.port = 50054
        
        # Create a channel
        self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        
        # Create a stub
        self.stub = bidirectional_pb2_grpc.BidirectionalStub(self.channel)

    def send_and_receive(self):
        """
        Send a stream of messages and receive a stream of responses simultaneously
        """
        print("Starting bidirectional streaming...\n")
        
        # Both sending and receiving happen simultaneously
        responses = self.stub.GetServerResponse(generate_messages())
        
        print("\nReceiving responses:")
        for response in responses:
            print(f"Client received: {response.message}")


if __name__ == '__main__':
    client = BidirectionalClient()
    client.send_and_receive()
