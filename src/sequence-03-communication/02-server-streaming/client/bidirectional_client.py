from __future__ import print_function

import grpc
import proto.bidirectional_pb2_grpc as bidirectional_pb2_grpc
import proto.bidirectional_pb2 as bidirectional_pb2


def make_message(message):
    return bidirectional_pb2.Message(
        message=message
    )


def generate_messages():
    messages = [
        make_message("First message"),
        make_message("Second message"),
        make_message("Third message"),
        make_message("Fourth message"),
        make_message("Fifth message"),
    ]
    for msg in messages:
        print(f"Hello Server Sending you the {msg.message}")
        yield msg


def send_message(stub):
    responses = stub.GetServerResponse(generate_messages())
    for response in responses:
        print(f"Hello from the server received your {response.message}")


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
        send_message(stub)


if __name__ == '__main__':
    run()