"""
Image upscaler module
Supports PIL Lanczos, Enhanced, OpenCV, Real-ESRGAN NCNN
"""

import subprocess
from pathlib import Path
from typing import Callable, Literal, Optional

import cv2
import numpy as np
from PIL import Image, ImageFilter


UpscaleMethod = Literal["auto", "lanczos", "enhanced", "opencv", "realesrgan"]


class ImageUpscaler:
    """Image upscaler class"""

    METHODS = ["auto", "lanczos", "enhanced", "opencv", "realesrgan"]
    SCALES = [2, 4]

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback or print

    def _log(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(message)

    def check_realesrgan_ncnn(self) -> Optional[str]:
        """Check for Real-ESRGAN NCNN executable"""
        script_dir = Path(__file__).parent.resolve()

        possible_paths = [
            script_dir / "bin" / "realesrgan-ncnn-vulkan",
            Path("./realesrgan-ncnn-vulkan"),
            Path("./bin/realesrgan-ncnn-vulkan"),
            Path("/usr/local/bin/realesrgan-ncnn-vulkan"),
            Path("/opt/homebrew/bin/realesrgan-ncnn-vulkan"),
        ]

        for p in possible_paths:
            if p.exists():
                return str(p)

        try:
            result = subprocess.run(
                ["which", "realesrgan-ncnn-vulkan"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return None

    def upscale_lanczos(self, img: Image.Image, scale: int) -> Image.Image:
        """PIL Lanczos upscale"""
        new_size = (img.size[0] * scale, img.size[1] * scale)
        return img.resize(new_size, Image.LANCZOS)

    def upscale_enhanced(self, img: Image.Image, scale: int) -> Image.Image:
        """Enhanced upscale (Lanczos + sharpening)"""
        new_size = (img.size[0] * scale, img.size[1] * scale)

        if img.mode == "RGBA":
            rgb = img.convert("RGB")
            alpha = img.split()[3]

            rgb_up = rgb.resize(new_size, Image.LANCZOS)
            rgb_up = rgb_up.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))

            alpha_up = alpha.resize(new_size, Image.LANCZOS)

            result = rgb_up.convert("RGBA")
            result.putalpha(alpha_up)
            return result
        else:
            result = img.resize(new_size, Image.LANCZOS)
            result = result.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))
            return result

    def upscale_opencv_cubic(self, img: Image.Image, scale: int) -> Image.Image:
        """OpenCV Cubic upscale"""
        new_size = (img.size[0] * scale, img.size[1] * scale)

        if img.mode == "RGBA":
            arr = np.array(img)
            result_channels = []
            for i in range(4):
                channel = arr[:, :, i]
                channel_up = cv2.resize(
                    channel,
                    (new_size[0], new_size[1]),
                    interpolation=cv2.INTER_CUBIC
                )
                result_channels.append(channel_up)
            result_arr = np.stack(result_channels, axis=2)
            return Image.fromarray(result_arr, "RGBA")
        else:
            arr = np.array(img.convert("RGB"))
            arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            result_bgr = cv2.resize(
                arr_bgr,
                (new_size[0], new_size[1]),
                interpolation=cv2.INTER_CUBIC
            )
            result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)

    def upscale_realesrgan_ncnn(
        self,
        input_path: Path,
        output_path: Path,
        scale: int,
        model: str = "realesrgan-x4plus"
    ) -> bool:
        """Upscale with Real-ESRGAN NCNN"""
        exe = self.check_realesrgan_ncnn()
        if not exe:
            return False

        exe_path = Path(exe)
        model_path = exe_path.parent / "models"

        cmd = [
            exe,
            "-i", str(input_path),
            "-o", str(output_path),
            "-s", "4",
            "-n", model,
            "-m", str(model_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self._log(f"Real-ESRGAN error: {result.stderr}")
                return False

            if scale == 2:
                img = Image.open(output_path)
                original_size = Image.open(input_path).size
                target_size = (original_size[0] * 2, original_size[1] * 2)
                img = img.resize(target_size, Image.LANCZOS)
                img.save(output_path, "PNG")

            return True
        except Exception as e:
            self._log(f"Real-ESRGAN execution failed: {e}")
            return False

    def upscale(
        self,
        image: Image.Image,
        scale: int = 2,
        method: UpscaleMethod = "auto",
        temp_input_path: Optional[Path] = None,
        temp_output_path: Optional[Path] = None,
    ) -> Image.Image:
        """Upscale image"""
        original_size = image.size
        self._log(f"Source: {original_size[0]}x{original_size[1]}, mode: {image.mode}")

        actual_method = method
        if method == "auto":
            if self.check_realesrgan_ncnn() and temp_input_path and temp_output_path:
                actual_method = "realesrgan"
                self._log("Method: Real-ESRGAN NCNN (Best Quality)")
            else:
                actual_method = "enhanced"
                self._log("Method: Enhanced Lanczos")

        if actual_method == "realesrgan" and temp_input_path and temp_output_path:
            image.save(temp_input_path, "PNG")
            success = self.upscale_realesrgan_ncnn(temp_input_path, temp_output_path, scale)
            if success:
                result = Image.open(temp_output_path)
                self._log(f"Result: {result.size[0]}x{result.size[1]}")
                return result
            else:
                self._log("Real-ESRGAN failed, falling back to Enhanced")
                actual_method = "enhanced"

        if actual_method == "lanczos":
            self._log("Method: Lanczos")
            result = self.upscale_lanczos(image, scale)
        elif actual_method == "enhanced":
            self._log("Method: Enhanced (Lanczos + Unsharp)")
            result = self.upscale_enhanced(image, scale)
        elif actual_method == "opencv":
            self._log("Method: OpenCV Cubic")
            result = self.upscale_opencv_cubic(image, scale)
        else:
            result = self.upscale_enhanced(image, scale)

        self._log(f"Result: {result.size[0]}x{result.size[1]}")
        return result
