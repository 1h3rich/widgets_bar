"""Main widget bar window for CachyOS KDE Plasma."""
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QPushButton, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QCursor, QRegion

import collectors
import media_ctrl
from notes_panel import NotesPanel

# ── Palette ───────────────────────────────────────────────────────────────────
BG_COLOR     = QColor(12, 12, 22, 218)
BORDER_COLOR = QColor(255, 255, 255, 22)
ACCENT       = "#9580FF"
TEXT_PRI     = "#E0E0F0"
TEXT_SEC     = "#7070A0"
TEXT_WARN    = "#FF9060"

STYLE_BASE = f"""
    QWidget {{ background: transparent; font-family: 'Noto Sans', 'Cantarell', sans-serif; }}
    QLabel  {{ background: transparent; color: {TEXT_PRI}; }}
"""

RADIUS      = 16
BAR_W       = 920
BAR_H       = 170
MARGIN      = 16
KDE_PANEL_H = 44   # altura aproximada del panel inferior de KDE


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lbl(text="", size=11, color=TEXT_PRI, bold=False):
    lbl = QLabel(text)
    w = "700" if bold else "400"
    lbl.setStyleSheet(f"color: {color}; font-size: {size}px; font-weight: {w};")
    return lbl


def _hdr(title):
    lbl = QLabel(title.upper())
    lbl.setStyleSheet(
        f"color: {TEXT_SEC}; font-size: 8px; font-weight: 700; letter-spacing: 1px;"
    )
    return lbl


def _sep():
    line = QFrame()
    line.setFixedWidth(1)
    line.setStyleSheet("background: rgba(255,255,255,15);")
    line.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    return line


def _pct_color(pct, warn=85, crit=95):
    if pct is None:
        return TEXT_SEC
    if pct >= crit:
        return TEXT_WARN
    if pct >= warn:
        return "#FFD060"
    return TEXT_PRI


def _temp_color(t, warn=80, crit=90):
    if t is None:
        return TEXT_SEC
    if t >= crit:
        return TEXT_WARN
    if t >= warn:
        return "#FFD060"
    return TEXT_PRI


# ── Bloque base ───────────────────────────────────────────────────────────────

