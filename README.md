# Easy Upscaler

<p align="center">
  <img src="logo.png" width="128" height="128" alt="Easy Upscaler">
</p>

A desktop image upscaler with single file and batch processing support. Built with PySide6.

## Features

- **Single & Batch Processing** — Add individual files or entire folders
- **Drag & Drop** — Drop files or folders directly into the app
- **Multiple Upscale Methods** — Lanczos, Enhanced (with sharpening), OpenCV Cubic, Real-ESRGAN NCNN
- **Scale Options** — 2x / 4x
- **Output Formats** — PNG, JPEG, WebP
- **Thumbnail Preview** — File list with thumbnails, dimensions, and file size
- **Real-time Status** — Per-file progress tracking with status markers
- **Cancellable** — Stop batch processing at any time

## Supported Input Formats

PNG, JPEG, WebP, BMP, TIFF

## Requirements

- Python 3.10+
- macOS / Windows / Linux

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Build Standalone App (macOS)

```bash
pip install pyinstaller
python build_app.py
```

The app bundle will be created at `dist/Easy Upscaler.app`.

## License

MIT
