from Proto import lock_pb2
from Proto import lock_pb2_grpc
import grpc

class Client:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = lock_pb2_grpc.LockServiceStub(self.channel)
        self.client_id = None
        
    def RPC_init(self):
        request = lock_pb2.Int()
        response = self.stub.client_init(request)
        print("Initialized connection with server:", response)
        self.client_id = response.rc
        print(f"Assigned client with id: {self.client_id}")

    def RPC_lock_acquire():
        response = self.stub.lock_acquire(lock_pb2.lock_args())
        if response.status == lock_pb2.Status.SUCCESS:
            print(f"Lock has been Acquired by clinet: {self.client_id}")
        else:
            print(f"Lock cannot be acquired by client: {self.client_id} as it is held by another client")
	
    def RPC_lock_release():
        response = self.stub.lock_release(lock_pb2.lock_args())
        if response.status == lock_pb2.Status.SUCCESS:
                print(f"Lock has been Released by client: {self.client_id}")
        else:
                print(f"Lock cannot be relased by client: {self.client_id} as it doesn't hold a lock")
	
    def append_file():
        pass
    def RPC_close():
        pass

if __name__ == '__main__':
    client = Client()
    client.RPC_init()
    client.RPC_lock_acquire()
    client.RPC_lock_release()
