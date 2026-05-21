import logging
import json
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

def setup_json_logger(logger_name="roxy"):
    """
    Setup a logger that writes JSON formatted logs to a unique timestamped file
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Generate a unique timestamp for the filename (Year-Month-Day_Hour-Minute)
    # Example format: 2026-05-21_11-20
    current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_filename = f"roxy_logs_{current_time_str}.json"
    
    # Get the current working directory
    log_path = Path.cwd() / log_filename
    
    # Create or get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create file handler with JSON formatter
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    
    # Create console handler with simple formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# --- Example Usage ---
if __name__ == "__main__":
    # 1. Initialize the logger (creates the new timestamped file)
    log = setup_json_logger()
    
    # 2. Log some messages
    log.info("A brand new log file has been created for this session!")
    log.debug("This hidden debug message only goes into the JSON file.")
    
    # 3. Log an error demonstration
    try:
        result = 10 / 0
    except ZeroDivisionError:
        log.exception("Captured an intentional math error.")
