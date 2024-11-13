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
    def __init__(self, server_id, peers, role=BACKUP_SERVER):
        self.server_id = server_id
        self.peers = sorted(peers)  # Ensure peers are sorted to establish FIFO order
        self.role = role  # Set server role: PRIMARY_SERVER or BACKUP_SERVER
        self.current_lock_holder = None  # client_id of current lock holder
        self.waiting_queue = deque()  # Queue for clients waiting for the lock
        self.next_client_id = 1  # ID assignment for new clients
        self.lock = threading.Lock()  # Synchronization lock
        self.heartbeat_intervals = {}  # Last heartbeat time for each client
        self.backup_servers = ["localhost:50051","localhost:50052", "localhost:50053", "localhost:50054"]  # Backup addresses
        self.last_primary_heartbeat = time.time()  # Track primary's heartbeat in backups
        self.current_term = 0  # Raft-style term
        self.voted_for = None  # Candidate this server voted for in the current term
        self.votes_received = 0  # Track received votes in the current election
        self.current_address = 'localhost:50051'

        # Load state on startup
        load_server_state(self)
        
        # Start leader election or heartbeat checking based on role
        if self.role == PRIMARY_SERVER:
            threading.Thread(target=self.send_heartbeats_to_backups, daemon=True).start()
        else:
            threading.Thread(target=self.check_primary_heartbeat, daemon=True).start()

    def start_election(self):
        """Initiate an election process in a FIFO order to become the primary server."""
        position = self.peers.index(self.server_id)
        delay = position
        for i in range(0,position):
            if is_port_available(int(peers[i])):
                delay = delay-1
                print(delay)
        election_delay = delay * delay * 10  # Delay election attempt based on position in FIFO order
        
        print(f"Server {self.server_id} waiting {election_delay} seconds before election attempt.")
        time.sleep(election_delay)

        # Recheck primary status before starting the election
        if time.time() - self.last_primary_heartbeat <= HEARTBEAT_TIMEOUT:
            print(f"Server {self.server_id} detected heartbeat from primary; aborting election.")
            return

        # Start election
        self.current_term += 1
        self.voted_for = self.server_id
        self.votes_received = 1  # Vote for self
        print(f"Server {self.server_id} started election for term {self.current_term}")

        # Request votes from peers
        for peer in self.peers:
            if peer != self.server_id and not is_port_available(int(peer)):
                threading.Thread(target=self.request_vote, args=(peer,), daemon=True).start()
            if not is_port_available(int(peer)):
                self.votes_received+=1

        # Election timeout to check if majority vote is achieved
        election_timeout = time.time() + 3
        while time.time() < election_timeout:
            if self.votes_received >= (len(self.peers) + 1) // 2 + 1:
                self.become_primary()
                return
            time.sleep(0.1)
        
        # If not elected, revert to follower
        self.role = BACKUP_SERVER
        print(f"Server {self.server_id} reverting to follower after unsuccessful election.")

    def request_vote(self, peer):
        """Request a vote from a peer."""
        try:
            channel = grpc.insecure_channel(f"localhost:{peer}")
            stub = lock_pb2_grpc.LockServiceStub(channel)
            vote_request = lock_pb2.VoteRequest(candidate_id=self.server_id, term=self.current_term)
            response = stub.vote(vote_request)
            
            if response.vote_granted:
                self.votes_received += 1
                print(f"Server {self.server_id} received a vote from {peer}. Total votes: {self.votes_received}")
        except grpc.RpcError:
            print(f"Failed to request vote from {peer}")

    def vote(self, request, context):
        """Respond to a vote request from a candidate server."""
        if request.term > self.current_term:
            self.current_term = request.term
            self.voted_for = request.candidate_id
            print(f"Server {self.server_id} voted for {request.candidate_id} in term {self.current_term}")
            return lock_pb2.VoteResponse(vote_granted=True)
        return lock_pb2.VoteResponse(vote_granted=False)

    def become_primary(self):
        """Promote this backup server to primary."""
        self.role = PRIMARY_SERVER
        print(f"Server {self.server_id} is now the primary.")
        load_server_state(self)  
        threading.Thread(target=self.send_heartbeats_to_backups, daemon=True).start()
        threading.Thread(target=self.check_heartbeats, daemon=True).start()


    def check_primary_heartbeat(self):
        """Backup server checks for primary's heartbeat."""
        while self.role == BACKUP_SERVER:
            time.sleep(HEARTBEAT_INTERVAL)
            print("primary is active")
            if time.time() - self.last_primary_heartbeat > HEARTBEAT_TIMEOUT:
                print("Primary server heartbeat missed. Initiating election.")
                self.start_election()
                continue

    def send_heartbeats_to_backups(self):
        """Primary server sends heartbeats to backups."""
        while self.role == PRIMARY_SERVER:
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
                    pass
                    print(f"Failed to send heartbeat to backup at {backup_address}")

    def log_heartbeat(self):
        while(True):
            if self.current_lock_holder is not None and self.heartbeat_intervals is not None and self.heartbeat_intervals.get(self.current_lock_holder) is not None:
                log_event(f"logged heartbeat for lock holder : {self.current_lock_holder}, {self.heartbeat_intervals[self.current_lock_holder]}")
                time.sleep(5)

    def heartbeat(self, request, context):
        """Handle heartbeat from primary or clients."""
        if self.role == BACKUP_SERVER:
            self.last_primary_heartbeat = time.time()
        else:
            client_id = request.client_id
            with self.lock:
                self.heartbeat_intervals[client_id] = time.time()
        return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

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
                if self.current_lock_holder and self.current_lock_holder == client_id:
                    return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
                else:
                    return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)


            # Record the request_id as processed
            mark_request_processed(request_id)

            if self.current_lock_holder and self.current_lock_holder == client_id:
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)

            if self.current_lock_holder is not None:
                if (client_id, peer) not in self.waiting_queue:
                    self.waiting_queue.append((client_id, peer))
                log_event(f"Client added to waiting queue : {client_id}")
                return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)

            self.current_lock_holder = client_id
            self.heartbeat_intervals[client_id] = time.time()  # Track heartbeat time
            log_event(f"Lock acquired by client: {client_id}")
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
        
    def lock_release(self, request, context):
        client_id = request.client_id
        request_id = request.request_id

        with self.lock:
            if is_duplicate_request(request_id) and self.current_lock_holder != client_id and self.heartbeat_intervals.get(client_id) is None:
                return lock_pb2.Response(status=lock_pb2.Status.SUCCESS)
            

            mark_request_processed(request_id)

            if self.current_lock_holder and self.current_lock_holder == client_id:
                self.current_lock_holder = None
                log_event(f"Lock released by client: {client_id}")

                if self.waiting_queue:
                    next_client_id, next_peer = self.waiting_queue.popleft()
                    self.current_lock_holder = next_client_id
                    self.heartbeat_intervals[next_client_id] = time.time()
                    log_event(f"Lock granted to next client in queue: {next_client_id}")

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
                if self.current_lock_holder != None and self.heartbeat_intervals.get(self.current_lock_holder) is None:
                    #Inital hearbeat after recovery
                    self.heartbeat_intervals[self.current_lock_holder] = time.time()           
                for client_id, last_heartbeat in list(self.heartbeat_intervals.items()):
                    if current_time - last_heartbeat >= 30:
                        if self.current_lock_holder and self.current_lock_holder == client_id:
                            self.current_lock_holder = None
                            log_event(f"Lock automatically released due to timeout for client: {client_id}")
                            print(f"Lock automatically released due to timeout for client: {client_id}")

                            if self.waiting_queue:
                                next_client_id, _ = self.waiting_queue.popleft()
                                self.current_lock_holder = next_client_id
                                self.heartbeat_intervals[next_client_id] = time.time()
                                log_event(f"Lock granted to next client in queue: {next_client_id}")
                        del self.heartbeat_intervals[client_id]

    def file_append(self, request, context):
            pass

def serve(server_id,peers,role):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    lock_service = LockServiceServicer(server_id, peers,role=role)
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
    server_id = input("Enter server id  ")
    role = input("Enter the role of the server  ")
    peers = ['50051','50052','50053','50054']

    if(server_id == '1') :
        server_id = '50051'
    elif(server_id == '2') :
        server_id = '50052'
    elif(server_id == '3') :
        server_id = '50053'
    elif(server_id == '4') :
        server_id = '50054'

    serve(server_id,peers,role)
