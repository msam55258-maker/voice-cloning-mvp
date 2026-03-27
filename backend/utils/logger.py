"""backend/utils/logger.py

Centralized logging configuration for the entire application.
Provides a standard formatter and level control.
"""

import logging
import sys

# ── LOGGING CONFIGURATION ─────────────────────────────────────────────────────

def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger instance with a standard format."""
    logger = logging.getLogger(name)
    
    # Only add handlers if they haven't been added yet (prevents double logging)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

# Root application logger
logger = setup_logger("voice_cloning")
