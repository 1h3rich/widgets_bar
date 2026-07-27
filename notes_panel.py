"""Floating notes panel anchored above the widget bar."""
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont

NOTES_FILE = os.path.join(os.path.dirname(__file__), "data", "notes.txt")


class NotesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(360, 200)
        self._setup_ui()
        self._load()

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save)
        self._editor.textChanged.connect(self._on_text_changed)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        lbl = QLabel("Notas rápidas")
        lbl.setStyleSheet("color: #8888AA; font-size: 10px; font-weight: 600; background: transparent;")
        layout.addWidget(lbl)

        self._editor = QPlainTextEdit()
        self._editor.setStyleSheet("""
            QPlainTextEdit {
                background: transparent;
                color: #E0E0F0;
                font-size: 12px;
                font-family: 'Noto Sans', 'Segoe UI', sans-serif;
                border: none;
                selection-background-color: rgba(150, 130, 255, 100);
            }
        """)
        self._editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self._editor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = self.rect().adjusted(0, 0, -1, -1)
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 14, 14)
        painter.fillPath(path, QColor(14, 14, 24, 220))
        painter.setPen(QColor(255, 255, 255, 22))
        painter.drawPath(path)

    def _on_text_changed(self):
        self._save_timer.start(800)

    def _save(self):
        os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            f.write(self._editor.toPlainText())

    def _load(self):
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                self._editor.setPlainText(f.read())

    def position_above(self, bar_geometry):
        x = bar_geometry.x()
        y = bar_geometry.y() - self.height() - 8
        self.move(x, y)

    def toggle(self, bar_geometry):
        if self.isVisible():
            self.hide()
        else:
            self.position_above(bar_geometry)
            self.show()
            self._editor.setFocus()
