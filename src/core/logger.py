import os
from datetime import datetime
from pathlib import Path

from loguru import logger

from .config import settings


def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Log file path with date
    log_file = log_dir / f"hotline_parser_{datetime.now().strftime('%Y%m%d')}.log"

    # Remove default logger
    logger.remove()

    # Custom format
    format_string = (
        "<green>{time:DD.MM.YY HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "[<cyan>{file}:{line}</cyan>] - "
        "<level>{message}</level>"
    )

    # Console logging
    logger.add(
        sink=lambda msg: print(msg, end=""),  # Print to console without extra newlines
        format=format_string,
        level="INFO",
        colorize=True,
    )

    # File logging
    logger.add(
        sink=log_file,
        format=format_string,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return logger


# Initialize logger
log = setup_logger()
