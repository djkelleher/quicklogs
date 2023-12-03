import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal, Optional, Union


def any_case_env_var(var: str, default: Optional[str] = None) -> Union[str, None]:
    value = os.getenv(var) or os.getenv(var.lower()) or os.getenv(var.upper())
    if value is None:
        return default
    if (vl := value.lower()) == "true":
        return True
    if vl == "false":
        return False
    return value


def get_logger(
    name: Optional[str] = None,
    level: Optional[Union[str, int]] = None,
    stdout: Optional[bool] = None,
    file_dir: Optional[Union[str, Path]] = None,
    show_source: Optional[Literal["pathname", "filename"]] = None,
    max_bytes: Optional[int] = 20_000_000,
    backup_count: Optional[int] = 2,
) -> Logger:
    """Create a new logger or return an existing logger with the given name.

    All arguments besides for `name` can be set via environment variables in the form `{LOGGER NAME}_{VARIABLE NAME}` or `QUICKLOGS_{VARIABLE NAME}`.
    Variables including logger name will be chosen before `QUICKLOGS_` variables. Variables can be uppercase or lowercase.

    Args:
        name (Optional[str], optional): Name for the logger. Defaults to None.
        level (Optional[Union[str, int]], optional): Logging level -- CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10. Defaults to None.
        stdout (Optional[bool], optional): Whether to write to stdout. Defaults to None.
        file_dir (Optional[Union[str, Path]], optional): Directory where log files should be written. Defaults to None.
        show_source (Optional[bool], optional): `pathname`: Show absolute file path in log string prefix. `filename`: Show file name in log string prefix. Defaults to None.
        max_bytes (int): Max number of bytes to store in one log file. Defaults to 20MB.
        backup_count (int): Number of log rotations to keep. Defaults to 2.

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
        stdout = stdout or any_case_env_var("QUICKLOGS_STDOUT")

    if file_dir is None:
        if name:
            file_dir = any_case_env_var(f"{name}_FILE_DIR")
        file_dir = file_dir or any_case_env_var("QUICKLOGS_FILE_DIR")

    if stdout is None and file_dir is None:
        stdout = True

    if level is None:
        if name:
            level = any_case_env_var(f"{name}_LOG_LEVEL")
        level = level or any_case_env_var("QUICKLOGS_LOG_LEVEL", logging.INFO)

    if show_source is None:
        if name:
            show_source = any_case_env_var(f"{name}_SHOW_SOURCE")
        show_source = show_source or any_case_env_var("QUICKLOGS_SHOW_SOURCE")

    if max_bytes is None:
        if name:
            max_bytes = any_case_env_var(f"{name}_MAX_BYTES")
        max_bytes = max_bytes or any_case_env_var("QUICKLOGS_MAX_BYTES")
    if max_bytes:
        max_bytes = int(max_bytes)

    if backup_count is None:
        if name:
            backup_count = any_case_env_var(f"{name}_BACKUP_COUNT")
        backup_count = backup_count or any_case_env_var("QUICKLOGS_BACKUP_COUNT")
    if backup_count:
        backup_count = int(backup_count)

    # set log level.
    logger.setLevel(
        logging.getLevelName(level.upper()) if isinstance(level, str) else level
    )

    # set formatting and handling.
    log_format = "[%(asctime)s][%(levelname)s]"
    if name:
        log_format += "[%(name)s]"
    if show_source:
        log_format += f"[%({show_source})s:%(lineno)d]"
    log_format += " %(message)s"
    formatter = logging.Formatter(log_format)
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
