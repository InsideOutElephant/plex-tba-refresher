# plex_refresher/utils/logging_setup.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict
from plex_refresher.exceptions.config_errors import ConfigurationError  # Fixed import

class LoggingSetup:
    @staticmethod
    def setup_logging(config: Dict) -> logging.Logger:
        log_config = config['logging']
        log_path = Path(log_config['file'])
        
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            test_file = log_path.parent / '.test_write'
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            raise ConfigurationError(f"Cannot write to log directory {log_path.parent}: {str(e)}")
        
        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format=log_config['format'],
            handlers=[
                RotatingFileHandler(
                    log_path,
                    maxBytes=log_config['max_size_mb'] * 1024 * 1024,
                    backupCount=log_config['backup_count']
                ),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('plex_refresher')