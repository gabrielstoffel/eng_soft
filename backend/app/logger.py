import json
import logging


class Logger:
    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)

    def _log(self, level: int, event_kind: str, data: dict) -> None:
        self._logger.log(level, json.dumps({"event_kind": event_kind, "data": data}))

    def debug(self, event_kind: str, data: dict = {}) -> None:
        self._log(logging.DEBUG, event_kind, data)

    def info(self, event_kind: str, data: dict = {}) -> None:
        self._log(logging.INFO, event_kind, data)

    def warn(self, event_kind: str, data: dict = {}) -> None:
        self._log(logging.WARNING, event_kind, data)

    def error(self, event_kind: str, data: dict = {}) -> None:
        self._log(logging.ERROR, event_kind, data)


def get_logger(name: str) -> Logger:
    return Logger(name)
