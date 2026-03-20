"""
Logging system module
"""

import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QObject, Signal


class LogEmitter(QObject):
    """Log message signal emitter"""
    log_signal = Signal(str)


class QTextEditHandler(logging.Handler):
    """Log handler that emits to QTextEdit"""

    def __init__(self, emitter: LogEmitter):
        super().__init__()
        self.emitter = emitter
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.emitter.log_signal.emit(f"[{timestamp}] {msg}")


class AppLogger:
    """Application logger"""

    _instance: Optional["AppLogger"] = None
    _emitter: Optional[LogEmitter] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._emitter = LogEmitter()
        self._logger = logging.getLogger("easy_upscaler")
        self._logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
        )
        self._logger.addHandler(console_handler)

        qt_handler = QTextEditHandler(self._emitter)
        self._logger.addHandler(qt_handler)

    @property
    def emitter(self) -> LogEmitter:
        return self._emitter

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(f"⚠️ {message}")

    def error(self, message: str) -> None:
        self._logger.error(f"❌ {message}")

    def success(self, message: str) -> None:
        self._logger.info(f"✅ {message}")


def get_logger() -> AppLogger:
    return AppLogger()