class Block(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(10, 7, 10, 7)
        self._vbox.setSpacing(3)
        self._vbox.addWidget(_hdr(title))

    def _row(self):
        h = QHBoxLayout()
        h.setSpacing(5)
        self._vbox.addLayout(h)
        return h


# ── Bloques de datos ──────────────────────────────────────────────────────────

class CpuRamBlock(Block):
    def __init__(self):
        super().__init__("CPU · RAM")
        r1 = self._row()
        self._cpu_val  = _lbl("--", 20, TEXT_PRI, bold=True)
        self._cpu_unit = _lbl("%", 10, TEXT_SEC)
        r1.addWidget(self._cpu_val)
        r1.addWidget(self._cpu_unit)
        r1.addStretch()

        r2 = self._row()
        self._ram_lbl = _lbl("-- / -- GB", 10, TEXT_SEC)
        r2.addWidget(self._ram_lbl)
        self._vbox.addStretch()

    def refresh(self, d):
        cpu = d["cpu_pct"]
        self._cpu_val.setText(f"{cpu:.0f}" if cpu is not None else "--")
        self._cpu_val.setStyleSheet(
            f"color: {_pct_color(cpu)}; font-size: 20px; font-weight: 700;"
        )
        self._ram_lbl.setText(f"RAM {d['ram_used']:.1f} / {d['ram_total']:.0f} GB")
        c = TEXT_WARN if d["ram_pct"] > 90 else TEXT_SEC
        self._ram_lbl.setStyleSheet(f"color: {c}; font-size: 10px;")


class GpuBlock(Block):
    def __init__(self):
        super().__init__("GPU · VRAM")
        r1 = self._row()
        self._gpu_val  = _lbl("--", 20, TEXT_PRI, bold=True)
        self._gpu_unit = _lbl("%", 10, TEXT_SEC)
        r1.addWidget(self._gpu_val)
        r1.addWidget(self._gpu_unit)
        r1.addStretch()

        r2 = self._row()
        self._vram_lbl = _lbl("-- / -- GB", 10, TEXT_SEC)
        r2.addWidget(self._vram_lbl)
        self._vbox.addStretch()

    def refresh(self, d):
        pct = d["gpu_pct"]
        self._gpu_val.setText(f"{pct}" if pct is not None else "--")
        self._gpu_val.setStyleSheet(
            f"color: {_pct_color(pct)}; font-size: 20px; font-weight: 700;"
        )
        if d["vram_used"] is not None:
            self._vram_lbl.setText(f"VRAM {d['vram_used']:.1f} / {d['vram_total']:.0f} GB")
        else:
            self._vram_lbl.setText("VRAM --")


class TempBlock(Block):
    def __init__(self):
        super().__init__("Temperaturas")
        # Una fila con los 3 valores en horizontal
        r = self._row()
        self._labels = {}
        for key, name in (("cpu", "CPU"), ("gpu", "GPU"), ("ssd", "SSD")):
            col = QVBoxLayout()
            col.setSpacing(1)
            val_lbl  = _lbl("--°", 14, TEXT_PRI, bold=True)
            name_lbl = _lbl(name, 8, TEXT_SEC)
            col.addWidget(val_lbl)
            col.addWidget(name_lbl)
            r.addLayout(col)
            if key != "ssd":
                r.addStretch()
            self._labels[key] = val_lbl
        self._vbox.addStretch()

    def refresh(self, d):
        pairs = [
            ("cpu", d["cpu_temp"], 85),
            ("gpu", d["gpu_temp"], 85),
            ("ssd", d["ssd_temp"], 70),
        ]
        for key, val, warn in pairs:
            lbl = self._labels[key]
            color = _temp_color(val, warn=warn)
            text  = f"{val:.0f}°" if val is not None else "--°"
            lbl.setText(text)
            lbl.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 700;")


class DiskBlock(Block):
    def __init__(self):
        super().__init__("Disco")
        r1 = self._row()
        self._val  = _lbl("--", 20, TEXT_PRI, bold=True)
        self._unit = _lbl("%", 10, TEXT_SEC)
        r1.addWidget(self._val)
        r1.addWidget(self._unit)
        r1.addStretch()

        r2 = self._row()
        self._free_lbl = _lbl("-- GB libres", 10, TEXT_SEC)
        r2.addWidget(self._free_lbl)
        self._vbox.addStretch()

    def refresh(self, disks):
        if not disks:
            return
        d = disks[0]
        c = TEXT_WARN if d["pct"] > 90 else _pct_color(d["pct"], warn=80, crit=90)
        self._val.setText(f"{d['pct']:.0f}")
        self._val.setStyleSheet(f"color: {c}; font-size: 20px; font-weight: 700;")
        self._free_lbl.setText(f"{d['free_gb']:.0f} GB libres")


class NetworkBlock(Block):
    def __init__(self):
        super().__init__("Red")
        r1 = self._row()
        self._down = _lbl("↓ --", 12, "#60D0FF", bold=True)
        r1.addWidget(self._down)
        r1.addStretch()

        r2 = self._row()
        self._up = _lbl("↑ --", 12, "#80F090", bold=True)
        r2.addWidget(self._up)
        self._vbox.addStretch()

    def refresh(self, d):
        self._down.setText(f"↓ {collectors.format_speed(d['down'])}")
        self._up.setText(f"↑ {collectors.format_speed(d['up'])}")


class SystemBlock(Block):
    def __init__(self):
        super().__init__("Sistema")
        r1 = self._row()
        self._distro = _lbl("CachyOS", 13, ACCENT, bold=True)
        r1.addWidget(self._distro)
        r1.addStretch()

        r2 = self._row()
        self._kernel = _lbl("--", 9, TEXT_SEC)
        r2.addWidget(self._kernel)

        r3 = self._row()
        self._uptime = _lbl("--", 10, TEXT_PRI)
        r3.addWidget(self._uptime)
        self._vbox.addStretch()

    def refresh(self, d):
        self._kernel.setText(f"Linux {d['kernel']}")
        self._uptime.setText(f"{d['uptime_h']}h {d['uptime_m']:02d}m activo")


class MediaBlock(Block):
    def __init__(self):
        super().__init__("Multimedia")
        r1 = self._row()
        self._title = _lbl("Sin reproducción", 11, TEXT_SEC)
        self._title.setMaximumWidth(200)
        r1.addWidget(self._title)
        r1.addStretch()

        r2 = self._row()
        self._artist = _lbl("", 9, TEXT_SEC)
        self._artist.setMaximumWidth(200)
        r2.addWidget(self._artist)

        r3 = self._row()
        btns = QHBoxLayout()
        btns.setSpacing(5)
        self._prev = self._btn("◀◀", media_ctrl.prev_track)
        self._play = self._btn("▶", media_ctrl.play_pause)
        self._next = self._btn("▶▶", media_ctrl.next_track)
        for b in (self._prev, self._play, self._next):
            btns.addWidget(b)
        btns.addStretch()
        r3.addLayout(btns)
        self._vbox.addStretch()

    def _btn(self, text, cb):
        b = QPushButton(text)
        b.setFixedSize(26, 22)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,14); color: {TEXT_PRI};
                border: 1px solid rgba(255,255,255,22); border-radius: 5px; font-size: 11px;
            }}
            QPushButton:hover   {{ background: rgba(149,128,255,80); }}
            QPushButton:pressed {{ background: rgba(149,128,255,160); }}
        """)
        b.clicked.connect(cb)
        return b

    def refresh(self, d):
        status, title, artist = d["status"], d["title"], d["artist"]
        if status == "none" or not title:
            self._title.setText("Sin reproducción")
            self._title.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
            self._artist.setText("")
            self._play.setText("⏵")
        else:
            MAX = 26
            self._title.setText(title[:MAX] + "…" if len(title) > MAX else title)
            self._title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 600;")
            self._artist.setText(artist[:MAX] + "…" if len(artist) > MAX else artist)
            self._play.setText("⏸" if status == "playing" else "▶")


class NotesButton(QWidget):
    def __init__(self, panel, bar, parent=None):
        super().__init__(parent)
        self._panel = panel
        self._bar   = bar
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 7, 12, 7)
        v.setSpacing(4)
        v.addWidget(_hdr("Notas"))
        btn = QPushButton("📝")
        btn.setFixedSize(36, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,12); color: {TEXT_PRI};
                border: 1px solid rgba(255,255,255,20); border-radius: 8px; font-size: 15px;
            }}
            QPushButton:hover   {{ background: rgba(149,128,255,80); }}
            QPushButton:pressed {{ background: rgba(149,128,255,160); }}
        """)
        btn.clicked.connect(lambda: self._panel.toggle(self._bar.geometry()))
        v.addWidget(btn)
        v.addStretch()


