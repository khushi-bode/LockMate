import logging
import sys
from config import LOG_FILE, LOG_LEVEL, LOGS_DIR

def setup_logger():
    """Initializes and returns the application logger."""
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("LockMate")
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Create a default logger instance
logger = setup_logger()
