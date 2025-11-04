from __future__ import annotations

from concurrent import futures

import grpc

import proto.unary_pb2 as pb2
import proto.unary_pb2_grpc as pb2_grpc

class UnaryService(pb2_grpc.UnaryServicer):
    """Implementation of the Unary gRPC service."""

    def GetServerResponse(
        self,
        request: pb2.Message,
        _context: grpc.ServicerContext,
    ) -> pb2.MessageResponse:
        message: str = request.message

        response_message = (
            f'Hello, I am up and running. Received "{message}" message from you.'
        )

        return pb2.MessageResponse(
            message=response_message,
            received=True,
        )


def serve() -> None:
    """Run the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)

    server.add_insecure_port("[::]:50051")
    server.start()
    print("✅ Unary gRPC server is running on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
