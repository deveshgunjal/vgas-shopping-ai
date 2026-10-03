"""
Logging configuration for VGAS Shopping AI
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

from app.core.config import settings


def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create file handler
    log_file = logs_dir / f"{settings.LOG_FILE}"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.getLogger("uvicorn.access").setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.getLogger("uvicorn.error").setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.INFO)
    
    return root_logger


class LogColors:
    """ANSI color codes for logging"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def color_log(message: str, color: str = "RESET", **kwargs):
    """Print colored log message safely"""
    color_code = getattr(LogColors, color.upper(), LogColors.RESET)
    text = f"{color_code}{message}{LogColors.RESET}"
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'), **kwargs)


# Custom logger class
class VGASLogger:
    """Custom logger with VGAS branding"""
    
    def __init__(self, name: str = "VGAS"):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def info(self, message: str, **kwargs):
        self.logger.info(f"[{self.name}] {message}", **kwargs)
    
    def success(self, message: str, **kwargs):
        color_log(f"[{self.name}] ✅ {message}", "GREEN", **kwargs)
        self.logger.info(f"[{self.name}] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs):
        color_log(f"[{self.name}] ⚠️ {message}", "YELLOW", **kwargs)
        self.logger.warning(f"[{self.name}] {message}", **kwargs)
    
    def error(self, message: str, **kwargs):
        color_log(f"[{self.name}] ❌ {message}", "RED", **kwargs)
        self.logger.error(f"[{self.name}] {message}", **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(f"[{self.name}] {message}", **kwargs)
    
    def critical(self, message: str, **kwargs):
        color_log(f"[{self.name}] 🚨 {message}", "RED", **kwargs)
        self.logger.critical(f"[{self.name}] {message}", **kwargs)


# Create VGAS logger
vgas_logger = VGASLogger("VGAS-AI")
