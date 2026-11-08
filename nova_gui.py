import sys
import threading
import os
import math
import random
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QSizePolicy,
    QScrollArea
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect,
    QThread, Signal, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QConicalGradient, QPainterPath
)

from nova_voice import speak
from listen import listen
from nova_brain import get_response, get_stream_response, set_ai_model
from memory_manager import get_stats, show_notification
import gui_controller


# ======================
# JARVIS COLOR PALETTE
# ======================

BG_DARK = QColor(5, 10, 20)
PANEL = QColor(10, 20, 38, 220)
ACCENT = QColor(0, 255, 255)
ACCENT_DIM = QColor(0, 136, 170)
TEXT = QColor(232, 237, 245)
TEXT_DIM = QColor(168, 179, 207)
SUCCESS = QColor(0, 255, 157)
THINKING = QColor(241, 196, 15)
SPEAKING = QColor(155, 89, 182)
OFFLINE = QColor(231, 76, 60)
ONLINE = QColor(0, 255, 157)


# ======================
# BACKEND BRIDGE
# ======================

class NovaWorker(QThread):
    """Background thread for AI streaming responses."""
    chunk_received = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        try:
            full_reply = ""
            for chunk in get_stream_response(self.text):
                full_reply += chunk
                self.chunk_received.emit(chunk)
            self.finished.emit(full_reply)
        except Exception as exc:
            self.error.emit(str(exc))


# ======================
# REALISTIC 3D LAPTOP HOLOGRAM (Center)
# ======================

class LaptopHologram(QWidget):
    """Realistic 3D laptop hologram like Jarvis armor display."""

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._angle = 0
        self._tilt = 20
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def _animate(self):
        self._angle = (self._angle + 2.5) % 360
        self.update()

    def _project3d(self, x, y, z, cx, cy, scale=1.0, focal=500):
        """3D projection with perspective."""
        rad_y = math.radians(self._angle)
        rad_x = math.radians(self._tilt)

        # Rotate around Y
        x1 = x * math.cos(rad_y) - z * math.sin(rad_y)
        z1 = x * math.sin(rad_y) + z * math.cos(rad_y)

        # Rotate around X (tilt)
        y1 = y * math.cos(rad_x) - z1 * math.sin(rad_x)
        z2 = y * math.sin(rad_x) + z1 * math.cos(rad_x)

        f = focal / (focal + z2)
        return int(cx + x1 * f * scale), int(cy - y1 * f * scale)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        holo = QColor(0, 255, 255, 200)
        holo_dim = QColor(0, 255, 255, 70)
        screen_bright = QColor(0, 255, 255, 60)

        painter.setPen(QPen(holo, 2))
        painter.setBrush(Qt.NoBrush)

        # Laptop dimensions
        lap_w = 200
        lap_d = 130
        screen_h = 125
        keyboard_h = 40
        base_thick = 16

        # ===== BASE (keyboard body) =====
        # Top face of base
        pts = [
            self._project3d(-lap_w/2, -keyboard_h/2, lap_d/2, cx, cy),
            self._project3d(lap_w/2, -keyboard_h/2, lap_d/2, cx, cy),
            self._project3d(lap_w/2, -keyboard_h/2, -lap_d/2, cx, cy),
            self._project3d(-lap_w/2, -keyboard_h/2, -lap_d/2, cx, cy),
        ]
        path = QPainterPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.closeSubpath()
        painter.setPen(QPen(holo_dim, 1))
        painter.setBrush(QBrush(QColor(0, 255, 255, 20)))
        painter.drawPath(path)

        # Front face thickness
        pts = [
            self._project3d(-lap_w/2, -keyboard_h/2, -lap_d/2, cx, cy),
            self._project3d(lap_w/2, -keyboard_h/2, -lap_d/2, cx, cy),
            self._project3d(lap_w/2, -keyboard_h/2 + base_thick, -lap_d/2, cx, cy),
            self._project3d(-lap_w/2, -keyboard_h/2 + base_thick, -lap_d/2, cx, cy),
        ]
        path = QPainterPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.closeSubpath()
        painter.setPen(QPen(holo, 1))
        painter.setBrush(QBrush(QColor(0, 255, 255, 35)))
        painter.drawPath(path)

        # Keyboard keys grid
        painter.setPen(QPen(holo, 1.5))
        for row in range(5):
            for col in range(8):
                kx = -lap_w/2 + 14 + col * 23
                ky = -keyboard_h/2 + 5 + row * 7
                if kx < lap_w/2 - 10:
                    kx_s, ky_s = self._project3d(kx, ky, lap_d/2 + 1, cx, cy)
                    painter.drawRect(kx_s - 3, ky_s - 3, 6, 6)

        # Trackpad
        tp_x, tp_y = self._project3d(-35, -keyboard_h/2 + 28, lap_d/2 + 1.1, cx, cy)
        painter.setPen(QPen(holo_dim, 1))
        painter.drawRect(tp_x - 16, tp_y - 9, 32, 18)

        # ===== SCREEN =====
        screen_top_y = -keyboard_h/2 - screen_h

        # Back thickness of screen
        pts = [
            self._project3d(-lap_w/2, screen_top_y, lap_d/2, cx, cy),
            self._project3d(lap_w/2, screen_top_y, lap_d/2, cx, cy),
            self._project3d(lap_w/2, screen_top_y, lap_d/2 + base_thick, cx, cy),
            self._project3d(-lap_w/2, screen_top_y, lap_d/2 + base_thick, cx, cy),
        ]
        path = QPainterPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.closeSubpath()
        painter.setPen(QPen(holo_dim, 1))
        painter.setBrush(QBrush(QColor(0, 255, 255, 15)))
        painter.drawPath(path)

        # Screen face (glowing display)
        pts = [
            self._project3d(-lap_w/2, screen_top_y, lap_d/2, cx, cy),
            self._project3d(lap_w/2, screen_top_y, lap_d/2, cx, cy),
            self._project3d(lap_w/2, screen_top_y + screen_h, lap_d/2, cx, cy),
            self._project3d(-lap_w/2, screen_top_y + screen_h, lap_d/2, cx, cy),
        ]
        path = QPainterPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.closeSubpath()
        grad = QLinearGradient(
            pts[0][0], pts[0][1], pts[2][0], pts[2][1]
        )
        grad.setColorAt(0, QColor(0, 255, 255, 35))
        grad.setColorAt(0.5, QColor(0, 150, 200, 15))
        grad.setColorAt(1, QColor(0, 255, 255, 35))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(holo, 2))
        painter.drawPath(path)

        # NOVA text on screen
        painter.setPen(QPen(ACCENT, 1))
        painter.setFont(QFont("Consolas", 12, QFont.Bold))
        tx, ty = self._project3d(-30, screen_top_y + 35, lap_d/2 + 1.1, cx, cy)
        painter.drawText(tx, ty, "NOVA")
        painter.setFont(QFont("Consolas", 9))
        tx, ty = self._project3d(-30, screen_top_y + 50, lap_d/2 + 1.1, cx, cy)
        painter.drawText(tx, ty, "SYSTEM ONLINE")

        # Screen scan line
        scan_y = screen_top_y + (self._angle % screen_h)
        sx1, sy1 = self._project3d(-lap_w/2, scan_y, lap_d/2 + 1.1, cx, cy)
        sx2, sy2 = self._project3d(lap_w/2, scan_y, lap_d/2 + 1.1, cx, cy)
        painter.setPen(QPen(QColor(0, 255, 255, 120), 1))
        painter.drawLine(sx1, sy1, sx2, sy2)

        # ===== HINGE =====
        hinge_y = screen_top_y
        hx1, hy1 = self._project3d(-lap_w/2, hinge_y, lap_d/2, cx, cy)
        hx2, hy2 = self._project3d(lap_w/2, hinge_y, lap_d/2, cx, cy)
        painter.setPen(QPen(holo, 1.5))
        painter.drawLine(hx1, hy1, hx2, hy2)

        # ===== Orbit ring around laptop =====
        self._orbit_angle = (getattr(self, '_orbit_angle', 0) + 2.5) % 360
        ring_r = max(lap_w, screen_h) * 0.7
        painter.setPen(QPen(QColor(0, 255, 255, 85), 1))
        for i in range(14):
            ang = self._orbit_angle + i * (360/14)
            px = cx + int(ring_r * math.cos(math.radians(ang)) * 0.9)
            py = cy + int(ring_r * 0.4 * math.sin(math.radians(ang)))
            painter.drawEllipse(px - 2, py - 2, 4, 4)

        # Floating particles around laptop
        painter.setPen(QPen(QColor(0, 255, 255, 120), 2))
        for i in range(10):
            ang = self._angle + i * 36
            dist = 135 + 15 * math.sin(math.radians(self._angle + i * 50))
            px = cx + int(dist * math.cos(math.radians(ang)) * 0.85)
            py = cy + int(dist * 0.35 * math.sin(math.radians(ang)))
            painter.drawEllipse(px - 2, py - 2, 4, 4)