# ── Ventana principal ─────────────────────────────────────────────────────────

TRIGGER_ABOVE = 80   # px por encima de la barra que activan el despliegue
HIDE_DELAY    = 1500 # ms de espera antes de ocultar


class WidgetBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLE_BASE)
        self._notes    = NotesPanel()
        self._expanded = False

        self._setup_window()
        self._setup_ui()
        self._position_bar()
        self._setup_animation()
        self._setup_timers()
        self._enable_blur()

        self.setWindowOpacity(0.0)
        self.show()

    # ── Ventana ────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setWindowTitle("widgets_bar")

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        outer.addWidget(container)

        main = QHBoxLayout(container)
        main.setContentsMargins(8, 0, 0, 0)
        main.setSpacing(0)

        inner = QWidget()
        inner.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        rows = QVBoxLayout(inner)
        rows.setContentsMargins(0, 0, 0, 0)
        rows.setSpacing(0)

        # Fila 1: CPU | GPU | Temps | Disco
        r1 = QHBoxLayout()
        r1.setSpacing(0)
        self._cpu  = CpuRamBlock()
        self._gpu  = GpuBlock()
        self._temp = TempBlock()
        self._disk = DiskBlock()
        for i, b in enumerate([self._cpu, self._gpu, self._temp, self._disk]):
            r1.addWidget(b)
            if i < 3:
                r1.addWidget(_sep())

        # Fila 2: Red | Sistema | Multimedia | Notas
        r2 = QHBoxLayout()
        r2.setSpacing(0)
        self._net       = NetworkBlock()
        self._sys       = SystemBlock()
        self._media     = MediaBlock()
        self._notes_btn = NotesButton(self._notes, self)
        for i, b in enumerate([self._net, self._sys, self._media]):
            r2.addWidget(b)
            r2.addWidget(_sep())
        r2.addWidget(self._notes_btn)

        hline = QFrame()
        hline.setFixedHeight(1)
        hline.setStyleSheet("background: rgba(255,255,255,12);")

        rows.addLayout(r1)
        rows.addWidget(hline)
        rows.addLayout(r2)

        main.addWidget(inner)

    # ── Posición ───────────────────────────────────────────────────────────────

    def _position_bar(self):
        geo = QApplication.primaryScreen().geometry()
        x = MARGIN
        y = geo.height() - BAR_H - KDE_PANEL_H - MARGIN
        self.setFixedSize(BAR_W, BAR_H)
        self.move(x, y)

    # ── Animación opacidad ─────────────────────────────────────────────────────

    # Fracción revelada (0..1) de la barra, de abajo hacia arriba.
    # Se anima vía setMask() en vez de move()/resize(): tocar la geometría
    # real de la ventana en KDE Wayland hacía que la barra "se hiciera más
    # pequeña" al interferir con el panel (ver notas del proyecto).
    def _get_reveal(self):
        return self._reveal_val

    def _set_reveal(self, v):
        self._reveal_val = v
        h = max(0, min(BAR_H, round(BAR_H * v)))
        if h >= BAR_H:
            self.clearMask()
        else:
            self.setMask(QRegion(0, BAR_H - h, BAR_W, h))

    reveal = pyqtProperty(float, _get_reveal, _set_reveal)

    def _setup_animation(self):
        self._reveal_val = 0.0
        self._set_reveal(0.0)

        self._anim_opacity = QPropertyAnimation(self, b"windowOpacity")
        self._anim_reveal  = QPropertyAnimation(self, b"reveal")
        self._anim_opacity.setDuration(240)
        self._anim_reveal.setDuration(240)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_bar)

        self._mouse_poll = QTimer(self)
        self._mouse_poll.timeout.connect(self._check_mouse)
        self._mouse_poll.start(50)

    def _check_mouse(self):
        mx, my = QCursor.pos().x(), QCursor.pos().y()
        bar = self.geometry()

        # Zona activa: la barra + TRIGGER_ABOVE px por encima + KDE_PANEL_H por debajo
        zone_x = bar.x() - 20
        zone_y = bar.y() - TRIGGER_ABOVE
        zone_w = bar.width() + 40
        zone_h = bar.height() + TRIGGER_ABOVE + KDE_PANEL_H
        in_zone = (zone_x <= mx <= zone_x + zone_w) and (zone_y <= my <= zone_y + zone_h)

        over_notes = self._notes.isVisible() and self._notes.geometry().contains(mx, my)

        if in_zone or over_notes:
            self._hide_timer.stop()
            if not self._expanded:
                self._show_bar()
        elif self._expanded and not self._hide_timer.isActive():
            self._hide_timer.start(HIDE_DELAY)

    def _show_bar(self):
        self._expanded = True
        self._anim_opacity.stop()
        self._anim_reveal.stop()
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_opacity.setStartValue(self.windowOpacity())
        self._anim_opacity.setEndValue(1.0)
        self._anim_reveal.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_reveal.setStartValue(self._reveal_val)
        self._anim_reveal.setEndValue(1.0)
        self._anim_opacity.start()
        self._anim_reveal.start()

    def _hide_bar(self):
        if self._notes.isVisible():
            return
        self._expanded = False
        self._anim_opacity.stop()
        self._anim_reveal.stop()
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_opacity.setStartValue(self.windowOpacity())
        self._anim_opacity.setEndValue(0.0)
        self._anim_reveal.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_reveal.setStartValue(self._reveal_val)
        self._anim_reveal.setEndValue(0.0)
        self._anim_opacity.start()
        self._anim_reveal.start()

    # ── Pintura ────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        r = self.rect().adjusted(0, 0, -1, -1)
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), RADIUS, RADIUS)
        p.fillPath(path, BG_COLOR)
        p.setPen(BORDER_COLOR)
        p.drawPath(path)

    # ── Blur KDE ───────────────────────────────────────────────────────────────

    def _enable_blur(self):
        try:
            wid = int(self.winId())
            subprocess.Popen(
                ["xprop", "-id", str(wid),
                 "-f", "_KDE_NET_WM_BLUR_BEHIND_REGION", "32c",
                 "-set", "_KDE_NET_WM_BLUR_BEHIND_REGION", "0"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    # ── Timers de datos ────────────────────────────────────────────────────────

    def _setup_timers(self):
        self._t_fast = QTimer(self)
        self._t_fast.timeout.connect(self._fast)
        self._t_fast.start(1500)

        self._t_slow = QTimer(self)
        self._t_slow.timeout.connect(self._slow)
        self._t_slow.start(5000)

        self._t_media = QTimer(self)
        self._t_media.timeout.connect(self._refresh_media)
        self._t_media.start(2000)

        self._fast()
        self._slow()
        self._refresh_media()

    def _fast(self):
        self._cpu.refresh(collectors.get_cpu_ram())
        self._gpu.refresh(collectors.get_gpu())
        self._temp.refresh(collectors.get_temps())
        self._net.refresh(collectors.get_network())

    def _slow(self):
        self._disk.refresh(collectors.get_disks())
        self._sys.refresh(collectors.get_system())

    def _refresh_media(self):
        self._media.refresh(media_ctrl.get_media_info())
