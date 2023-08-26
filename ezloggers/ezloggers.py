import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union


def any_case_env_var(var: str, default: Optional[str] = None) -> Union[str, None]:
    return os.getenv(var) or os.getenv(var.lower()) or os.getenv(var.upper()) or default


def get_logger(
    name: Optional[str] = None,
    level: Optional[Union[str, int]] = None,
    stdout: Optional[bool] = None,
    show_file_path: Optional[bool] = None,
    file_dir: Optional[Union[str, Path]] = None,
    max_bytes: Optional[int] = 20_000_000,
    backup_count: Optional[int] = 2,
) -> Logger:
    """Create a new logger or return an existing logger with the given name.

    All arguments besides for `name` can be set via environment variables in the form `{LOGGER NAME}_{VARIABLE NAME}` or `EZLOGGERS_{VARIABLE NAME}`.
    Variables including logger name will be chosen before `EZLOGGERS_` variables. Variables can be uppercase or lowercase.

    Args:
        name (Optional[str], optional): Name for the logger. Defaults to None.
        level (Optional[Union[str, int]], optional): Logging level -- CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10.
        stdout (Optional[bool], optional): Whether to write to stdout.
        show_file_path (Optional[bool], optional): Show absolute file path in log string prefix rather than just filename. Defaults to True if level is DEBUG, else False.
        file_dir (Optional[Union[str, Path]], optional): Directory where log files should be written.
        max_bytes (int): Max number of bytes to store in one log file.
        backup_count (int): Number of log rotations to keep.

    Returns:
        Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    # if this is not the first call, the logger will already have handlers.
    if logger.handlers:
        # return the already configured logger.
        return logger

    if stdout is None:
        if name:
            stdout = any_case_env_var(f"{name}_STDOUT")
        stdout = stdout or any_case_env_var("EZLOGGERS_STDOUT")

    if file_dir is None:
        if name:
            file_dir = any_case_env_var(f"{name}_FILE_DIR")
        file_dir = file_dir or any_case_env_var("EZLOGGERS_FILE_DIR")

    if level is None:
        if name:
            level = any_case_env_var(f"{name}_LOG_LEVEL")
        level = level or any_case_env_var("EZLOGGERS_LOG_LEVEL", logging.INFO)

    if show_file_path is None:
        if name:
            show_file_path = any_case_env_var(f"{name}_SHOW_FILE_PATH")
        show_file_path = show_file_path or any_case_env_var("EZLOGGERS_SHOW_FILE_PATH")

    if max_bytes is None:
        if name:
            max_bytes = any_case_env_var(f"{name}_MAX_BYTES")
        max_bytes = max_bytes or any_case_env_var("EZLOGGERS_MAX_BYTES")
    if max_bytes:
        max_bytes = int(max_bytes)

    if backup_count is None:
        if name:
            backup_count = any_case_env_var(f"{name}_BACKUP_COUNT")
        backup_count = backup_count or any_case_env_var("EZLOGGERS_BACKUP_COUNT")
    if backup_count:
        backup_count = int(backup_count)

    # set log level.
    logger.setLevel(
        logging.getLevelName(level.upper()) if isinstance(level, str) else level
    )

    # set formatting and handling.
    file_name_fmt = "pathname" if show_file_path else "filename"
    name_fmt = "[%(name)s]" if name else ""
    formatter = logging.Formatter(
        f"[%(asctime)s][%(levelname)s]{name_fmt}[%({file_name_fmt})s:%(lineno)d] %(message)s"
    )
    if stdout:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if file_dir:
        file = Path(file_dir) / f"{name or f'python_{os.getpid()}'}.log"
        # create log directory if it doesn't currently exist.
        file.parent.mkdir(exist_ok=True, parents=True)
        # add file handler.
        handler = RotatingFileHandler(
            file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # don't duplicate log messages.
    logger.propagate = False

    return logger
