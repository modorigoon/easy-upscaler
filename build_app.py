#!/usr/bin/env python3
"""
Build Easy Upscaler as a macOS .app bundle using PyInstaller
"""

import subprocess
import sys


def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Easy Upscaler",
        "--windowed",
        "--onedir",
        "--icon", "logo.png",
        "--add-data", "logo.png:.",
        "--noconfirm",
        "--clean",
        "main.py",
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("\nBuild complete! App is at: dist/Easy Upscaler.app")


if __name__ == "__main__":
    main()
