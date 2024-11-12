from concurrent import futures
import grpc
import threading
from collections import deque
import time
from Proto import lock_pb2
from Proto import lock_pb2_grpc
from .utils import load_server_state, log_event, is_duplicate_request, mark_request_processed, is_port_available

HEARTBEAT_INTERVAL = 5  # Heartbeat interval in seconds
HEARTBEAT_TIMEOUT = 20  # Timeout threshold for failover
PRIMARY_SERVER = "primary"
BACKUP_SERVER = "backup"

class LockServiceServicer(lock_pb2_grpc.LockServiceServicer):
    def __init__(self, role=BACKUP_SERVER):
        self.role = role  # Set server role: PRIMARY_SERVER or BACKUP_SERVER
        self.current_lock_holder = None  # (client_id, version) of current lock holder
        self.current_version = 0  # Version for each lock acquisition
        self.waiting_queue = deque()  # Queue for clients waiting for the lock
        self.next_client_id = 1  # ID assignment for new clients
        self.lock = threading.Lock()  # Synchronization lock
        self.heartbeat_intervals = {}  # Last heartbeat time for each client
        self.backup_servers = ["localhost:50052", "localhost:50053", "localhost:50054"]  # Backup addresses
        self.last_primary_heartbeat = time.time()  # Track primary's heartbeat in backups
        self.current_address = 'locahost:50051'

        # Load state on startup
        load_server_state(self)
        
        # Only primary starts heartbeat thread
        if self.role == PRIMARY_SERVER:
            threading.Thread(target=self.send_heartbeats_to_backups, daemon=True).start()
        else:
            threading.Thread(target=self.check_primary_heartbeat, daemon=True).start()

    def send_heartbeats_to_backups(self):
        """Primary server sends heartbeats to backups."""
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            for backup_address in self.backup_servers:
                if backup_address == self.current_address:
                    continue
                try:
                    channel = grpc.insecure_channel(backup_address)
                    stub = lock_pb2_grpc.LockServiceStub(channel)
                    stub.heartbeat(lock_pb2.Heartbeat(client_id=0))
                    print(f"Heartbeat sent to backup at {backup_address}")
                except grpc.RpcError:
                    print(f"Failed to send heartbeat to backup at {backup_address}")

    def check_primary_heartbeat(self):
        """Backup server checks for primary's heartbeat."""
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            if time.time() - self.last_primary_heartbeat > HEARTBEAT_TIMEOUT:
                print("Primary heartbeat missed. Initiating failover.")
                self.become_primary()
                break

    def heartbeat(self, request, context):
        """Handle heartbeat from primary or clients."""
        if self.role == BACKUP_SERVER:
            print(f"primary server is active {self.current_address}")
            self.last_primary_heartbeat = time.time()
        else:
            client_id = request.client_id
            with self.lock:
                self.heartbeat_intervals[client_id] = time.time()
        return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

    def become_primary(self):
        """Promote this backup server to primary."""
        self.role = PRIMARY_SERVER
        load_server_state(self)  # Load state from log file
        threading.Thread(target=self.check_heartbeats, daemon=True).start()
        threading.Thread(target=self.send_heartbeats_to_backups, daemon=True).start()
        print("This server is now the primary")

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
                    return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)


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


    def check_heartbeats(self):
        """Periodically check heartbeats to release lock if the client is inactive."""
        while True:
            time.sleep(1)
            current_time = time.time()
            
            with self.lock:
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

    def file_append(self, request, context):
            pass

def serve(role):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    lock_service = LockServiceServicer(role=role)
    lock_pb2_grpc.add_LockServiceServicer_to_server(lock_service, server)
    if(role == PRIMARY_SERVER):
        server.add_insecure_port('[::]:50051')
        server.start()
        threading.Thread(target=lock_service.check_heartbeats, daemon=True).start()
    else:
        flag = True
        ports = [50052, 50053, 50054]

        for port in ports:
            if is_port_available(port):
                flag = False
                server.add_insecure_port(f'[::]:{port}')
                lock_service.current_address = f"localhost:{port}"
                server.start()
                print(f"{role.capitalize()} server started at: {port}")
                break
        if flag is True:
            print("No Port available")

    server.wait_for_termination()

if __name__ == '__main__':
    # Set role as "primary" or "backup" here. Defaulting to primary for demonstration.
    role = input("Enter role server")
    serve(role)
