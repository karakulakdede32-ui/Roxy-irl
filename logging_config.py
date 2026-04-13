import logging
import json
import os
from datetime import datetime
from pathlib import Path

class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_json_logger(logger_name="roxy", log_filename="roxy_logs.json"):
    """
    Setup a logger that writes JSON formatted logs to a file in the current working directory
    
    Args:
        logger_name (str): Name of the logger
        log_filename (str): Name of the JSON log file
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get the current working directory (where the script is run from)
    log_path = Path.cwd() / log_filename
    
    # Create or get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create file handler with JSON formatter
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    
    # Create console handler with simple formatter (optional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
