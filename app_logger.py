"""
Logging module for Roxy IRL — writes to a file on the device.
"""
import os
import logging
from datetime import datetime

LOG_FILE = os.path.join(os.path.expanduser("~"), ".roxy_app.log")

def setup_logger():
    """Set up and return the app logger."""
    logger = logging.getLogger("RoxyIRL")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    try:
        fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass  # Can't log if file logging fails
    
    return logger

logger = setup_logger()

def get_log_content():
    """Return the last N lines of the log."""
    try:
        if not os.path.exists(LOG_FILE):
            return "No log file found."
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-100:])  # Last 100 lines
    except Exception as e:
        return f"Error reading log: {e}"
