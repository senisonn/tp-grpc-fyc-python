import grpc
from concurrent import futures
import proto.bidirectional_pb2 as bidirectional_pb2
import proto.bidirectional_pb2_grpc as bidirectional_pb2_grpc


class BidirectionalService(bidirectional_pb2_grpc.BidirectionalServicer):
    """Implementation of Bidirectional Streaming service"""

    def GetServerResponse(self, request_iterator, context):
        """
        Receives a stream of messages and yields a stream of responses
        Both streams operate independently
        """
        for message in request_iterator:
            print(f"Server received: {message.message}")
            
            # Echo back the message with server prefix
            response = bidirectional_pb2.Message(
                message=f"Server echo: {message.message}"
            )
            
            print(f"Server sending: {response.message}")
            yield response


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bidirectional_pb2_grpc.add_BidirectionalServicer_to_server(
        BidirectionalService(), server
    )
    server.add_insecure_port('[::]:50054')
    print("Bidirectional Streaming Server started on port 50054...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
