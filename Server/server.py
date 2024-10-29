from concurrent import futures
import grpc
from Proto import lock_pb2
from Proto import lock_pb2_grpc


class LockServiceServicer(lock_pb2_grpc.LockServiceServicer):
    def __init__(self):
        self.lock_table = {}
        self.active_clients = {}
        self.next_client_id = 1 
        
    def client_init(self, request, context):
        client_id = self.next_client_id
        self.next_client_id += 1
        self.active_clients[context.peer()] = client_id # context.peer() uniquely identifies client connection at a network level. returns eg: ipv4:a.b.c.d:xyx I added it for tracking ?
        print(f"Client initialized with client_id: {client_id}")
        return lock_pb2.Int(rc=client_id)
    
    def lock_acquire(self, request, context):
        client_id = self.active_clients.get(context.peer())
        if client_id is None:
            return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)
        
        if client_id in self.lock_table:
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS) # lock already acquired by this client_id
        elif any(self.lock_table.values()):
            return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR) # some other client holds lock
        else:
            self.lock_table[client_id] = True 
            print(f"Lock Acquired by client: {client_id}")
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS) # lock acquired
        
    def lock_release(self, request, context):
        client_id = self.active_clients.get(context.peer())
        if client_id is None:
            return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR)
        if self.lock_table.get(client_id):
            self.lock_table.pop(client_id)
            print(f"Lock released by client: {client_id}")
            return lock_pb2.Response(status=lock_pb2.Status.SUCCESS) #lock released
        else:
            return lock_pb2.Response(status=lock_pb2.Status.FILE_ERROR) # no lock to release
            
    def append_file():
        pass
    def close():
         pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # Multi-threaded server
    lock_pb2_grpc.add_LockServiceServicer_to_server(LockServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at localhost:50051")
    server.wait_for_termination()

if __name__ == '__main__':
	serve()

