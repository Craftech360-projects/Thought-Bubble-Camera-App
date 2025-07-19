"""Logging configuration for Thought Bubble App."""

import logging
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """Configure logging for the application."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # Suppress some noisy loggers
    logging.getLogger('pygame').setLevel(logging.WARNING)
    
    return logger