# ======================
# SUN-LIKE REACTOR CORE (Right Side Top)
# ======================

class ReactorCore(QWidget):
    """Sun-like reactor: bright center, smooth continuous orbits, roaming particles."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(240, 240)
        self._angle = 0.0
        self._pulse = 0.0
        self._mode = "online"
        self._particles = []
        random.seed(42)
        for _ in range(28):
            self._particles.append({
                'angle': random.random() * 360,
                'dist': random.uniform(45, 95),
                'speed': random.uniform(0.8, 2.2),
                'tilt': random.uniform(-35, 35),
                'size': random.uniform(1.5, 3.5),
            })
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(20)  # Smooth 50fps

    def set_mode(self, mode: str):
        self._mode = mode
        self.update()

    def _animate(self):
        self._angle = (self._angle + 1.5) % 360  # Smooth slow rotation
        self._pulse = (self._pulse + 0.08) % (math.pi * 2)
        for p in self._particles:
            p['angle'] = (p['angle'] + p['speed']) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2

        mode_colors = {
            "online": ONLINE,
            "listening": ACCENT,
            "thinking": THINKING,
            "speaking": SPEAKING,
            "offline": OFFLINE,
        }
        color = mode_colors.get(self._mode, ACCENT)

        # --- Smooth continuous orbit rings (3D ellipses) ---
        ring_configs = [
            (85, 0, 1.0),
            (68, 28, 0.85),
            (102, -22, 0.7),
            (74, 45, 0.6),
        ]
        for ring_r, tilt_base, thickness in ring_configs:
            tilt_rad = math.radians(tilt_base + self._angle * 0.3)
            painter.setPen(QPen(color, 1))
            painter.setBrush(Qt.NoBrush)
            points = []
            for i in range(0, 360, 5):
                ang = math.radians(i)
                x = ring_r * math.cos(ang)
                y = ring_r * math.sin(ang) * math.cos(tilt_rad)
                z = ring_r * math.sin(ang) * math.sin(tilt_rad)
                f = 1.0 / (1.0 + z / 250.0)
                px = cx + int(x * f)
                py = cy + int(y * f * 0.55)
                points.append((px, py))
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

        # --- Roaming particles (smooth, no cutting) ---
        painter.setPen(Qt.NoPen)
        for p in self._particles:
            tilt_rad = math.radians(p['tilt'])
            ang = math.radians(p['angle'])
            x = p['dist'] * math.cos(ang)
            y = p['dist'] * math.sin(ang) * math.cos(tilt_rad)
            z = p['dist'] * math.sin(ang) * math.sin(tilt_rad)
            f = 1.0 / (1.0 + z / 200.0)
            px = cx + int(x * f)
            py = cy + int(y * f * 0.6)
            alpha = int(100 + 120 * math.sin(self._pulse + p['angle'] * 0.5))
            pcolor = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setBrush(QBrush(pcolor))
            painter.drawEllipse(px - p['size'], py - p['size'], p['size'] * 2, p['size'] * 2)

        # --- Sun center (bright pulsing) ---
        inner_r = int(26 + 10 * abs(math.sin(self._pulse * 2)))
        for i in range(6):
            glow_r = inner_r + i * 7
            alpha = int(50 * (1 - i * 0.14)) + int(35 * abs(math.sin(self._pulse)))
            glow = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2)

        grad = QRadialGradient(cx, cy, inner_r)
        grad.setColorAt(0, QColor(255, 255, 255, 255))
        grad.setColorAt(0.35, QColor(color.red(), color.green(), color.blue(), 230))
        grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 50))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)

        # Center spark
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 2, cy - 2, 4, 4)


# ======================
# INDIVIDUAL STAT HOLOGRAM (Right Side)
# ======================

class StatHoloWidget(QFrame):
    """Individual stat with moving 3D hologram icon."""

    def __init__(self, name, icon_type, color, unit=""):
        super().__init__()
        self.name = name
        self.icon_type = icon_type
        self.color = color
        self.unit = unit
        self._angle = 0
        self._value = "--"
        self._subvalue = ""
        self.setFixedSize(130, 105)
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 140);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 10px;
            }
        """)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(35)

    def set_value(self, value: str, sub: str = ""):
        self._value = value
        self._subvalue = sub

    def _animate(self):
        self._angle = (self._angle + 2) % 360
        self.update()

    def _project3d(self, x, y, z, cx, cy, scale=1.0, focal=250):
        rad_y = math.radians(self._angle)
        x1 = x * math.cos(rad_y) - z * math.sin(rad_y)
        z1 = x * math.sin(rad_y) + z * math.cos(rad_y)
        f = focal / (focal + z1)
        return int(cx + x1 * f * scale), int(cy - y * f * scale)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = 40, h // 2 - 8
        c = self.color

        if self.icon_type == "cpu":
            # Processor chip hologram
            painter.setPen(QPen(c, 2))
            painter.setBrush(Qt.NoBrush)
            cw, ch = 30, 30
            pts = [
                self._project3d(-cw/2, -ch/2, 0, cx, cy),
                self._project3d(cw/2, -ch/2, 0, cx, cy),
                self._project3d(cw/2, ch/2, 0, cx, cy),
                self._project3d(-cw/2, ch/2, 0, cx, cy),
            ]
            path = QPainterPath()
            path.moveTo(*pts[0])
            for p in pts[1:]:
                path.lineTo(*p)
            path.closeSubpath()
            painter.drawPath(path)
            # Corner pins
            painter.setPen(QPen(c, 1.5))
            for i in range(8):
                ang = self._angle + i * 45
                px = cx + int(18 * math.cos(math.radians(ang)))
                py = cy + int(18 * math.sin(math.radians(ang)) * 0.6)
                painter.drawPoint(px, py)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(cx - 2, cy - 2, 4, 4)

        elif self.icon_type == "ram":
            # Memory stick hologram
            painter.setPen(QPen(c, 2))
            painter.setBrush(Qt.NoBrush)
            for offset in (-10, 10):
                bx = cx + offset
                pts = [
                    self._project3d(-7, -20, 0, bx, cy),
                    self._project3d(7, -20, 0, bx, cy),
                    self._project3d(7, 20, 0, bx, cy),
                    self._project3d(-7, 20, 0, bx, cy),
                ]
                path = QPainterPath()
                path.moveTo(*pts[0])
                for p in pts[1:]:
                    path.lineTo(*p)
                path.closeSubpath()
                painter.drawPath(path)
                for seg in range(4):
                    sy = -20 + seg * 10
                    sx1, sy1 = self._project3d(-7, sy, 0, bx, cy)
                    sx2, sy2 = self._project3d(7, sy, 0, bx, cy)
                    painter.drawLine(sx1, sy1, sx2, sy2)

        elif self.icon_type == "bat":
            # Battery hologram
            painter.setPen(QPen(c, 2))
            painter.setBrush(Qt.NoBrush)
            bw, bh = 22, 28
            pts = [
                self._project3d(-bw/2, -bh/2, 0, cx, cy),
                self._project3d(bw/2, -bh/2, 0, cx, cy),
                self._project3d(bw/2, bh/2, 0, cx, cy),
                self._project3d(-bw/2, bh/2, 0, cx, cy),
            ]
            path = QPainterPath()
            path.moveTo(*pts[0])
            for p in pts[1:]:
                path.lineTo(*p)
            path.closeSubpath()
            painter.drawPath(path)
            tip = [
                self._project3d(bw/2, -5, 0, cx, cy),
                self._project3d(bw/2 + 5, 0, 0, cx, cy),
                self._project3d(bw/2, 5, 0, cx, cy),
            ]
            tpath = QPainterPath()
            tpath.moveTo(*tip[0])
            for p in tip[1:]:
                tpath.lineTo(*p)
            tpath.closeSubpath()
            painter.drawPath(tpath)
            try:
                fill_val = float(self._value.replace(self.unit, '').replace('%', ''))
            except Exception:
                fill_val = 50.0
            fill = max(0.0, min(1.0, fill_val / 100.0))
            painter.setBrush(QBrush(QColor(c.red(), c.green(), c.blue(), 100)))
            painter.drawRect(cx - bw/2 + 2, cy - bh/2 + 2, int((bw - 4) * fill), bh - 4)

        elif self.icon_type == "clock":
            # Clock/calendar hologram for time & date
            painter.setPen(QPen(c, 2))
            painter.setBrush(Qt.NoBrush)
            cr = 16
            painter.drawEllipse(cx - cr, cy - cr, cr * 2, cr * 2)
            now = datetime.now()
            sec_ang = now.second * 6
            min_ang = now.minute * 6 + now.second * 0.1
            hr_ang = (now.hour % 12) * 30 + now.minute * 0.5
            for ang, length in ((sec_ang, 12), (min_ang, 10), (hr_ang, 7)):
                hx = cx + int(length * math.cos(math.radians(ang - 90)))
                hy = cy + int(length * math.sin(math.radians(ang - 90)) * 0.7)
                painter.drawLine(cx, cy, hx, hy)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(cx - 2, cy - 2, 4, 4)

        # Value text on right
        painter.setPen(QPen(c, 1))
        painter.setFont(QFont("Consolas", 13, QFont.Bold))
        painter.drawText(90, cy + 6, self._value)
        if self._subvalue:
            painter.setPen(QPen(TEXT_DIM, 1))
            painter.setFont(QFont("Consolas", 9))
            painter.drawText(90, cy + 20, self._subvalue)
        painter.setPen(QPen(TEXT_DIM, 1))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(90, cy + 32, self.name)


