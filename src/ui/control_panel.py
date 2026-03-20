"""
Upscale settings control panel
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
)


class ControlPanel(QFrame):
    """Upscale settings panel (single-row layout)"""

    scale_changed = Signal(int)
    method_changed = Signal(str)
    format_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(25)

        # === Scale ===
        layout.addWidget(QLabel("Scale:"))

        self._scale_group = QButtonGroup(self)
        self._scale_2x = QRadioButton("2x")
        self._scale_2x.setChecked(True)
        self._scale_4x = QRadioButton("4x")

        self._scale_group.addButton(self._scale_2x, 2)
        self._scale_group.addButton(self._scale_4x, 4)

        layout.addWidget(self._scale_2x)
        layout.addWidget(self._scale_4x)

        self._scale_group.buttonClicked.connect(self._on_scale_changed)

        layout.addWidget(self._create_separator())

        # === Method ===
        layout.addWidget(QLabel("Method:"))

        self._method_combo = QComboBox()
        self._method_combo.addItems([
            "Auto",
            "Lanczos - Fast, Basic",
            "Enhanced - With Sharpening",
            "OpenCV - Edge Preserving",
            "Real-ESRGAN - AI, Best Quality",
        ])
        self._method_combo.setMinimumWidth(180)
        self._method_combo.currentTextChanged.connect(self._on_method_changed)
        layout.addWidget(self._method_combo)

        layout.addWidget(self._create_separator())

        # === Output Format ===
        layout.addWidget(QLabel("Format:"))

        self._format_combo = QComboBox()
        self._format_combo.addItems(["PNG", "JPEG", "WebP"])
        self._format_combo.setMinimumWidth(80)
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        layout.addWidget(self._format_combo)

        layout.addStretch()

    def _create_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: #505050;")
        return sep

    def _on_scale_changed(self) -> None:
        self.scale_changed.emit(self._scale_group.checkedId())

    def _on_method_changed(self, text: str) -> None:
        self.method_changed.emit(self.get_method())

    def _on_format_changed(self, text: str) -> None:
        self.format_changed.emit(self.get_output_format())

    def get_scale(self) -> int:
        return self._scale_group.checkedId()

    def get_method(self) -> str:
        text = self._method_combo.currentText()
        key = text.split(" - ")[0] if " - " in text else text
        method_map = {
            "Auto": "auto",
            "Lanczos": "lanczos",
            "Enhanced": "enhanced",
            "OpenCV": "opencv",
            "Real-ESRGAN": "realesrgan",
        }
        return method_map.get(key, "auto")

    def get_output_format(self) -> str:
        return self._format_combo.currentText().lower()

    def set_scale(self, scale: int) -> None:
        button = self._scale_group.button(scale)
        if button:
            button.setChecked(True)

    def set_method(self, method: str) -> None:
        method_map = {
            "auto": "Auto",
            "lanczos": "Lanczos - Fast, Basic",
            "enhanced": "Enhanced - With Sharpening",
            "opencv": "OpenCV - Edge Preserving",
            "realesrgan": "Real-ESRGAN - AI, Best Quality",
        }
        text = method_map.get(method, "Auto")
        index = self._method_combo.findText(text)
        if index >= 0:
            self._method_combo.setCurrentIndex(index)

    def set_output_format(self, fmt: str) -> None:
        fmt_map = {"png": "PNG", "jpeg": "JPEG", "jpg": "JPEG", "webp": "WebP"}
        text = fmt_map.get(fmt, "PNG")
        index = self._format_combo.findText(text)
        if index >= 0:
            self._format_combo.setCurrentIndex(index)
