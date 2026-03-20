#!/usr/bin/env python3
"""
Easy Upscaler - 이미지 업스케일러
PySide6 기반 데스크톱 애플리케이션
"""

import sys
from src.app import create_app


def main():
    app = create_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
