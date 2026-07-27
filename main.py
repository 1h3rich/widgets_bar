#!/usr/bin/env python3
"""CachyOS Widget Bar — launcher."""
import sys
import psutil  # pre-warm cpu_percent baseline
psutil.cpu_percent(interval=None)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from bar import WidgetBar


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CachyOS Widget Bar")

    bar = WidgetBar()
    bar.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
