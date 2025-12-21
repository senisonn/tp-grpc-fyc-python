from collections import defaultdict
from datetime import datetime

class MetricsAggregator:
    """Agrégation des métriques de logs"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'total': 0,
            'by_level': defaultdict(int),
            'errors': 0
        })
    
    def add_log(self, log_entry):
        """Ajouter un log aux métriques"""
        service = log_entry.service_name
        
        self.metrics[service]['total'] += 1
        self.metrics[service]['by_level'][log_entry.level] += 1
        
        if log_entry.level >= 3:
            self.metrics[service]['errors'] += 1
    
    def get_metrics(self, service_name=None):
        """Récupérer les métriques"""
        if service_name:
            return self.metrics.get(service_name, {})
        return dict(self.metrics)
    
    def reset_metrics(self):
        """Réinitialiser les métriques"""
        self.metrics.clear()