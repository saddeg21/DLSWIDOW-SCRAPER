"""
Logging config module.

This module provides logging setup and utilities.
"""

import logging
import logging.config
import os
import yaml
from pathlib import Path
from typing import Optional

def setup_logging(config_path: Optional[str] = None, log_level: Optional[str] = None) -> None:
    """
    Setup logging configuration.

    Args:
        config_path: Path to the logging configuration file.
        log_level: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    if config_path is None:
        current_dir = Path(__file__).parent.parent.parent # baya ilkel ama çalışıyor
        config_path = current_dir / "config" / "logging.yaml"
    
    if Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        except Exception as e:
            print(f"Warning: Could not load logging config {config_path}: {e}")
            _setup_basic_logging(log_level)
    else:
        _setup_basic_logging(log_level) 

def _setup_basic_logging(log_level: Optional[str] = None) -> None:
    """
    Setup basic logging configuration.
    """
    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)

    # formatter is being used to format log messages
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("logs/twitter_scraper.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    """
    if not logging.getLogger().handlers:
        setup_logging()
    return logging.getLogger("twitter_scraper.{name}")

class LoggerMixin:
    """
    Mixin class to add logging capabilities to a class.
    """

    @property
    def logger(self) -> logging.Logger:
        """Get the logger for this class."""
        return get_logger(self.__class__.__name__)

def log_performance(func):
    """
    Decorator to log the performance of a function.
    """

    import time
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(
                f"{func.__name__} took {execution_time:.2f} seconds"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {e}"
            )
            raise

    return wrapper

class LoggingContext:
    """Context manager for enhanced logging."""

    def __init__(self, logger_name: str, operation: str):
        """ Inits logging context manager."""
        self.logger = get_logger(logger_name)
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        """Enters the logging context."""
        self.logger.info(f"Starting {self.operation}")
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exits the logging context."""
        import time
        duration = time.time() - self.start_time

        if exc_type is None:
            self.logger.info(f"Completed {self.operation} in {duration:.2f} seconds")
        else:
            self.logger.error(f"Failed {self.operation} in {duration:.2f} seconds: {exc_val}")

        return False