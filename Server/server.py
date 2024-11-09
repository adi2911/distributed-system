from concurrent import futures
import grpc
import threading
from collections import deque
import time
from Proto import lock_pb2
from Proto import lock_pb2_grpc
from .utils import load_server_state, log_event, is_duplicate_request, mark_request_processed

class LockServiceServicer(lock_pb2_grpc.LockServiceServicer):
    def __init__(self):
        self.current_lock_holder = None  # Store the (client_id, version) of the current lock holder
        self.current_version = 0  # Version for each lock acquisition to handle stale releases
        self.waiting_queue = deque()  # Queue for clients waiting for the lock, storing (client_id, peer)
        self.next_client_id = 1  # ID assignment for new clients
        self.lock = threading.Lock()  # Synchronization lock
        self.heartbeat_intervals = {}  # Track the last heartbeat time for each client

        # Load server state from logs on startup
        load_server_state(self)

    def client_init(self, request, context):
        with self.lock:
            client_id = self.next_client_id
            self.next_client_id += 1
            log_event(f"Client initialized with client_id: {client_id}")
        return lock_pb2.Int(rc=client_id)
    
    def lock_acquire(self, request, context):
        client_id = request.client_id
        request_id = request.request_id
        peer = context.peer()

        with self.lock:
            if is_duplicate_request(request_id):
                if self.current_lock_holder and self.current_lock_holder[0] == client_id:
                    return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
                else:
                    return lock_pb2.Response(status=lock_pb2.Status.DUPLICATE_ERROR)


            # Record the request_id as processed
            mark_request_processed(request_id)

            if self.current_lock_holder and self.current_lock_holder[0] == client_id:
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

            if self.current_lock_holder is not None:
                if (client_id, peer) not in self.waiting_queue:
                    self.waiting_queue.append((client_id, peer))
                log_event(f"Client {client_id} added to waiting queue")
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)

            self.current_version += 1
            self.current_lock_holder = (client_id, self.current_version)
            self.heartbeat_intervals[client_id] = time.time()  # Track heartbeat time
            log_event(f"Lock acquired by client: {client_id}, version: {self.current_version}")
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
        
    def lock_release(self, request, context):
        client_id = request.client_id
        request_id = request.request_id

        with self.lock:
            if is_duplicate_request(request_id) and self.current_lock_holder[0] != client_id and self.heartbeat_intervals.get(client_id) is None:
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
            
            # if self.current_lock_holder[0] != client_id:
            #     return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)


            mark_request_processed(request_id)

            if self.current_lock_holder and self.current_lock_holder[0] == client_id:
                self.current_lock_holder = None
                log_event(f"Lock released by client: {client_id}")

                if self.waiting_queue:
                    next_client_id, next_peer = self.waiting_queue.popleft()
                    self.current_version += 1
                    self.current_lock_holder = (next_client_id, self.current_version)
                    self.heartbeat_intervals[next_client_id] = time.time()
                    log_event(f"Lock granted to next client in queue: {next_client_id}, version: {self.current_version}")

                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
            else:
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)

    def heartbeat(self, request, context):
        client_id = request.client_id
        with self.lock:
            self.heartbeat_intervals[client_id] = time.time()
        return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

    def check_heartbeats(self):
        """Periodically check heartbeats to release lock if the client is inactive."""
        while True:
            time.sleep(1)
            current_time = time.time()
            
            with self.lock:
                #Crucial when the server restart
                # if self.current_lock_holder:
                #     lock_holder_id = self.current_lock_holder[0]
                #     last_heartbeat = self.heartbeat_intervals.get(lock_holder_id, 0)
                    
                    # if current_time - last_heartbeat >= 10:
                    #     self.current_lock_holder = None
                    #     log_event(f"Lock released due to timeout for client: {lock_holder_id}")
                    #     print(f"Lock released due to timeout for client: {lock_holder_id}")
                    #     if self.waiting_queue:
                    #         next_client_id, _ = self.waiting_queue.popleft()
                    #         self.current_version += 1
                    #         self.current_lock_holder = (next_client_id, self.current_version)
                    #         self.heartbeat_intervals[next_client_id] = time.time()
                    #         log_event(f"Lock granted to next client in queue: {next_client_id}, version: {self.current_version}")

                # General timeout check
                for client_id, last_heartbeat in list(self.heartbeat_intervals.items()):
                    if current_time - last_heartbeat >= 30:
                        if self.current_lock_holder and self.current_lock_holder[0] == client_id:
                            self.current_lock_holder = None
                            log_event(f"Lock automatically released due to timeout for client: {client_id}")
                            print(f"Lock automatically released due to timeout for client: {client_id}")

                            if self.waiting_queue:
                                next_client_id, _ = self.waiting_queue.popleft()
                                self.current_version += 1
                                self.current_lock_holder = (next_client_id, self.current_version)
                                self.heartbeat_intervals[next_client_id] = time.time()
                                log_event(f"Lock granted to next client in queue: {next_client_id}, version: {self.current_version}")
                        del self.heartbeat_intervals[client_id]

    def getCurrent_lock_holder(self,request,context):
        current_lock_holder=self.current_lock_holder
        return lock_pb2.Response(current_lock_holder=current_lock_holder)

    def file_append(self, request, context):
        client_id = request.client_id
        request_id = request.request_id
        filename = request.filename
        content = request.content
        is_error = False
        
        with self.lock:
            if is_duplicate_request(request_id):
                if request_id not in self.append_request_cache:
                    if is_error:
                        is_error=False
                        return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)   
                    return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
                else:
                    return lock_pb2.Response(status=lock_pb2.Status.DUPLICATE_ERROR)
        
        mark_request_processed(request_id)
        self.append_request_cache[request_id] = True
        
        try:
            with open(filename, 'a') as file:
                file.write(content + '\n')
                self.cleanup_cache(request_id)
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

        except FileNotFoundError:
                log_event(f"File {filename} not found for client {client_id}")
                is_error=True
                self.cleanup_cache(request_id)
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)
            
    def cleanup_cache(self, request_id):
        with self.lock:
            if request_id in self.append_request_cache:
                del self.append_request_cache[request_id]
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  
    lock_service = LockServiceServicer()
    lock_pb2_grpc.add_LockServiceServicer_to_server(lock_service, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at localhost:50051")

    # Run the heartbeat check loop in a separate thread
    threading.Thread(target=lock_service.check_heartbeats, daemon=True).start()

    server.wait_for_termination()

if __name__ == '__main__':
    serve()
