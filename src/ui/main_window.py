"""
Main window module
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QGuiApplication, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.batch_processor import UpscaleWorker, collect_image_files
from ..utils.config import AppConfig
from ..utils.logger import get_logger
from .control_panel import ControlPanel
from .file_list_widget import FileListWidget
from .log_panel import LogPanel


class MainWindow(QMainWindow):
    """Main window"""

    def __init__(self):
        super().__init__()
        self._config = AppConfig()
        self._logger = get_logger()
        self._worker: Optional[UpscaleWorker] = None

        self._setup_ui()
        self._setup_shortcuts()
        self._load_config()
        self._show_welcome()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Easy Upscaler")
        self.setAcceptDrops(True)

        screen = QGuiApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        self.setMinimumSize(800, 600)

        initial_width = min(1200, screen_size.width() - 20)
        initial_height = min(800, screen_size.height() - 80)
        self.resize(initial_width, initial_height)

        icon_path = Path(__file__).parent.parent.parent / "logo.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === Input ===
        input_btn_layout = QHBoxLayout()

        self._add_files_btn = QPushButton("📄 Add Files")
        self._add_files_btn.setObjectName("toolbarButton")
        self._add_files_btn.clicked.connect(self._add_files)
        input_btn_layout.addWidget(self._add_files_btn)

        self._add_folder_btn = QPushButton("📁 Add Folder")
        self._add_folder_btn.setObjectName("toolbarButton")
        self._add_folder_btn.clicked.connect(self._add_folder)
        input_btn_layout.addWidget(self._add_folder_btn)

        self._clear_btn = QPushButton("✕ Clear")
        self._clear_btn.setObjectName("toolbarButton")
        self._clear_btn.clicked.connect(self._clear_files)
        input_btn_layout.addWidget(self._clear_btn)

        input_btn_layout.addStretch()

        self._file_count_label = QLabel("0 files")
        self._file_count_label.setStyleSheet("color: #888;")
        input_btn_layout.addWidget(self._file_count_label)

        main_layout.addLayout(input_btn_layout)

        # File list
        self._file_list = FileListWidget()
        self._file_list.file_count_changed.connect(
            lambda n: self._file_count_label.setText(f"{n} files")
        )
        main_layout.addWidget(self._file_list, stretch=1)

        # === Output path ===
        output_frame = QFrame()
        output_frame.setObjectName("buttonGroup")
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(10, 8, 10, 8)

        output_layout.addWidget(QLabel("Output:"))

        self._output_dir_edit = QLineEdit()
        self._output_dir_edit.setPlaceholderText("Select output folder for upscaled images")
        self._output_dir_edit.setReadOnly(True)
        self._output_dir_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 10px;
            }
        """)
        output_layout.addWidget(self._output_dir_edit)

        self._browse_output_btn = QPushButton("Browse")
        self._browse_output_btn.setObjectName("toolbarButton")
        self._browse_output_btn.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self._browse_output_btn)

        main_layout.addWidget(output_frame)

        # === Control panel ===
        self._control_panel = ControlPanel()
        self._control_panel.setMaximumHeight(60)
        main_layout.addWidget(self._control_panel)

        # === Action buttons ===
        action_layout = QHBoxLayout()

        self._start_btn = QPushButton("🚀 Start Upscale")
        self._start_btn.setObjectName("toolbarButtonPrimary")
        self._start_btn.setMinimumHeight(40)
        self._start_btn.clicked.connect(self._start_upscale)
        action_layout.addWidget(self._start_btn)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("toolbarButton")
        self._cancel_btn.setMinimumHeight(40)
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._cancel_upscale)
        action_layout.addWidget(self._cancel_btn)

        main_layout.addLayout(action_layout)

        # === Progress ===
        self._progress_label = QLabel("")
        self._progress_label.setStyleSheet("color: #888;")
        self._progress_label.setVisible(False)
        main_layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumHeight(20)
        main_layout.addWidget(self._progress_bar)

        # === Log panel ===
        self._log_panel = LogPanel()
        self._log_panel.setMinimumHeight(120)
        self._log_panel.setMaximumHeight(180)
        main_layout.addWidget(self._log_panel)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence.StandardKey.Open, self, self._add_files)

    def _load_config(self) -> None:
        self._control_panel.set_scale(self._config.upscale_scale)
        self._control_panel.set_method(self._config.upscale_method)
        self._control_panel.set_output_format(self._config.output_format)

        if self._config.last_output_dir:
            self._output_dir_edit.setText(self._config.last_output_dir)

    def _save_config(self) -> None:
        self._config.upscale_scale = self._control_panel.get_scale()
        self._config.upscale_method = self._control_panel.get_method()
        self._config.output_format = self._control_panel.get_output_format()
        self._config.last_output_dir = self._output_dir_edit.text()
        self._config.save()

    def _show_welcome(self) -> None:
        self._logger.emitter.log_signal.connect(self._log_panel.append_log)
        self._logger.info("━" * 50)
        self._logger.info("Easy Upscaler")
        self._logger.info("━" * 50)
        self._logger.info("Add files or folders, or drag & drop to get started")
        self._logger.info("━" * 50)

    # === Drag & drop ===

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        paths = [Path(url.toLocalFile()) for url in urls]

        files = [p for p in paths if p.is_file()]
        dirs = [p for p in paths if p.is_dir()]

        if files:
            added = self._file_list.add_files(files)
            if added:
                self._logger.info(f"{added} files added ({self._file_list.count()} total)")

        for d in dirs:
            dir_files = collect_image_files(d)
            added = self._file_list.add_files(dir_files)
            if added:
                self._logger.info(f"Folder [{d.name}] {added} files added")

    # === Add files/folders ===

    def _add_files(self) -> None:
        start_dir = self._config.last_input_dir or str(Path.home())
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            start_dir,
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.tiff)",
        )
        if file_paths:
            self._config.last_input_dir = str(Path(file_paths[0]).parent)
            paths = [Path(p) for p in file_paths]
            added = self._file_list.add_files(paths)
            if added:
                self._logger.info(f"{added} files added ({self._file_list.count()} total)")

    def _add_folder(self) -> None:
        start_dir = self._config.last_input_dir or str(Path.home())
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder", start_dir)
        if dir_path:
            d = Path(dir_path)
            self._config.last_input_dir = str(d)
            files = collect_image_files(d)
            added = self._file_list.add_files(files)
            self._logger.info(f"Folder [{d.name}] {added} files added ({self._file_list.count()} total)")

            # Auto-suggest output folder
            if not self._output_dir_edit.text():
                suggested = d.parent / f"{d.name}_upscaled"
                self._output_dir_edit.setText(str(suggested))

    def _clear_files(self) -> None:
        self._file_list.clear()

    # === Output folder ===

    def _browse_output_dir(self) -> None:
        start_dir = self._output_dir_edit.text() or self._config.last_output_dir or str(Path.home())
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Folder", start_dir)
        if dir_path:
            self._output_dir_edit.setText(dir_path)

    # === Upscale execution ===

    def _start_upscale(self) -> None:
        files = self._file_list.get_file_paths()
        if not files:
            QMessageBox.warning(self, "Notice", "No image files to process.")
            return

        output_dir = self._output_dir_edit.text()
        if not output_dir:
            QMessageBox.warning(self, "Notice", "Please select an output folder.")
            return

        output_path = Path(output_dir)
        self._save_config()

        # Reset status
        self._file_list.reset_all_status()

        # UI transition
        self._start_btn.setVisible(False)
        self._cancel_btn.setVisible(True)
        self._progress_bar.setVisible(True)
        self._progress_label.setVisible(True)
        self._progress_bar.setMaximum(len(files))
        self._progress_bar.setValue(0)
        self._set_inputs_enabled(False)

        # Start worker
        self._worker = UpscaleWorker()
        self._worker.setup(
            input_files=files,
            output_dir=output_path,
            scale=self._control_panel.get_scale(),
            method=self._control_panel.get_method(),
            output_format=self._control_panel.get_output_format(),
        )

        self._worker.progress.connect(self._on_progress)
        self._worker.file_started.connect(self._on_file_started)
        self._worker.file_finished.connect(self._on_file_finished)
        self._worker.all_finished.connect(self._on_all_finished)
        self._worker.error.connect(self._on_error)
        self._worker.log_message.connect(self._logger.info)

        self._worker.start()

    def _cancel_upscale(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._logger.warning("Cancelling...")

    def _set_inputs_enabled(self, enabled: bool) -> None:
        self._add_files_btn.setEnabled(enabled)
        self._add_folder_btn.setEnabled(enabled)
        self._clear_btn.setEnabled(enabled)
        self._browse_output_btn.setEnabled(enabled)
        self._control_panel.setEnabled(enabled)

    def _on_progress(self, current: int, total: int) -> None:
        self._progress_bar.setValue(current)
        self._progress_label.setText(f"{current}/{total}")

    def _on_file_started(self, name: str) -> None:
        self._progress_label.setText(f"Processing: {name}")
        self._file_list.set_file_status(name, "processing")

    def _on_file_finished(self, name: str, success: bool) -> None:
        self._file_list.set_file_status(name, "done" if success else "failed")

    def _on_all_finished(self, success: int, fail: int) -> None:
        self._start_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setVisible(False)
        self._progress_label.setVisible(False)
        self._set_inputs_enabled(True)

        if fail == 0:
            self._logger.success(f"Done: {success} succeeded")
        else:
            self._logger.warning(f"Done: {success} succeeded, {fail} failed")

        self._logger.info(f"Output: {self._output_dir_edit.text()}")

    def _on_error(self, message: str) -> None:
        self._start_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._progress_bar.setVisible(False)
        self._progress_label.setVisible(False)
        self._set_inputs_enabled(True)
        self._logger.error(message)
        QMessageBox.warning(self, "Error", message)

    def closeEvent(self, event) -> None:
        self._save_config()
        super().closeEvent(event)
