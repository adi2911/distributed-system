from concurrent import futures
import grpc
from Proto import lock_pb2
from Proto import lock_pb2_grpc


class LockServiceServicer(lock_pb2_grpc.LockServiceServicer):
    def __init__(self):
        self.lock_table = {} 

    def client_init(self, request, context):
        print(f"Client initialized with rc: {request.rc}")
        return lock_pb2.Int(rc=request.rc)
    
    def lock_acquire():
        pass
    def lock_release():
        pass
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
