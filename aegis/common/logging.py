from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class _Logger:
    def __init__(self, name: str):
        self.name = str(name)

    def _emit(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        if args:
            try:
                message = message % args
            except Exception:
                message = " ".join([message, *[str(a) for a in args]])
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.name,
            "message": str(message),
        }
        if kwargs:
            payload["fields"] = kwargs
        print(payload)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._emit("DEBUG", message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._emit("INFO", message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._emit("WARNING", message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._emit("ERROR", message, *args, **kwargs)


_LOGGERS: dict[str, _Logger] = {}


def get_logger(name: str) -> _Logger:
    key = str(name)
    if key not in _LOGGERS:
        _LOGGERS[key] = _Logger(key)
    return _LOGGERS[key]