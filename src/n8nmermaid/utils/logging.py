# src/n8nmermaid/utils/logging.py
"""Centralized logging configuration for n8nmermaid."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

LOG_FILE_CONVERT = "conversion.log"

logger = logging.getLogger(__name__)


def setup_logging():
    """
    Configures logging based on environment variables.

    Reads N8NMERMAID_LOG_LEVEL (default: INFO) and LOGGING_TARGET
    (default: FILE) from .env file or environment. Sets up console
    and/or file handlers accordingly.
    """
    load_dotenv()

    log_level_name = os.getenv("N8NMERMAID_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    if not isinstance(log_level, int) or log_level == 0:
        print(
            f"Warning: Invalid N8NMERMAID_LOG_LEVEL '{log_level_name}'. "
            "Defaulting to INFO.",
            file=sys.stderr,
        )
        log_level = logging.INFO
        log_level_name = "INFO"

    logging_target = os.getenv("LOGGING_TARGET", "FILE").upper()
    if logging_target not in ["CONSOLE", "FILE"]:
        print(
            f"Warning: Invalid LOGGING_TARGET '{logging_target}'. "
            "Defaulting to FILE.",
            file=sys.stderr,
        )
        logging_target = "FILE"

    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG if logging_target == "FILE" else log_level)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(log_formatter)
    console_log_level = log_level if logging_target == "CONSOLE" else logging.WARNING
    console_handler.setLevel(console_log_level)
    root_logger.addHandler(console_handler)

    file_handler_active = False
    if logging_target == "FILE":
        try:
            log_file_path = Path(LOG_FILE_CONVERT)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            log_file_handler = logging.FileHandler(log_file_path, mode="w")
            log_file_handler.setFormatter(log_formatter)
            log_file_handler.setLevel(log_level)
            root_logger.addHandler(log_file_handler)
            file_handler_active = True
        except Exception as e:
            logging.warning(
                f"Could not configure file logging to {log_file_path}: {e}. "
                "File logging disabled.",
                exc_info=False,
            )

    logger.info(f"Logging configured. Target: {logging_target}.")
    if file_handler_active:
        logger.info(f"File log level: {logging.getLevelName(log_level)}")
    logger.info(f"Console log level: {logging.getLevelName(console_log_level)}")
    logger.debug(f"Root logger level: {logging.getLevelName(root_logger.level)}")
