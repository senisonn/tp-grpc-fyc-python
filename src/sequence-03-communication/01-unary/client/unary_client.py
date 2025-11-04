from __future__ import annotations


import grpc

import proto.unary_pb2 as pb2
import proto.unary_pb2_grpc as pb2_grpc


class UnaryClient:
    """Client for calling the Unary gRPC service."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
    ) -> None:
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def get_server_response(self, message: str) -> pb2.MessageResponse:
        """Make a unary RPC call to the server."""
        request = pb2.Message(message=message)
        print(f"📨 Sending request: {request}")
        return self.stub.GetServerResponse(request)


if __name__ == "__main__":
    client = UnaryClient()
    response = client.get_server_response("Hello Server, you there?")
    print(f"✅ Server Response:\n{response}")
