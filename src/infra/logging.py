"""Logging setup for sg_project_template.

Uses loguru: a single global `logger` that any module can import with
`from loguru import logger` — no per-module `get_logger(__name__)` boilerplate.
The first call to `setup_logger()` configures the global handler; subsequent
calls are no-ops.
"""

import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger

__all__ = ["logger", "setup_logger"]


_CONFIGURED = False


def setup_logger(level: str = "INFO", log_file: Path | None = None) -> None:
    """Configure the global loguru handler. Idempotent — safe to call twice."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    def format_with_path(record: Any) -> str:
        record["extra"]["path"] = os.path.relpath(record["file"].path, os.getcwd())
        return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{extra[path]}:{line}</cyan> <magenta>{function}()</magenta> | <lvl>{message}</lvl>\n{exception}"

    logger.remove()  # drop the default stderr handler
    logger.add(
        sys.stderr,
        level=level,
        format=format_with_path,
        backtrace=True,
        diagnose=True,
    )
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            level=level,
            format=format_with_path,
            rotation="10 MB",
            retention="7 days",
        )
