import logging
import os

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(level=log_level, format=log_format)
    
    # Create a file handler for logging to a file
    log_file = os.getenv("LOG_FILE", "app.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Add the file handler to the root logger
    logging.getLogger().addHandler(file_handler)

setup_logging()