import os
import json
from datetime import datetime
from pathlib import Path

class FileStorage:
    """Gestion du stockage des logs sur disque"""
    
    def __init__(self, log_directory):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.logs_buffer = []
        self.buffer_size = 100
    
    def write_log(self, log_entry):
        """Écrire un log dans un fichier"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        service_name = log_entry.service_name or 'unknown'
        
        log_file = self.log_directory / f"{service_name}_{date_str}.log"
        
        log_data = {
            'id': log_entry.id,
            'service': log_entry.service_name,
            'level': self._get_level_name(log_entry.level),
            'message': log_entry.message,
            'timestamp': log_entry.timestamp,
            'metadata': dict(log_entry.metadata),
            'trace_id': log_entry.trace_id
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_data) + '\n')
    
    def batch_write_logs(self, log_entries):
        """Écriture par batch pour optimiser les I/O"""
        for log_entry in log_entries:
            self.write_log(log_entry)
    
    def _get_level_name(self, level):
        """Convertir le niveau de log en string"""
        levels = {0: 'DEBUG', 1: 'INFO', 2: 'WARNING', 3: 'ERROR', 4: 'CRITICAL'}
        return levels.get(level, 'UNKNOWN')
    
    def get_logs(self, service_name=None, start_date=None, end_date=None):
        """Récupérer les logs depuis les fichiers"""
        logs = []
        
        for log_file in self.log_directory.glob('*.log'):
            if service_name and not log_file.name.startswith(service_name):
                continue
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        logs.append(log)
                    except json.JSONDecodeError:
                        continue
        
        return logs