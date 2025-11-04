import grpc
import logs_pb2
import logs_pb2_grpc

def stream_logs(level, duration):
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = logs_pb2_grpc.LogServiceStub(channel)
        
        # Créer la requête
        request = logs_pb2.LogRequest(level=level, duration=duration)
        
        print(f"📡 Streaming des logs de niveau {level} pendant {duration} secondes...\n")
        
        # Recevoir le flux de logs
        try:
            for log in stub.StreamLogs(request):
                print(f"[{log.timestamp}] [{log.level}] [{log.service}] {log.message}")
        except grpc.RpcError as e:
            print(f"❌ Erreur gRPC: {e}")

if __name__ == '__main__':
    #stream_logs("INFO", 10)  
    stream_logs("ERROR", 5)