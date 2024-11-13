from Proto import lock_pb2
from Proto import lock_pb2_grpc
import grpc
import time
import threading

SWITCH_SERVER_TIMEOUT = 25
MAXIMUM_RETRIES = 60

class Client:
    def __init__(self):
        self.client_id = None
        self.request_counter = 0
        self.stop_heartbeat = False
        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = lock_pb2_grpc.LockServiceStub(self.channel)
        except grpc.RpcError:
            print(f"Server is not available on localhost: 50051, switching to different server")
            self.switch_server(self)


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
        timeout=5
        request_id = self.generate_request_id()
        # Start the heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeats, daemon=True)
        self.heartbeat_thread.start()
        while True:
            try:
                response = self.stub.lock_acquire(lock_pb2.lock_args(
                    client_id=self.client_id,
                    request_id=request_id
                ))
                timeout = 5
                retry_interval = 5
                if response.status == lock_pb2.Status.SUCCESS:
                    print(f"Lock has been acquired by client: {self.client_id}")
                    break
                else:
                    print(f"Client {self.client_id} is waiting in queue.")
                    time.sleep(retry_interval)
                

            except grpc.RpcError:
                print(f"Server is unavailable. Retrying in {retry_interval} seconds...")
                if timeout >= SWITCH_SERVER_TIMEOUT:
                    print(f"Maximum retries reached, switching to different server")
                    self.switch_server()
                    continue
                time.sleep(retry_interval)
                timeout +=5
                retry_interval = min(retry_interval + 2, 20)

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
                    break  
                else:
                    print(f"Lock cannot be released by client: {self.client_id} as it doesn't hold the lock")
                    break  # Exit if lock release failed for other reasons

            except grpc.RpcError:
                print(f"Error releasing lock: Server may be unavailable. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retry_interval = min(retry_interval + 2, 20)  # Exponential backoff with a max wait time

    def send_heartbeats(self):
        while not self.stop_heartbeat:
            try:
                time.sleep(5)  # Send heartbeat every 5 seconds
                self.stub.heartbeat(lock_pb2.Heartbeat(client_id=self.client_id))
            except grpc.RpcError:
                print("Failed to send heartbeat: Server may be unavailable.")
                break

    def switch_server(self):
        #trying to connect to one of the backup sever
        servers = ['localhost: 50052','localhost: 50053','localhost: 50054','localhost: 50051']
        retries = 0
        flag = True
        while True:
            if retries >= MAXIMUM_RETRIES:
                print(f"No server is available")
            for server in servers:
                try:
                    self.channel = grpc.insecure_channel(server)
                    self.stub = lock_pb2_grpc.LockServiceStub(self.channel)
                    flag = False
                    break
                except grpc.RpcError:
                    print(f"Unable to connect to server at {server}, trying next server")
            if flag:
                retries=retries+4
                print("No server available, trying again")
                continue
            print(f"Connection successful with new server")
            break


    def append_file(self, filename, content):
        pass

    def RPC_close(self):
        pass

if __name__ == '__main__':
    client = Client()
    client.RPC_init()
    client.RPC_lock_acquire()
    time.sleep(50)
    client.RPC_lock_release()
