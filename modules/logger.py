import logging
import os
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_FOLDER = os.path.join(PROJECT_ROOT, "logs")
LOG_FILENAME = os.path.join(LOGS_FOLDER, f"app_log_{datetime.now().strftime('%Y-%m-%d')}.txt")

def setup_logger(name="flask_automation"):
    """Sets up a logger that logs to the console and a daily file."""
    
    # 1. Create the logs directory if it doesn't exist
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    
    # 2. Get or create the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent handlers from being added multiple times if setup_logger is called repeatedly
    if not logger.handlers:
        # 3. File Handler: writes to the daily log file. ADDING encoding='utf-8'
        file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 4. Console Handler: writes to the console. The StreamHandler uses sys.stderr by default.
        # We need to ensure its stream is UTF-8 compatible. 
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 5. Formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 6. Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize the main log handler for use across the application
LOG = setup_logger()
