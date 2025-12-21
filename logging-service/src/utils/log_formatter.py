from datetime import datetime

class LogFormatter:
    """Formatage des logs pour l'affichage"""
    
    @staticmethod
    def format_log_entry(log_entry):
        """Formate un log pour l'affichage console"""
        timestamp = datetime.fromtimestamp(log_entry.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        level = LogFormatter._get_level_name(log_entry.level)
        
        return f"[{timestamp}] [{log_entry.service_name}] [{level}] {log_entry.message}"
    
    @staticmethod
    def _get_level_name(level):
        levels = {0: 'DEBUG', 1: 'INFO', 2: 'WARNING', 3: 'ERROR', 4: 'CRITICAL'}
        return levels.get(level, 'UNKNOWN')