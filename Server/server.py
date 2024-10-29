from concurrent import futures
import grpc
import threading
from collections import deque
from Proto import lock_pb2
from Proto import lock_pb2_grpc

class LockServiceServicer(lock_pb2_grpc.LockServiceServicer):
    def __init__(self):
        self.current_lock_holder = None  # Store the client ID of the current lock holder
        self.waiting_queue = deque()  # Queue for clients waiting for the lock
        self.next_client_id = 1  # ID assignment for new clients
        self.lock = threading.Lock()  # Synchronization lock

    def client_init(self, request, context):
        with self.lock: 
            client_id = self.next_client_id
            self.next_client_id += 1
            print(f"Client initialized with client_id: {client_id}")
        return lock_pb2.Int(rc=client_id)
    
    def lock_acquire(self, request, context):
        client_id = request.client_id

        with self.lock:  
            if self.current_lock_holder == client_id:
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

            if self.current_lock_holder is not None:
                if client_id not in self.waiting_queue:
                    self.waiting_queue.append(client_id)
                print(f"Client {client_id} added to waiting queue")
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)

            self.current_lock_holder = client_id
            print(f"Lock acquired by client: {client_id}")
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
        
    def lock_release(self, request, context):
        client_id = request.client_id

        with self.lock:  
            if self.current_lock_holder == client_id:
                self.current_lock_holder = None  # Release the lock
                print(f"Lock released by client: {client_id}")

                if self.waiting_queue:
                    next_client_id = self.waiting_queue.popleft()
                    self.current_lock_holder = next_client_id
                    print(f"Lock granted to next client in queue: {next_client_id}")

                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
            else:
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)
    
    def append_file(self, request, context):
        pass
    
    def close(self, request, context):
        pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  
    lock_pb2_grpc.add_LockServiceServicer_to_server(LockServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at localhost:50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
