"""
Batch image upscale processor
QThread-based async processing (single + bulk)
"""

import tempfile
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageOps
from PySide6.QtCore import QThread, Signal

from .upscaler import ImageUpscaler, UpscaleMethod

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


class UpscaleWorker(QThread):
    """Upscale worker thread"""

    progress = Signal(int, int)  # (current index, total count)
    file_started = Signal(str)  # filename
    file_finished = Signal(str, bool)  # (filename, success)
    all_finished = Signal(int, int)  # (succeeded, failed)
    error = Signal(str)
    log_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_files: List[Path] = []
        self._output_dir: Optional[Path] = None
        self._scale: int = 2
        self._method: UpscaleMethod = "auto"
        self._output_format: str = "png"
        self._cancelled = False

    def setup(
        self,
        input_files: List[Path],
        output_dir: Path,
        scale: int = 2,
        method: UpscaleMethod = "auto",
        output_format: str = "png",
    ) -> None:
        """Set processing parameters"""
        self._input_files = input_files
        self._output_dir = output_dir
        self._scale = scale
        self._method = method
        self._output_format = output_format
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel processing"""
        self._cancelled = True

    def _log(self, message: str) -> None:
        self.log_message.emit(message)

    def run(self) -> None:
        if not self._input_files or not self._output_dir:
            self.error.emit("Input files or output path not set.")
            return

        self._output_dir.mkdir(parents=True, exist_ok=True)

        upscaler = ImageUpscaler(log_callback=self._log)
        total = len(self._input_files)
        success_count = 0
        fail_count = 0

        self._log(f"Upscale started: {total} files, {self._scale}x, {self._method}")

        for idx, input_path in enumerate(self._input_files):
            if self._cancelled:
                self._log("Cancelled by user")
                break

            file_name = input_path.name
            self.file_started.emit(file_name)
            self.progress.emit(idx, total)

            try:
                image = Image.open(input_path)
                image = ImageOps.exif_transpose(image)

                # Temp files for Real-ESRGAN
                temp_input = None
                temp_output = None
                if self._method in ("auto", "realesrgan"):
                    temp_dir = Path(tempfile.gettempdir())
                    temp_input = temp_dir / "upscale_input.png"
                    temp_output = temp_dir / "upscale_output.png"

                result = upscaler.upscale(
                    image,
                    scale=self._scale,
                    method=self._method,
                    temp_input_path=temp_input,
                    temp_output_path=temp_output,
                )

                # Generate output filename
                out_name = f"{input_path.stem}_x{self._scale}.{self._output_format}"
                out_path = self._output_dir / out_name

                # Save
                if self._output_format in ("jpg", "jpeg"):
                    if result.mode == "RGBA":
                        rgb = Image.new("RGB", result.size, (255, 255, 255))
                        rgb.paste(result, mask=result.split()[3])
                        rgb.save(out_path, "JPEG", quality=95)
                    else:
                        result.save(out_path, "JPEG", quality=95)
                elif self._output_format == "webp":
                    result.save(out_path, "WebP", quality=95)
                else:
                    result.save(out_path, "PNG")

                success_count += 1
                self.file_finished.emit(file_name, True)
                self._log(f"  Done: {out_name}")

            except Exception as e:
                fail_count += 1
                self.file_finished.emit(file_name, False)
                self._log(f"  Failed: {file_name} - {e}")

        self.progress.emit(total, total)
        self.all_finished.emit(success_count, fail_count)
        self._log(f"Completed: {success_count} succeeded, {fail_count} failed")


def collect_image_files(directory: Path) -> List[Path]:
    """Collect image files from directory (sorted)"""
    files = []
    for f in sorted(directory.iterdir()):
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            files.append(f)
    return files
