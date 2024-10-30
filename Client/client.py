from Proto import lock_pb2
from Proto import lock_pb2_grpc
import grpc
import time

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

    def RPC_lock_acquire(self):
        while True:
            response = self.stub.lock_acquire(lock_pb2.lock_args(client_id=self.client_id))
            
            if response.status == lock_pb2.Status.SUCCESS:
                print(f"Lock has been acquired by client: {self.client_id}")
                break 
            else:
                print(f"Lock currently held by another client. Client {self.client_id} is waiting in queue.")
                time.sleep(2)  # Small delay before re-checking
    
    def RPC_lock_release(self):
        response = self.stub.lock_release(lock_pb2.lock_args(client_id=self.client_id))
        if response.status == lock_pb2.Status.SUCCESS:
            print(f"Lock has been released by client: {self.client_id}")
        else:
            print(f"Lock cannot be released by client: {self.client_id} as it doesn't hold the lock")
    
    def append_file(self):
        pass
    
    def RPC_close(self):
        pass

if __name__ == '__main__':
    client = Client()
    client.RPC_init()
    client.RPC_lock_acquire()
    
    # TO DO Append file task
    time.sleep(15)  
    
    client.RPC_lock_release()
