import logging
import sys
from datetime import datetime

class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = LogColors.RESET
        if record.levelno == logging.ERROR:
            log_color = LogColors.RED
        elif record.levelno == logging.WARNING:
            log_color = LogColors.YELLOW
        elif record.levelno == logging.INFO:
            log_color = LogColors.GREEN

        formatted = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {record.levelname}: {record.msg}"
        return f"{log_color}{formatted}{LogColors.RESET}"
    
def setup_logger():
    logger = logging.getLogger("custom_logger")
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
