"""
Configuration management module
"""

import json
from pathlib import Path
from typing import Any, Dict

from PySide6.QtCore import QStandardPaths


class AppConfig:
    """Application configuration manager"""

    DEFAULT_CONFIG = {
        "upscale_scale": 2,
        "upscale_method": "auto",
        "output_format": "png",
        "last_input_dir": "",
        "last_output_dir": "",
    }

    def __init__(self):
        self._config_dir = Path(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        ) / "easy-upscaler"
        self._config_file = self._config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        self._config = self.DEFAULT_CONFIG.copy()
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    self._config.update(saved_config)
            except Exception:
                pass

    def save(self) -> None:
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @property
    def upscale_scale(self) -> int:
        return self._config.get("upscale_scale", 2)

    @upscale_scale.setter
    def upscale_scale(self, value: int) -> None:
        self._config["upscale_scale"] = value

    @property
    def upscale_method(self) -> str:
        return self._config.get("upscale_method", "auto")

    @upscale_method.setter
    def upscale_method(self, value: str) -> None:
        self._config["upscale_method"] = value

    @property
    def output_format(self) -> str:
        return self._config.get("output_format", "png")

    @output_format.setter
    def output_format(self, value: str) -> None:
        self._config["output_format"] = value

    @property
    def last_input_dir(self) -> str:
        return self._config.get("last_input_dir", "")

    @last_input_dir.setter
    def last_input_dir(self, value: str) -> None:
        self._config["last_input_dir"] = value

    @property
    def last_output_dir(self) -> str:
        return self._config.get("last_output_dir", "")

    @last_output_dir.setter
    def last_output_dir(self, value: str) -> None:
        self._config["last_output_dir"] = value
