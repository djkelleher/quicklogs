import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest

from quicklogs import get_logger


@pytest.mark.parametrize("use_env_vars", [False, True])
def test_logger(use_env_vars):
    file_dir = Path(TemporaryDirectory().name)
    level = "DEBUG"
    backup_count = 2
    max_bytes = 1000

    name = f"test_logger_{uuid4()}"
    if use_env_vars:
        for var, value in (
            (f"{name}_LOG_LEVEL", level),
            (f"{name}_SHOW_SOURCE", "pathname"),
            (f"{name}_FILE_DIR", str(file_dir)),
            (f"{name}_MAX_BYTES", str(max_bytes)),
            (f"{name}_BACKUP_COUNT", str(backup_count)),
        ):
            os.environ[var] = value
        logger = get_logger(name=name)
    else:
        logger = get_logger(
            name=name,
            level=level,
            show_source="pathname",
            file_dir=file_dir,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )

    random_uuid = str(uuid4())

    logger.info(random_uuid)
    logger.debug(random_uuid)

    log_file = file_dir / f"{name}.log"
    assert log_file.is_file()
    log_contents = log_file.read_text().strip()

    assert log_contents.count("[INFO]") == 1
    assert log_contents.count("[DEBUG]") == 1

    assert len(log_contents.split("\n")) == 2

    for _ in range(10000):
        logger.info(random_uuid)

    assert len(list(file_dir.iterdir())) == backup_count + 1
