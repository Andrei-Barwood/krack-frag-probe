"""Structured logging: human-readable console + optional JSON lines.

Author: Kirtan Teg Singh (ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any, TextIO


class JsonLineFormatter(logging.Formatter):
    """Emit one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        for key in ("test", "verdict", "bssid", "iface", "event"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, default=str)


def setup_logging(
    *,
    verbose: bool = False,
    json_mode: bool = False,
    no_color: bool = False,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Configure root package logger and return it.

    Parameters
    ----------
    verbose:
        DEBUG if True else INFO.
    json_mode:
        If True, emit JSON lines instead of plain text.
    no_color:
        Reserved for callers that disable Rich; plain handler ignores color.
    stream:
        Output stream (default stderr).
    """
    del no_color  # Console color handled by Rich in CLI; keep API stable.
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("krack_frag_probe")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setLevel(level)
    if json_mode:
        handler.setFormatter(JsonLineFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%H:%M:%S")
        )
    logger.addHandler(handler)
    return logger


def log_event(
    logger: logging.Logger,
    message: str,
    *,
    level: int = logging.INFO,
    **extra: Any,
) -> None:
    """Log with structured extras (visible in JSON formatter)."""
    logger.log(level, message, extra=extra)
