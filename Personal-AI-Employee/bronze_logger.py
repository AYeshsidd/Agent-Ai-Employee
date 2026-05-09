import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from config import Config


class BronzeLogger:
    """Centralized logging for Bronze Tier operations"""

    _loggers = {}

    @staticmethod
    def setup_logs_directory():
        """Create logs directory if it doesn't exist"""
        Config.LOGS_DIR.mkdir(exist_ok=True)

    @staticmethod
    def get_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
        """
        Get or create a logger with specified name

        Args:
            name: Logger name
            log_file: Optional specific log file path

        Returns:
            Configured logger instance
        """
        if name in BronzeLogger._loggers:
            return BronzeLogger._loggers[name]

        BronzeLogger.setup_logs_directory()

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        bronze_handler = logging.FileHandler(Config.BRONZE_TIER_LOG)
        bronze_handler.setFormatter(formatter)
        logger.addHandler(bronze_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        BronzeLogger._loggers[name] = logger
        return logger

    @staticmethod
    def log_task_action(logger: logging.Logger, action: str, task_name: str,
                       source: str, status: str, details: str = ""):
        """
        Log task action with standardized format

        Args:
            logger: Logger instance
            action: Action type (CREATE, READ, UPDATE, MOVE, DELETE, ANALYZE)
            task_name: Task filename
            source: Source component (Watcher, VaultManager, Skill)
            status: Status (SUCCESS, FAILED, IN_PROGRESS)
            details: Additional details
        """
        timestamp = datetime.now().isoformat()
        log_message = f"[{action}] Task: {task_name} | Source: {source} | Status: {status}"

        if details:
            log_message += f" | Details: {details}"

        if status == "FAILED":
            logger.error(log_message)
        elif status == "IN_PROGRESS":
            logger.info(log_message)
        else:
            logger.info(log_message)

    @staticmethod
    def log_lifecycle_event(logger: logging.Logger, task_name: str,
                           from_folder: str, to_folder: str, status: str):
        """
        Log task lifecycle transition

        Args:
            logger: Logger instance
            task_name: Task filename
            from_folder: Source folder
            to_folder: Destination folder
            status: Status (SUCCESS, FAILED)
        """
        timestamp = datetime.now().isoformat()
        log_message = f"[LIFECYCLE] Task: {task_name} | Transition: {from_folder} -> {to_folder} | Status: {status}"

        if status == "FAILED":
            logger.error(log_message)
        else:
            logger.info(log_message)

    @staticmethod
    def log_watcher_event(logger: logging.Logger, event_type: str,
                         file_name: str, status: str, details: str = ""):
        """
        Log watcher file system event

        Args:
            logger: Logger instance
            event_type: Event type (FILE_DETECTED, TASK_CREATED, FILE_REMOVED)
            file_name: File name
            status: Status (SUCCESS, FAILED)
            details: Additional details
        """
        timestamp = datetime.now().isoformat()
        log_message = f"[WATCHER] Event: {event_type} | File: {file_name} | Status: {status}"

        if details:
            log_message += f" | Details: {details}"

        if status == "FAILED":
            logger.error(log_message)
        else:
            logger.info(log_message)

    @staticmethod
    def log_skill_execution(logger: logging.Logger, skill_name: str,
                           operation: str, status: str, details: str = ""):
        """
        Log agent skill execution

        Args:
            logger: Logger instance
            skill_name: Skill name
            operation: Operation performed
            status: Status (SUCCESS, FAILED, IN_PROGRESS)
            details: Additional details
        """
        timestamp = datetime.now().isoformat()
        log_message = f"[SKILL] {skill_name} | Operation: {operation} | Status: {status}"

        if details:
            log_message += f" | Details: {details}"

        if status == "FAILED":
            logger.error(log_message)
        else:
            logger.info(log_message)
