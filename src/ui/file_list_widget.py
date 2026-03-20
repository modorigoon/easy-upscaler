"""
File list widget with thumbnail preview and status marking
"""

from pathlib import Path
from typing import Dict, List

from PIL import Image
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QImage, QPixmap, QColor, QPainter, QBrush, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

THUMB_SIZE = 48


class FileItemWidget(QWidget):
    """File list item widget (thumbnail + file info + status)"""

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self._file_path = file_path
        self._status = "pending"  # pending, processing, done, failed

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 10, 4)
        layout.setSpacing(10)

        # Thumbnail
        self._thumb_label = QLabel()
        self._thumb_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
        """)
        self._load_thumbnail(file_path)
        layout.addWidget(self._thumb_label)

        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self._name_label = QLabel(file_path.name)
        self._name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #e0e0e0;")
        info_layout.addWidget(self._name_label)

        # Image dimensions + file size
        detail = self._get_file_details(file_path)
        self._detail_label = QLabel(detail)
        self._detail_label.setStyleSheet("font-size: 11px; color: #888;")
        info_layout.addWidget(self._detail_label)

        layout.addLayout(info_layout, stretch=1)

        # Status icon
        self._status_label = QLabel("")
        self._status_label.setFixedWidth(28)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self._status_label)

    def _load_thumbnail(self, file_path: Path) -> None:
        """Load thumbnail"""
        try:
            img = Image.open(file_path)
            img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)

            if img.mode == "RGBA":
                data = img.tobytes("raw", "RGBA")
                qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
            else:
                img = img.convert("RGB")
                data = img.tobytes("raw", "RGB")
                qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGB888)

            pixmap = QPixmap.fromImage(qimg)
            self._thumb_label.setPixmap(
                pixmap.scaled(
                    THUMB_SIZE, THUMB_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        except Exception:
            self._thumb_label.setText("?")
            self._thumb_label.setStyleSheet(
                self._thumb_label.styleSheet() + "color: #666; font-size: 18px;"
            )

    def _get_file_details(self, file_path: Path) -> str:
        """File detail info string"""
        parts = []
        try:
            img = Image.open(file_path)
            parts.append(f"{img.size[0]}x{img.size[1]}")
        except Exception:
            pass

        try:
            size_bytes = file_path.stat().st_size
            if size_bytes < 1024:
                parts.append(f"{size_bytes}B")
            elif size_bytes < 1024 * 1024:
                parts.append(f"{size_bytes / 1024:.1f}KB")
            else:
                parts.append(f"{size_bytes / (1024 * 1024):.1f}MB")
        except Exception:
            pass

        return "  ·  ".join(parts) if parts else file_path.suffix.upper()

    def set_status(self, status: str) -> None:
        """Update status: pending, processing, done, failed"""
        self._status = status
        status_map = {
            "pending": ("", ""),
            "processing": ("⏳", "color: #e8a317;"),
            "done": ("✅", ""),
            "failed": ("❌", ""),
        }
        icon, style = status_map.get(status, ("", ""))
        self._status_label.setText(icon)
        if style:
            self._status_label.setStyleSheet(f"font-size: 16px; {style}")

        # Change name color on done/failed
        if status == "done":
            self._name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #4ec9b0;")
        elif status == "failed":
            self._name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #f44747;")
        elif status == "processing":
            self._name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #dcdcaa;")
        else:
            self._name_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #e0e0e0;")

    @property
    def file_path(self) -> Path:
        return self._file_path


class FileListWidget(QWidget):
    """Thumbnail file list widget"""

    file_count_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: Dict[str, FileItemWidget] = {}  # filename -> widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._list_widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #2a2a2a;
                padding: 0px;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        layout.addWidget(self._list_widget)

    def add_files(self, paths: List[Path]) -> int:
        """Add files, return count of added"""
        added = 0
        for p in paths:
            key = p.as_posix()
            if key not in self._items:
                item_widget = FileItemWidget(p)
                list_item = QListWidgetItem(self._list_widget)
                list_item.setSizeHint(QSize(0, THUMB_SIZE + 12))
                self._list_widget.setItemWidget(list_item, item_widget)
                self._items[key] = item_widget
                added += 1

        if added:
            self.file_count_changed.emit(len(self._items))
        return added

    def set_files(self, paths: List[Path]) -> None:
        """Replace file list"""
        self.clear()
        self.add_files(paths)

    def clear(self) -> None:
        """Clear list"""
        self._list_widget.clear()
        self._items.clear()
        self.file_count_changed.emit(0)

    def get_file_paths(self) -> List[Path]:
        """Get current file paths"""
        return [w.file_path for w in self._items.values()]

    def set_file_status(self, filename: str, status: str) -> None:
        """Update file status (matched by filename)"""
        for key, widget in self._items.items():
            if widget.file_path.name == filename:
                widget.set_status(status)
                # Scroll to processing item
                if status == "processing":
                    for i in range(self._list_widget.count()):
                        item = self._list_widget.item(i)
                        if self._list_widget.itemWidget(item) is widget:
                            self._list_widget.scrollToItem(item)
                            break
                break

    def reset_all_status(self) -> None:
        """Reset all status"""
        for widget in self._items.values():
            widget.set_status("pending")

    def count(self) -> int:
        return len(self._items)
