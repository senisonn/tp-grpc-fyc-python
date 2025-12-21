import grpc
import proto.logging_pb2 as logging_pb2
import proto.logging_pb2_grpc as logging_pb2_grpc
import proto.common_pb2 as common_pb2
from src.storage import FileStorage
from src.storage import MetricsAggregator
from src.utils import LogFormatter
from src.config import config
import time

class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    """Implémentation du service de logging"""
    
    def __init__(self):
        self.storage = FileStorage(config.LOG_DIRECTORY)
        self.metrics = MetricsAggregator()
        self.formatter = LogFormatter()
        print(f"✅ Logging Service initialisé - Stockage: {config.LOG_DIRECTORY}")
    
    def StreamLogs(self, request_iterator, context):
        """
        Réception de logs en streaming depuis les autres services
        """
        log_count = 0
        
        try:
            for log_entry in request_iterator:
                # Afficher dans la console
                formatted_log = self.formatter.format_log_entry(log_entry)
                print(formatted_log)
                
                # Stocker sur disque
                self.storage.write_log(log_entry)
                
                # Mettre à jour les métriques
                self.metrics.add_log(log_entry)
                
                log_count += 1
            
            return common_pb2.Status(
                success=True,
                message=f"Received and stored {log_count} logs",
                code=200
            )
        
        except Exception as e:
            print(f"❌ Erreur lors du streaming de logs: {str(e)}")
            return common_pb2.Status(
                success=False,
                message=f"Error: {str(e)}",
                code=500
            )
    
    def GetLogs(self, request, context):
        """
        Récupération des logs stockés (streaming serveur)
        """
        try:
            logs = self.storage.get_logs(
                service_name=request.service_name if request.service_name else None
            )
            
            # Filtrer par niveau si spécifié
            if request.min_level:
                logs = [log for log in logs if log.get('level', 0) >= request.min_level]
            
            # Limiter le nombre de résultats
            limit = request.limit if request.limit > 0 else 100
            logs = logs[:limit]
            
            # Streamer les logs
            for log in logs:
                log_entry = logging_pb2.LogEntry(
                    id=log['id'],
                    service_name=log['service'],
                    level=self._get_level_value(log['level']),
                    message=log['message'],
                    timestamp=log['timestamp'],
                    metadata=log.get('metadata', {}),
                    trace_id=log.get('trace_id', '')
                )
                yield log_entry
        
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des logs: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def GetMetrics(self, request, context):
        """
        Récupération des métriques agrégées
        """
        try:
            metrics_data = self.metrics.get_metrics(request.service_name)
            
            # Construire la réponse
            log_counts = {}
            service_metrics = []
            
            if request.service_name:
                # Métriques pour un service spécifique
                if metrics_data:
                    log_counts = {str(k): v for k, v in metrics_data['by_level'].items()}
                    total = metrics_data['total']
                else:
                    total = 0
            else:
                # Métriques pour tous les services
                total = 0
                for service, data in metrics_data.items():
                    total += data['total']
                    service_metric = logging_pb2.ServiceMetric(
                        service_name=service,
                        log_count=data['total'],
                        error_count=data['errors'],
                        average_response_time=0.0
                    )
                    service_metrics.append(service_metric)
            
            return logging_pb2.MetricsResponse(
                log_counts_by_level=log_counts,
                total_logs=total,
                service_metrics=service_metrics
            )
        
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des métriques: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
    
    def HealthCheck(self, request, context):
        """Health check du service"""
        return logging_pb2.HealthCheckResponse(
            healthy=True,
            version="1.0.0",
            uptime_seconds=int(time.time())
        )
    
    def _get_level_value(self, level_name):
        """Convertir le nom du niveau en valeur"""
        levels = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
        return levels.get(level_name, 1)