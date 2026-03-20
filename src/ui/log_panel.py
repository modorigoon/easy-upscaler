"""
Log panel module
"""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogPanel(QFrame):
    """Log display panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2d2d2d;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 2, 5, 2)

        title_label = QLabel("Log")
        title_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(clear_btn)

        layout.addWidget(header_widget)

        # Log text area
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                border: none;
            }
        """)
        layout.addWidget(self._text_edit)

    def append_log(self, message: str) -> None:
        self._text_edit.append(message)
        scrollbar = self._text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self) -> None:
        self._text_edit.clear()