# ======================
# TIME/DATE/WEATHER HOLOGRAM
# ======================

class TimeDateWeatherWidget(QFrame):
    """Time, date, and weather with a shared hologram clock."""

    def __init__(self):
        super().__init__()
        self._angle = 0
        self._time_str = "--:--"
        self._date_str = "-- -- ----"
        self._weather_str = "--°C"
        self.setFixedSize(260, 110)
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 140);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 10px;
            }
        """)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(35)

    def _animate(self):
        self._angle = (self._angle + 2) % 360
        self.update()

    def set_data(self, time_str, date_str, weather_str):
        self._time_str = time_str
        self._date_str = date_str
        self._weather_str = weather_str
        self.update()

    def _project3d(self, x, y, z, cx, cy, scale=1.0, focal=250):
        rad_y = math.radians(self._angle)
        x1 = x * math.cos(rad_y) - z * math.sin(rad_y)
        z1 = x * math.sin(rad_y) + z * math.cos(rad_y)
        f = focal / (focal + z1)
        return int(cx + x1 * f * scale), int(cy - y * f * scale)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = 50, h // 2
        c = ACCENT

        # Clock hologram on left
        painter.setPen(QPen(c, 2))
        painter.setBrush(Qt.NoBrush)
        cr = 20
        painter.drawEllipse(cx - cr, cy - cr, cr * 2, cr * 2)
        now = datetime.now()
        sec_ang = now.second * 6
        min_ang = now.minute * 6 + now.second * 0.1
        hr_ang = (now.hour % 12) * 30 + now.minute * 0.5
        for ang, length in ((sec_ang, 16), (min_ang, 13), (hr_ang, 9)):
            hx = cx + int(length * math.cos(math.radians(ang - 90)))
            hy = cy + int(length * math.sin(math.radians(ang - 90)) * 0.7)
            painter.drawLine(cx, cy, hx, hy)
        painter.setBrush(QBrush(c))
        painter.drawEllipse(cx - 2, cy - 2, 4, 4)

        # Orbit dots around clock
        painter.setPen(QPen(c, 1.5))
        for i in range(12):
            ang = self._angle + i * 30
            px = cx + int(26 * math.cos(math.radians(ang)))
            py = cy + int(26 * math.sin(math.radians(ang)) * 0.6)
            painter.drawEllipse(px - 1.5, py - 1.5, 3, 3)

        # Text on right
        painter.setPen(QPen(c, 1))
        painter.setFont(QFont("Consolas", 15, QFont.Bold))
        painter.drawText(100, cy + 8, self._time_str)

        painter.setPen(QPen(TEXT_DIM, 1))
        painter.setFont(QFont("Consolas", 10))
        painter.drawText(100, cy + 26, self._date_str)
        painter.drawText(100, cy + 44, self._weather_str)


# ======================
# CHAT BUBBLE (Floating)
# ======================

class ChatBubble(QFrame):
    """A floating chat message bubble that fades in and drifts away."""

    def __init__(self, text: str, is_user: bool = False, ttl_ms: int = 9000):
        super().__init__()
        self.is_user = is_user
        self.ttl_ms = ttl_ms
        self._setup_ui(text)
        self._start_floating_animation()

    def _setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(650)
        self.label.setFont(QFont("Consolas", 12))
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 157, 80),
                        stop:1 rgba(0, 200, 120, 60));
                    border: 1px solid rgba(0, 255, 157, 120);
                    border-radius: 16px;
                    color: #000000;
                }
            """)
            self.label.setStyleSheet("color: #000000; font-size: 13px; font-weight: 600;")
            layout.addStretch()
            layout.addWidget(self.label, 0)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(10, 20, 38, 200);
                    border: 1px solid rgba(0, 255, 255, 60);
                    border-radius: 16px;
                    color: #e8edf5;
                }
            """)
            self.label.setStyleSheet("color: #e8edf5; font-size: 13px;")
            layout.addWidget(self.label, 0)
            layout.addStretch()

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.setWindowOpacity(0.0)

    def _start_floating_animation(self):
        self._fade_in = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_in.setDuration(600)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        self._float_up = QPropertyAnimation(self, b"pos", self)
        self._float_up.setDuration(700)
        self._float_up.setStartValue(self.pos() + QPoint(0, 12))
        self._float_up.setEndValue(self.pos())
        self._float_up.setEasingCurve(QEasingCurve.OutCubic)

        self._group = QParallelAnimationGroup(self)
        self._group.addAnimation(self._fade_in)
        self._group.addAnimation(self._float_up)
        self._group.start()

        QTimer.singleShot(self.ttl_ms, self._fade_out_and_remove)

    def _fade_out_and_remove(self):
        self._fade_out = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_out.setDuration(800)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)

        self._drift = QPropertyAnimation(self, b"pos", self)
        self._drift.setDuration(900)
        self._drift.setStartValue(self.pos())
        self._drift.setEndValue(self.pos() + QPoint(0, -20))
        self._drift.setEasingCurve(QEasingCurve.InCubic)

        self._out_group = QParallelAnimationGroup(self)
        self._out_group.addAnimation(self._fade_out)
        self._out_group.addAnimation(self._drift)
        self._out_group.finished.connect(self._remove_self)
        self._out_group.start()

    def _remove_self(self):
        parent_layout = self.parentWidget().layout() if self.parentWidget() else None
        if parent_layout:
            parent_layout.removeWidget(self)
        self.deleteLater()


# ======================
# TYPING INDICATOR
# ======================

class TypingIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)

        self.label = QLabel("NOVA is processing")
        self.label.setStyleSheet("color: #00ffff; font-size: 11px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(self.label)
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._state = 0
        self.hide()

    def start(self):
        self._timer.start(300)
        self.show()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _animate(self):
        states = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"]
        self.label.setText(f"NOVA is processing {states[self._state % len(states)]}")
        self._state += 1


# ======================
# MAIN JARVIS WINDOW
# ======================

class JarvisWindow(QMainWindow):
    """NOVA — Jarvis-style AI Operating Companion."""

    def __init__(self):
        super().__init__()

        gui_controller.GUI_ROOT = self

        self.setWindowTitle("NOVA — JARVIS Interface")
        self.resize(1600, 900)
        self.setMinimumSize(1300, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.nova_running = False
        self.current_ai_model = "qwen3:1.8b"
        self._worker = None
        self._current_nova_bubble = None
        self._current_nova_text = ""
        self._drag_pos = None
        self.chat_visible = False

        self._build_ui()
        self._start_timers()
        self._register_hotkey()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.central = QWidget()
        self.central.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCentralWidget(self.central)

        main = QVBoxLayout(self.central)
        main.setContentsMargins(40, 30, 40, 30)
        main.setSpacing(20)

        # HUD Overlay
        self.hud = HUDOverlay(self.central)
        self.hud.setGeometry(0, 0, self.width(), self.height())
        self.hud.raise_()

        # Title Bar
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("◉ NOVA CORE")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffff; letter-spacing: 2px;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.btn_min = QPushButton("─")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("✕")
        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 10);
                    border: 1px solid rgba(255, 255, 255, 30);
                    border-radius: 6px;
                    color: #e8edf5;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(0, 255, 255, 40);
                }
            """)
        self.btn_close.clicked.connect(self.close)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self._toggle_max)
        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_max)
        title_layout.addWidget(self.btn_close)

        main.addWidget(title_bar)

        # Content - Three columns
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground, True)
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(40)

        # Left: Empty spacer
        self.left_spacer = QWidget()
        self.left_spacer.setAttribute(Qt.WA_TranslucentBackground, True)
        self.left_spacer.setMinimumWidth(80)
        content_layout.addWidget(self.left_spacer, 0)

        # Center: Spinning Laptop Hologram
        center_panel = QWidget()
        center_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignCenter)

        self.hologram = LaptopHologram()
        self.hologram.setFixedSize(340, 340)
        center_layout.addWidget(self.hologram)

        # Status below hologram
        self.status_label = QLabel("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.status_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.status_label)

        content_layout.addWidget(center_panel, 1)

        # Right: Core + Stats (inline layout)
        right_panel = QWidget()
        right_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        right_panel.setFixedWidth(300)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        # Reactor Core (sun-like)
        core_container = QWidget()
        core_container.setAttribute(Qt.WA_TranslucentBackground, True)
        core_layout = QHBoxLayout(core_container)
        core_layout.setContentsMargins(0, 0, 0, 0)
        core_layout.setAlignment(Qt.AlignCenter)

        self.core = ReactorCore()
        core_layout.addWidget(self.core)
        right_layout.addWidget(core_container)

        # First row of stats: CPU, RAM, BAT inline
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row1.setAlignment(Qt.AlignCenter)

        self.cpu_stat = StatHoloWidget("CPU", "cpu", QColor(0, 255, 157), "%")
        self.ram_stat = StatHoloWidget("RAM", "ram", QColor(0, 255, 255), "%")
        self.bat_stat = StatHoloWidget("BAT", "bat", QColor(241, 196, 15), "%")

        row1.addWidget(self.cpu_stat, 0, Qt.AlignCenter)
        row1.addWidget(self.ram_stat, 0, Qt.AlignCenter)
        row1.addWidget(self.bat_stat, 0, Qt.AlignCenter)
        right_layout.addLayout(row1)

        # Second row: Time/Date/Weather combined
        self.tdw_widget = TimeDateWeatherWidget()
        right_layout.addWidget(self.tdw_widget, 0, Qt.AlignCenter)

        right_layout.addStretch()
        content_layout.addWidget(right_panel, 0)

        main.addWidget(content, 1)

        # Hidden Chat Panel
        self.chat_panel = QWidget()
        self.chat_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        chat_panel_layout = QVBoxLayout(self.chat_panel)
        chat_panel_layout.setContentsMargins(0, 0, 0, 0)
        chat_panel_layout.setSpacing(10)

        self.chat_frame = GlassPanel()
        chat_layout = QVBoxLayout(self.chat_frame)
        chat_layout.setContentsMargins(20, 15, 20, 15)
        chat_layout.setSpacing(8)

        self.chat_title_lbl = QLabel("SYSTEM TERMINAL")
        self.chat_title_lbl.setStyleSheet("color: #00ffff; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        chat_layout.addWidget(self.chat_title_lbl)

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QFrame.NoFrame)
        self.chat_scroll.setAttribute(Qt.WA_TranslucentBackground, True)
        self.chat_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.chat_container = QWidget()
        self.chat_container.setAttribute(Qt.WA_TranslucentBackground, True)
        self.chat_layout_inner = QVBoxLayout(self.chat_container)
        self.chat_layout_inner.setContentsMargins(0, 0, 0, 0)
        self.chat_layout_inner.setSpacing(10)
        self.chat_layout_inner.addStretch()

        self.chat_scroll.setWidget(self.chat_container)
        chat_layout.addWidget(self.chat_scroll, 1)

        self.typing = TypingIndicator()
        chat_layout.addWidget(self.typing)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 160);
                border: 1px solid rgba(0, 255, 255, 60);
                border-radius: 24px;
            }
        """)
        input_frame.setFixedHeight(56)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 0, 16, 0)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or speak to NOVA...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #e8edf5;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.voice_btn = QPushButton("🎙")
        self.voice_btn.setFixedSize(40, 40)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 30);
                border: 1px solid rgba(0, 255, 255, 80);
                border-radius: 20px;
                color: #00ffff;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 60);
            }
        """)
        self.voice_btn.clicked.connect(self._on_voice)
        input_layout.addWidget(self.voice_btn)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(80, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #0099cc);
                border: none;
                border-radius: 20px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33e0ff, stop:1 #0099cc);
            }
            QPushButton:disabled {
                background: #444444;
                color: #888888;
            }
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_frame)
        chat_panel_layout.addWidget(self.chat_frame)

        # Control buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.start_btn = QPushButton("▶ START")
        self.start_btn.setFixedSize(100, 36)
        self.start_btn.setStyleSheet(self._btn_style("#00ff9d"))
        self.start_btn.clicked.connect(self._start_nova)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setFixedSize(100, 36)
        self.stop_btn.setStyleSheet(self._btn_style("#e74c3c"))
        self.stop_btn.clicked.connect(self._stop_nova)
        btn_row.addWidget(self.stop_btn)

        self.hide_chat_btn = QPushButton("✕ HIDE CHAT")
        self.hide_chat_btn.setFixedSize(110, 36)
        self.hide_chat_btn.setStyleSheet(self._btn_style("#34495e"))
        self.hide_chat_btn.clicked.connect(self._hide_chat)
        btn_row.addWidget(self.hide_chat_btn)

        btn_row.addStretch()
        chat_panel_layout.addLayout(btn_row)

        self.chat_panel.hide()
        main.addWidget(self.chat_panel)

    @staticmethod
    def _btn_style(accent_hex):
        return f"""
            QPushButton {{
                background: {accent_hex};
                border: none;
                border-radius: 10px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.7;
            }}
        """

    # ------------------------------------------------------------------
    # Timers
    # ------------------------------------------------------------------
    def _start_timers(self):
        self.dash_timer = QTimer(self)
        self.dash_timer.timeout.connect(self._update_dashboard)
        self.dash_timer.start(1000)
        self._update_dashboard()

        self.resize_timer = QTimer(self)
        self.resize_timer.timeout.connect(self._resize_hud)
        self.resize_timer.start(100)

    def _resize_hud(self):
        self.hud.setGeometry(0, 0, self.width(), self.height())

    def _update_dashboard(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            try:
                battery = psutil.sensors_battery()
                bat_text = f"{battery.percent}%" if battery else "N/A"
            except Exception:
                bat_text = "N/A"
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%a, %d %b %Y")
            weather_str = "24°C"  # Placeholder - could fetch from API

            self.cpu_stat.set_value(f"{cpu:.0f}%", "%")
            self.ram_stat.set_value(f"{ram:.0f}%", "%")
            self.bat_stat.set_value(bat_text, "%")
            self.tdw_widget.set_data(time_str, date_str, weather_str)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Hotkey: Alt + Space
    # ------------------------------------------------------------------
    def _register_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey("alt+space", lambda: threading.Thread(target=self._hotkey_listen, daemon=True).start())
        except Exception as exc:
            print(f"Hotkey registration failed: {exc}")

    def _hotkey_listen(self):
        self.set_status("listening", "Hotkey activated")
        try:
            text = listen()
        except Exception:
            text = ""
        if not text:
            self.set_status("offline", "No speech detected")
            return
        self._add_user_message(text)
        self.set_status("thinking", "Thinking")
        try:
            response = get_response(text)
        except Exception as exc:
            response = f"Error: {exc}"
        self._add_nova_message(response)
        self.set_status("speaking", "Speaking")
        try:
            speak(response)
        except Exception:
            pass
        self.set_status("listening", "Listening")

    # ------------------------------------------------------------------
    # Window dragging
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # ------------------------------------------------------------------
    # Chat visibility
    # ------------------------------------------------------------------
    def _show_chat(self):
        if not self.chat_visible:
            self.chat_visible = True
            self.chat_panel.show()
            self._add_nova_message("Chat terminal opened.")

    def _hide_chat(self):
        self.chat_visible = False
        self.chat_panel.hide()

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------
    def _add_user_message(self, text: str):
        bubble = ChatBubble(text, is_user=True)
        self.chat_layout_inner.insertWidget(self.chat_layout_inner.count() - 1, bubble)
        QTimer.singleShot(30, self._scroll_to_bottom)

    def _add_nova_message(self, text: str):
        bubble = ChatBubble(text, is_user=False)
        self.chat_layout_inner.insertWidget(self.chat_layout_inner.count() - 1, bubble)
        QTimer.singleShot(30, self._scroll_to_bottom)
        return bubble

    def _start_nova_stream(self):
        self._current_nova_bubble = ChatBubble("", is_user=False)
        self.chat_layout_inner.insertWidget(self.chat_layout_inner.count() - 1, self._current_nova_bubble)
        self._current_nova_text = ""
        self.typing.start()
        QTimer.singleShot(30, self._scroll_to_bottom)

    def _append_nova_stream(self, chunk: str):
        self._current_nova_text += chunk
        self._current_nova_bubble.label.setText(self._current_nova_text)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _finish_nova_stream(self, full_text: str):
        self._current_nova_text = full_text
        self._current_nova_bubble.label.setText(full_text)
        self.typing.stop()
        self._current_nova_bubble = None
        self._current_nova_text = ""
        QTimer.singleShot(30, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        bar = self.chat_scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return

        if text.lower() in ("show chat", "open chat"):
            self._show_chat()
            return

        self.core.set_mode("thinking")
        self.set_status("thinking", f"User: {text}")

        self._show_chat()
        self._add_user_message(text)
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        self._start_nova_stream()

        self._worker = NovaWorker(text)
        self._worker.chunk_received.connect(self._append_nova_stream)
        self._worker.finished.connect(self._on_ai_finished)
        self._worker.error.connect(self._on_ai_error)
        self._worker.start()

    def _on_ai_finished(self, full_text: str):
        self._finish_nova_stream(full_text)
        self.core.set_mode("listening")
        self.set_status("listening", f"NOVA: {full_text}")
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_ai_error(self, error_msg: str):
        self.typing.stop()
        self.core.set_mode("offline")
        self.set_status("offline", f"Error: {error_msg}")
        if self._current_nova_bubble:
            self._current_nova_bubble.label.setText(f"Error: {error_msg}")
            self._current_nova_bubble = None
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_voice(self):
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.core.set_mode("listening")
        self.set_status("listening", "Listening...")
        self._show_chat()

        def _voice_thread():
            try:
                text = listen()
            except Exception:
                text = ""
            if text:
                self.core.set_mode("thinking")
                self._add_user_message(text)
                self._start_nova_stream()
                self._worker = NovaWorker(text)
                self._worker.chunk_received.connect(self._append_nova_stream)
                self._worker.finished.connect(self._on_ai_finished)
                self._worker.error.connect(self._on_ai_error)
                self._worker.start()
            else:
                self.core.set_mode("offline")
                self.set_status("offline", "No speech detected")
                self.send_btn.setEnabled(True)
                self.input_field.setEnabled(True)

        threading.Thread(target=_voice_thread, daemon=True).start()

    def _on_model_change(self, model_name: str):
        self.current_ai_model = model_name
        set_ai_model(model_name)

    def set_status(self, mode: str, message: str = ""):
        colors = {
            "online": (ONLINE, "#00ff9d"),
            "listening": (ACCENT, "#00ffff"),
            "thinking": (THINKING, "#f1c40f"),
            "speaking": (SPEAKING, "#9b59b6"),
            "offline": (OFFLINE, "#e74c3c"),
        }
        color, hex_color = colors.get(mode, (OFFLINE, "#e74c3c"))
        self.status_label.setText(f"● {mode.upper()}")
        self.status_label.setStyleSheet(f"color: {hex_color}; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.core.set_mode(mode)

    # ------------------------------------------------------------------
    # Start / Stop / Voice loop
    # ------------------------------------------------------------------
    def _start_nova(self):
        if self.nova_running:
            self._add_nova_message("Already running.")
            return
        self.nova_running = True
        self._add_nova_message("System activated.")
        show_notification("NOVA", "System activated")
        try:
            speak("Nova is now online")
        except Exception:
            pass
        self.set_status("listening", "System activated")
        threading.Thread(target=self._nova_loop, daemon=True).start()

    def _stop_nova(self):
        self.nova_running = False
        self.set_status("offline", "System stopped")
        self._add_nova_message("System stopped.")
        show_notification("NOVA", "System stopped")

    def _nova_loop(self):
        while self.nova_running:
            self.set_status("listening", "Listening...")
            try:
                text = listen()
            except Exception:
                text = ""
            if not text:
                continue
            self._add_user_message(text)
            self.set_status("thinking", "Thinking")
            response = ""
            try:
                for chunk in get_stream_response(text):
                    response += chunk
            except Exception as exc:
                response = f"Error: {exc}"
            if response == "EXIT_NOVA":
                self._add_nova_message("Shutting down.")
                self.set_status("offline", "Shutting down")
                try:
                    speak("Shutting down")
                except Exception:
                    pass
                QTimer.singleShot(0, self.close)
                break
            self._add_nova_message(response)
            self.set_status("speaking", "Speaking")
            try:
                speak(response)
            except Exception:
                pass
            self.set_status("listening", "Listening")

    # ------------------------------------------------------------------
    # System tray
    # ------------------------------------------------------------------
    def _minimize_to_tray(self):
        try:
            import pystray
            from PIL import Image

            try:
                image = Image.open("nova_icon.ico")
            except Exception:
                image = Image.new("RGB", (64, 64), (0, 255, 255))

            def show_window(icon, item):
                self.showNormal()
                self.raise_()

            def quit_app(icon, item):
                self.nova_running = False
                icon.stop()
                self.close()

            menu = pystray.Menu(
                pystray.MenuItem("Show NOVA", show_window),
                pystray.MenuItem("Start Listening", lambda i, _: self._start_nova()),
                pystray.MenuItem("Stop Listening", lambda i, _: self._stop_nova()),
                pystray.MenuItem("Exit", quit_app),
            )
            icon = pystray.Icon("NOVA", image, "NOVA Assistant", menu)
            self.hide()
            threading.Thread(target=icon.run, daemon=True).start()
        except Exception:
            self.hide()


# ======================
# HUD OVERLAY
# ======================

class HUDOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._offset = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def _animate(self):
        self._offset = (self._offset + 2) % 20
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(0, 255, 255, 15), 1)
        painter.setPen(pen)
        for y in range(0, self.height(), 4):
            painter.drawLine(0, (y + self._offset) % self.height(), self.width(), (y + self._offset) % self.height())

        pen = QPen(QColor(0, 255, 255, 80), 2)
        painter.setPen(pen)
        size = 40
        painter.drawLine(20, 20, 20 + size, 20)
        painter.drawLine(20, 20, 20, 20 + size)
        painter.drawLine(self.width() - 20 - size, 20, self.width() - 20, 20)
        painter.drawLine(self.width() - 20, 20, self.width() - 20, 20 + size)
        painter.drawLine(20, self.height() - 20 - size, 20, self.height() - 20)
        painter.drawLine(20, self.height() - 20, 20 + size, self.height() - 20)
        painter.drawLine(self.width() - 20 - size, self.height() - 20, self.width() - 20, self.height() - 20)
        painter.drawLine(self.width() - 20, self.height() - 20 - size, self.width() - 20, self.height() - 20)


# ======================
# GLASS PANEL
# ======================

class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 180);
                border: 1px solid rgba(0, 255, 255, 40);
                border-radius: 16px;
            }
        """)
        self.setAttribute(Qt.WA_TranslucentBackground, True)


# ======================
# ENTRY POINT
# ======================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    from PySide6.QtGui import QPalette
    palette = QPalette()
    palette.setColor(QPalette.Window, BG_DARK)
    palette.setColor(QPalette.WindowText, TEXT)
    palette.setColor(QPalette.Base, PANEL)
    palette.setColor(QPalette.AlternateBase, BG_DARK)
    palette.setColor(QPalette.Text, TEXT)
    palette.setColor(QPalette.Button, PANEL)
    palette.setColor(QPalette.ButtonText, TEXT)
    app.setPalette(palette)

    window = JarvisWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
