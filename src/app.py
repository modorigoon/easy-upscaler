"""
Application setup module
"""

import platform
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def _set_macos_app_name(name: str) -> None:
    """Set macOS menu bar application name"""
    if platform.system() != "Darwin":
        return
    try:
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if info:
            info["CFBundleName"] = name
    except ImportError:
        pass


def create_app() -> QApplication:
    """Create and configure QApplication"""
    _set_macos_app_name("Easy Upscaler")

    app = QApplication([])
    app.setApplicationName("Easy Upscaler")
    app.setOrganizationName("CodeIslet")

    icon_path = Path(__file__).parent.parent / "logo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #2d2d2d;
            color: #d4d4d4;
            font-size: 13px;
        }

        QTabWidget::pane {
            border: 1px solid #404040;
            border-radius: 4px;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #333333;
            color: #d4d4d4;
            padding: 8px 20px;
            border: 1px solid #404040;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2d2d2d;
            border-bottom: 2px solid #0e639c;
        }
        QTabBar::tab:hover:!selected {
            background-color: #3c3c3c;
        }

        QFrame#buttonGroup {
            background-color: #333333;
            border: 1px solid #404040;
            border-radius: 6px;
        }

        QPushButton#toolbarButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #505050;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }
        QPushButton#toolbarButton:hover {
            background-color: #505050;
            border-color: #606060;
        }
        QPushButton#toolbarButton:pressed {
            background-color: #383838;
        }
        QPushButton#toolbarButton:disabled {
            background-color: #2d2d2d;
            color: #666666;
            border-color: #3c3c3c;
        }

        QPushButton#toolbarButtonPrimary {
            background-color: #0e639c;
            color: #ffffff;
            border: 1px solid #1177bb;
            padding: 8px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton#toolbarButtonPrimary:hover {
            background-color: #1177bb;
            border-color: #2299dd;
        }
        QPushButton#toolbarButtonPrimary:pressed {
            background-color: #0d5a8c;
        }
        QPushButton#toolbarButtonPrimary:disabled {
            background-color: #2d4a5c;
            color: #666666;
            border-color: #3c5a6c;
        }

        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1177bb;
        }
        QPushButton:pressed {
            background-color: #0d5a8c;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }

        QRadioButton {
            spacing: 5px;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }

        QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #404040;
            border-radius: 3px;
            padding: 3px 10px;
            min-width: 80px;
        }
        QComboBox:hover {
            border-color: #0e639c;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            border: 1px solid #404040;
            selection-background-color: #0e639c;
        }

        QProgressBar {
            border: 1px solid #404040;
            border-radius: 3px;
            text-align: center;
            background-color: #1e1e1e;
        }
        QProgressBar::chunk {
            background-color: #0e639c;
        }

        QLabel {
            background-color: transparent;
        }
    """)

    window = MainWindow()
    window.show()

    app._main_window = window

    return app
