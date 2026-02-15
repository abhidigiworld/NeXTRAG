import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "smartrag") -> logging.Logger:
    """Setup structured logger with daily rotation"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. Console Handler (for simple output to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. File Handler (Rotating daily at midnight)
    # This will create files like: smartrag.log, smartrag.log.2024-02-14, etc.
    log_file = os.path.join(log_dir, "smartrag.log")
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep logs for 30 days
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
