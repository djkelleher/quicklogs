## Easily configure Python loggers

### Install
`pip install ezloggers`
### Usage
There is one function: `get_logger`
```py
from ezloggers import get_logger
```

#### Signature
```py
def get_logger(
    name: Optional[str] = None,
    level: Optional[Union[str, int]] = None,
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
        show_file_path (Optional[bool], optional): Show absolute file path in log string prefix rather than just filename. Defaults to True if level is DEBUG, else False.
        file_dir (Optional[Union[str, Path]], optional): Directory where log files should be written.
        max_bytes (int): Max number of bytes to store in one log file.
        backup_count (int): Number of log rotations to keep.

    Returns:
        Logger: The configured logger.
    """
```
