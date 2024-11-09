from Proto import lock_pb2
from Proto import lock_pb2_grpc
import grpc
import time
import threading

class Client:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = lock_pb2_grpc.LockServiceStub(self.channel)
        self.client_id = None
        self.request_counter = 0
        self.stop_heartbeat = False

    def generate_request_id(self):
        self.request_counter += 1
        return f"{self.client_id}-{self.request_counter}"

    def RPC_init(self):
        request = lock_pb2.Int()
        response = self.stub.client_init(request)
        print("Initialized connection with server:", response)
        self.client_id = response.rc
        print(f"Assigned client with id: {self.client_id}")

    def RPC_lock_acquire(self):
        retry_interval = 5
        request_id = self.generate_request_id()
        while True:
            try:
                response = self.stub.lock_acquire(lock_pb2.lock_args(
                    client_id=self.client_id,
                    request_id=request_id
                ))
                if response.status == lock_pb2.Status.SUCCESS:
                    print(f"Lock has been acquired by client: {self.client_id}")

                    # Start the heartbeat thread
                    self.heartbeat_thread = threading.Thread(target=self.send_heartbeats, daemon=True)
                    self.heartbeat_thread.start()
                    return True
                    break
                elif response.status == lock_pb2.Status.DUPLICATE_ERROR:
                    print("Your request is being processed.")
                else:
                    print(f"Client {self.client_id} is waiting in queue.")
                    time.sleep(retry_interval)

            except grpc.RpcError:
                print(f"Server is unavailable. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retry_interval = min(retry_interval + 5, 30)

    def RPC_lock_release(self):
        retry_interval = 5  # Initial retry interval
        request_id = self.generate_request_id()
        while True:
            try:
                response = self.stub.lock_release(lock_pb2.lock_args(
                    client_id=self.client_id,
                    request_id=request_id
                ))
                if response.status == lock_pb2.Status.SUCCESS:
                    print(f"Lock has been released by client: {self.client_id}")
                    # Stop the heartbeat thread
                    self.stop_heartbeat = True
                    if hasattr(self, 'heartbeat_thread'):
                        self.heartbeat_thread.join()
                    break  # Exit the loop if lock release was successful
                elif response.status == lock_pb2.Status.DUPLICATE_ERROR:
                    print("Your request is being processed.")
                else:
                    print(f"Lock cannot be released by client: {self.client_id} as it doesn't hold the lock")
                    break  # Exit if lock release failed for other reasons

            except grpc.RpcError:
                print(f"Error releasing lock: Server may be unavailable. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retry_interval = min(retry_interval + 5, 30)  # Exponential backoff with a max wait time

    def send_heartbeats(self):
        while not self.stop_heartbeat:
            try:
                time.sleep(5)  # Send heartbeat every 5 seconds
                self.stub.heartbeat(lock_pb2.Heartbeat(client_id=self.client_id))
            except grpc.RpcError:
                print("Failed to send heartbeat: Server may be unavailable.")
                break

    def append_file(self, filename, content):
        retry_interval = 5  # Initial retry interval
        request_id = self.generate_request_id()
        while True:
            try:
                lock_holder_response = self.stub.getCurrent_lock_holder(lock_pb2.current_lock_holder(client_id = self.client_id))    
                if lock_holder_response.status == lock_pb2.Status.SUCCESS:
                        response=self.stub.append_file(lock_pb2.file_args(filename=filename,content=content.encode("utf-8"),client_id=self.client_id,request_id=request_id))
                        if response.status== lock_pb2.Status.SUCCESS:
                            print(f"File has been appended by client {self.client_id} ")
                        elif response.status== lock_pb2.Status.DUPLICATE_ERROR:
                            print("Your query is being processed.")
                            time.sleep(retry_interval)
                            retry_interval = min(retry_interval + 2, 30)
                        else:
                            print("Failed to append file.")
                            break
                else:
                    self.RPC_lock_acquire()
            except grpc.RpcError:
                    print(f"{grpc.RpcError}")
                    print("Failed to connect to server: Server may be unavailable.")
                    break
                    



    def RPC_close(self):
        pass

if __name__ == '__main__':
    '''client = Client()
    client.RPC_init()
    client.RPC_lock_acquire()
    time.sleep(15)
    client.RPC_lock_release()'''
    
    client = Client()
    client.RPC_init()
    is_lock_acquired = client.RPC_lock_acquire()
    time.sleep(10)
    if is_lock_acquired:
        client.append_file('file_0.txt', 'Client 2 data')
    time.sleep(50)
    


