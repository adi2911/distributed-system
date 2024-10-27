from Proto import lock_pb2
from Proto import lock_pb2_grpc
import grpc

class Client:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = lock_pb2_grpc.LockServiceStub(self.channel)
        
    def RPC_init(self):
        request = lock_pb2.Int(rc=1)
        response = self.stub.client_init(request)
        print("Initialized connection with server:", response)

    def RPC_lock_acquire():
        pass
    def RPC_lock_release():
        pass
    def append_file():
        pass
    def RPC_close():
        pass

if __name__ == '__main__':
    client = Client()
    client.RPC_init()
