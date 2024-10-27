from __future__ import print_function

import grpc
import bidirectional.bidirectional_pb2_grpc as bidirectional_pb2_grpc
import bidirectional.bidirectional_pb2 as bidirectional_pb2

class Client:
    def __init__(self):
        pass

def send_message(stub,client_id):
    request = bidirectional_pb2.ClientRequest(id=client_id)
    response = stub.client_init(request)
    print("The ID of the client is %s" % response.message)


def RPC_init(int):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bidirectional_pb2_grpc.LockServiceStub(channel)
        send_message(stub) #function to be made by us


if __name__ == '__main__':
    RPC_init(1)
    
    def RPC_lock_acquire():
        pass
    def RPC_lock_release():
        pass
    def append_file():
        pass
    def RPC_close():
        pass


#User prompt for file name and what to append
