"""
NOVA — Personal AI Operating Companion
JARVIS-style desktop application built with PySide6.
Real desktop app — not a website.
"""

import sys
import os
import threading
import time
import math
import random
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QScrollArea,
    QProgressBar, QGraphicsDropShadowEffect, QSizeGrip
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect,
    QThread, Signal, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QConicalGradient, QPainterPath, QFontDatabase
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
PANEL = QColor(15, 25, 40, 220)
PANEL_LIGHT = QColor(25, 35, 55, 180)
ACCENT = QColor(0, 255, 255)      # Cyan neon
ACCENT_DIM = QColor(0, 150, 200)
TEXT = QColor(230, 240, 255)
TEXT_DIM = QColor(130, 150, 180)
GLOW = QColor(0, 255, 255, 60)
SUCCESS = QColor(0, 255, 157)
THINKING = QColor(241, 196, 15)
SPEAKING = QColor(155, 89, 182)
OFFLINE = QColor(231, 76, 60)
ONLINE = QColor(0, 255, 157)


# ======================
# BACKEND WORKER
# ======================

class NovaWorker(QThread):
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
# ARC REACTOR CORE (Center)
# ======================

class ArcReactorCore(QWidget):
    """Jarvis-style arc reactor in the center."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self._angle = 0.0
        self._pulse = 0.0
        self._mode = "online"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def set_mode(self, mode: str):
        self._mode = mode
        self.update()

    def _animate(self):
        self._angle = (self._angle + 2.5) % 360
        self._pulse = (self._pulse + 0.08) % (math.pi * 2)
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

        # Outer rings
        for i in range(4):
            ring_r = 140 - (i * 25)
            alpha = int(50 * (1 - i * 0.2)) + int(40 * abs(__import__("math").sin(self._pulse)))
            glow = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(QPen(glow, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)

        # Rotating inner ring
        painter.setPen(QPen(color, 3))
        painter.setBrush(Qt.NoBrush)
        for i in range(8):
            ang = self._angle + i * 45
            x1 = cx + int(90 * __import__("math").cos(__import__("math").radians(ang)))
            y1 = cy + int(90 * __import__("math").sin(__import__("math").radians(ang)))
            x2 = cx + int(120 * __import__("math").cos(__import__("math").radians(ang)))
            y2 = cy + int(120 * __import__("math").sin(__import__("math").radians(ang)))
            painter.drawLine(x1, y1, x2, y2)

        # Inner core
        inner_r = int(35 + 10 * abs(__import__("math").sin(self._pulse * 2)))
        grad = QRadialGradient(cx, cy, inner_r)
        grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 255))
        grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 40))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)

        # Center spark
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 3, cy - 3, 6, 6)


# ======================
# HOLOGRAPHIC PANEL
# ======================

class HoloPanel(QFrame):
    """Glassmorphism panel with neon border."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 35, 55, 190),
                    stop:1 rgba(8, 14, 26, 200));
                border: 2px solid rgba(0, 255, 255, 70);
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 255, 255, 60))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(10)
        if title:
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; letter-spacing: 2px; font-family: 'Consolas', monospace;")
            self._layout.addWidget(title_lbl)

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)


# ======================
# STAT ROW
# ======================

class StatRow(QWidget):
    def __init__(self, label: str, color=ACCENT):
        super().__init__()
        self.setFixedHeight(26)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(f"color: #a8b3cf; font-size: 11px; font-family: 'Consolas', monospace;")
        self.lbl.setFixedWidth(65)
        layout.addWidget(self.lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255, 255, 255, 15);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {color.name()};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.bar)

        self.val_lbl = QLabel("0%")
        self.val_lbl.setStyleSheet(f"color: {color.name()}; font-size: 11px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.val_lbl.setFixedWidth(34)
        layout.addWidget(self.val_lbl)

    def set_value(self, pct: int):
        self.bar.setValue(pct)
        self.val_lbl.setText(f"{pct}%")


# ======================
# CHAT BUBBLE
# ======================

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool = False, ttl_ms: int = 9000):
        super().__init__()
        self.is_user = is_user
        self.ttl_ms = ttl_ms
        self._setup_ui(text)
        self._start_floating_animation()

    def _setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(10)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(700)
        self.label.setFont(QFont("Consolas", 13))
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 157, 90),
                        stop:1 rgba(0, 200, 120, 70));
                    border: 1px solid rgba(0, 255, 157, 130);
                    border-radius: 18px;
                    color: #000000;
                }
            """)
            self.label.setStyleSheet("color: #000000; font-size: 14px; font-weight: 600;")
            layout.addStretch()
            layout.addWidget(self.label, 0)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(10, 20, 38, 210);
                    border: 1px solid rgba(0, 255, 255, 70);
                    border-radius: 18px;
                    color: #e6f0ff;
                }
            """)
            self.label.setStyleSheet("color: #e6f0ff; font-size: 14px;")
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
        self._float_up.setStartValue(self.pos() + QPoint(0, 14))
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
        self._drift.setEndValue(self.pos() + QPoint(0, -22))
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
        self.setFixedHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 6, 18, 6)

        self.label = QLabel("NOVA is processing")
        self.label.setStyleSheet("color: #00ffff; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
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
    def __init__(self):
        super().__init__()

        gui_controller.GUI_ROOT = self

        self.setWindowTitle("NOVA — JARVIS Interface")
        self.resize(1600, 900)
        self.setMinimumSize(1400, 800)
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

    def _build_ui(self):
        self.central = QWidget()
        self.central.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCentralWidget(self.central)

        main = QVBoxLayout(self.central)
        main.setContentsMargins(35, 30, 35, 30)
        main.setSpacing(20)

        # Title Bar
        title_bar = QWidget()
        title_bar.setFixedHeight(55)
        title_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("JARVIS")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #00ffff; letter-spacing: 4px; font-family: 'Consolas', monospace;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        time_date = QWidget()
        time_date.setAttribute(Qt.WA_TranslucentBackground, True)
        td_layout = QVBoxLayout(time_date)
        td_layout.setContentsMargins(0, 0, 0, 0)
        td_layout.setSpacing(2)
        td_layout.setAlignment(Qt.AlignRight)

        self.time_label = QLabel("02:43 AM")
        self.time_label.setStyleSheet("color: #e6f0ff; font-size: 22px; font-weight: bold; font-family: 'Consolas', monospace;")
        td_layout.addWidget(self.time_label)

        self.date_label = QLabel("FRIDAY 04 APR 2024")
        self.date_label.setStyleSheet("color: #a8b3cf; font-size: 11px; font-family: 'Consolas', monospace;")
        td_layout.addWidget(self.date_label)

        title_layout.addWidget(time_date)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(34, 34)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 8px;
                color: #e6f0ff;
                font-size: 13px;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 45); }
        """)
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_close)

        main.addWidget(title_bar)

        # Content - Three columns
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground, True)
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(35)

        # Left Panel
        left_panel = QWidget()
        left_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        voice_panel = HoloPanel("VOICE COMMAND")
        voice_inner = QHBoxLayout()
        mic_lbl = QLabel("🎙")
        mic_lbl.setStyleSheet("color: #00ffff; font-size: 16px;")
        voice_inner.addWidget(mic_lbl)
        voice_inner.addStretch()
        status_lbl = QLabel("ACTIVE")
        status_lbl.setStyleSheet("color: #00ff9d; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace;")
        voice_inner.addWidget(status_lbl)
        voice_panel.addWidget(QLabel())  # spacer
        voice_panel.layout().addLayout(voice_inner)
        left_layout.addWidget(voice_panel)

        sys_panel = HoloPanel("SYSTEM SETTINGS")
        self.sys_cpu = StatRow("CPU", QColor(0, 255, 157))
        self.sys_mem = StatRow("Memory", QColor(0, 255, 255))
        self.sys_stor = StatRow("Storage", QColor(241, 196, 15))
        self.sys_net = StatRow("Network", QColor(155, 89, 182))
        sys_panel.addWidget(self.sys_cpu)
        sys_panel.addWidget(self.sys_mem)
        sys_panel.addWidget(self.sys_stor)
        sys_panel.addWidget(self.sys_net)
        left_layout.addWidget(sys_panel)

        env_panel = HoloPanel("ENVIRONMENT")
        env_row = QHBoxLayout()
        self.env_temp = QLabel("--°C")
        self.env_temp.setStyleSheet("color: #00ffff; font-size: 13px; font-family: 'Consolas', monospace;")
        self.env_hum = QLabel("--%")
        self.env_hum.setStyleSheet("color: #a8b3cf; font-size: 13px; font-family: 'Consolas', monospace;")
        env_row.addWidget(self.env_temp)
        env_row.addStretch()
        env_row.addWidget(self.env_hum)
        env_panel.addWidget(QLabel())
        env_panel.layout().addLayout(env_row)
        env_clear = QPushButton("CLEAR")
        env_clear.setFixedSize(72, 26)
        env_clear.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 20);
                border: 1px solid rgba(0, 255, 255, 60);
                border-radius: 4px;
                color: #00ffff;
                font-size: 9px;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 45); }
        """)
        env_panel.addWidget(env_clear)
        left_layout.addWidget(env_panel)

        comm_panel = HoloPanel("COMMUNICATIONS")
        comm_inner = QHBoxLayout()
        comm_inner.setSpacing(8)
        photo_lbl = QLabel("👤")
        photo_lbl.setStyleSheet("font-size: 26px;")
        comm_inner.addWidget(photo_lbl)
        comm_info = QVBoxLayout()
        comm_info.setSpacing(2)
        comm_name = QLabel("FEDER PEDRO")
        comm_name.setStyleSheet("color: #00ffff; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace;")
        comm_online = QLabel("● ONLINE")
        comm_online.setStyleSheet("color: #00ff9d; font-size: 9px; font-family: 'Consolas', monospace;")
        comm_info.addWidget(comm_name)
        comm_info.addWidget(comm_online)
        comm_inner.addLayout(comm_info)
        comm_inner.addStretch()
        call_btn = QPushButton("📞")
        call_btn.setFixedSize(30, 30)
        call_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 20);
                border: 1px solid rgba(0, 255, 255, 55);
                border-radius: 15px;
                color: #00ffff;
                font-size: 14px;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 45); }
        """)
        comm_inner.addWidget(call_btn)
        comm_panel.addWidget(QLabel())
        comm_panel.layout().addLayout(comm_inner)
        left_layout.addWidget(comm_panel)

        left_layout.addStretch()
        content_layout.addWidget(left_panel, 0)

        # Center Panel - Arc Reactor Core
        center_panel = QWidget()
        center_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(15)
        center_layout.setAlignment(Qt.AlignCenter)

        self.core = ArcReactorCore()
        self.core.setFixedSize(320, 320)
        center_layout.addWidget(self.core)

        self.status_label = QLabel("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.status_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.status_label)

        content_layout.addWidget(center_panel, 1)

        # Right Panel
        right_panel = QWidget()
        right_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        right_panel.setFixedWidth(340)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        cpu_panel = HoloPanel("CPU")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setFixedHeight(10)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 12);
                border: none;
                border-radius: 5px;
            }
            QProgressBar::chunk { background: #00ffff; border-radius: 5px; }
        """)
        cpu_panel.addWidget(self.cpu_bar)
        cpu_val = QLabel("70%")
        cpu_val.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        cpu_panel.addWidget(cpu_val)
        right_layout.addWidget(cpu_panel)

        loc_panel = HoloPanel("LOCATION")
        map_lbl = QLabel("🗺")
        map_lbl.setStyleSheet("font-size: 36px; color: rgba(0, 255, 255, 45);")
        map_lbl.setAlignment(Qt.AlignCenter)
        loc_panel.addWidget(map_lbl)
        loc_city = QLabel("NEW YORK, NY")
        loc_city.setStyleSheet("color: #e6f0ff; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        loc_city.setAlignment(Qt.AlignCenter)
        loc_panel.addWidget(loc_city)
        loc_pin = QLabel("📍")
        loc_pin.setStyleSheet("color: #00ffff; font-size: 16px;")
        loc_pin.setAlignment(Qt.AlignCenter)
        loc_panel.addWidget(loc_pin)
        right_layout.addWidget(loc_panel)

        mission_panel = HoloPanel("MISSION")
        mission_title = QLabel("DAILY OBJECTIVES")
        mission_title.setStyleSheet("color: #a8b3cf; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace;")
        mission_panel.addWidget(mission_title)

        mission_items = [
            ("□", "DATA ANALYSIS", "COMPLETE TASKS BY 18:00"),
            ("□", "SYSTEM OPTIMIZATION", "PENDING REVIEW"),
            ("□", "SECURITY AUDIT", "IN PROGRESS"),
        ]
        for checkbox, title, status in mission_items:
            row = QHBoxLayout()
            row.setSpacing(8)
            cb = QLabel(checkbox)
            cb.setStyleSheet("color: #a8b3cf; font-size: 11px; font-family: 'Consolas', monospace;")
            row.addWidget(cb)
            t = QLabel(title)
            t.setStyleSheet("color: #e6f0ff; font-size: 11px; font-family: 'Consolas', monospace;")
            row.addWidget(t)
            row.addStretch()
            s = QLabel(status)
            s.setStyleSheet("color: #00ffff; font-size: 10px; font-family: 'Consolas', monospace;")
            row.addWidget(s)
            mission_panel.addLayout(row)
        right_layout.addWidget(mission_panel)

        sys_panel2 = HoloPanel("SYSTEM SETTINGS")
        sys_inner = QHBoxLayout()
        holo_body = QLabel("🫐")
        holo_body.setStyleSheet("font-size: 36px; color: rgba(0, 255, 255, 35);")
        sys_inner.addWidget(holo_body)
        sys_inner.addStretch()
        cap_lbl = QLabel("100%")
        cap_lbl.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        sys_inner.addWidget(cap_lbl)
        sys_panel2.addWidget(QLabel())
        sys_panel2.layout().addLayout(sys_inner)
        right_layout.addWidget(sys_panel2)

        right_layout.addStretch()
        content_layout.addWidget(right_panel, 0)

        main.addWidget(content, 1)

        # Bottom Navigation
        nav_bar = QWidget()
        nav_bar.setFixedHeight(82)
        nav_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(45)

        nav_items = [
            ("🧭", "NAVIGATOR"),
            ("📡", "DISPATCHER"),
            ("📷", "CAMERA"),
            ("💬", "MESSENGER"),
            ("⚙", "SYSTEM"),
        ]
        for icon, label in nav_items:
            btn = QPushButton(f"{icon}\n{label}")
            btn.setFixedSize(70, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(25, 35, 55, 160);
                    border: 2px solid rgba(0, 255, 255, 50);
                    border-radius: 14px;
                    color: #a8b3cf;
                    font-size: 10px;
                    font-family: 'Consolas', monospace;
                }
                QPushButton:hover { background: rgba(0, 255, 255, 45); color: #00ffff; }
            """)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        res_lbl = QLabel("444 x 296")
        res_lbl.setStyleSheet("color: #a8b3cf; font-size: 11px; font-family: 'Consolas', monospace;")
        nav_layout.addWidget(res_lbl)

        main.addWidget(nav_bar)

        # Bottom Left - Camera + Waveform
        bottom_left = QWidget()
        bottom_left.setAttribute(Qt.WA_TranslucentBackground, True)
        bottom_left.setFixedHeight(60)
        bottom_layout = QHBoxLayout(bottom_left)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(18)

        cam_btn = QPushButton("📷")
        cam_btn.setFixedSize(48, 48)
        cam_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 25);
                border: 1px solid rgba(0, 255, 255, 60);
                border-radius: 24px;
                color: #00ffff;
                font-size: 22px;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 55); }
        """)
        bottom_layout.addWidget(cam_btn)

        self.waveform_lbl = QLabel("▁▃▅▇▅▃▁")
        self.waveform_lbl.setStyleSheet("color: #00ffff; font-size: 16px; font-weight: bold; font-family: 'Consolas', monospace;")
        bottom_layout.addWidget(self.waveform_lbl)
        bottom_layout.addStretch()

        main.addWidget(bottom_left)

        # Hidden Chat Panel
        self.chat_panel = QWidget()
        self.chat_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        chat_panel_layout = QVBoxLayout(self.chat_panel)
        chat_panel_layout.setContentsMargins(0, 0, 0, 0)
        chat_panel_layout.setSpacing(12)

        self.chat_frame = HoloPanel("SYSTEM TERMINAL")
        chat_layout = QVBoxLayout(self.chat_frame)
        chat_layout.setContentsMargins(22, 16, 22, 16)
        chat_layout.setSpacing(10)

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QFrame.NoFrame)
        self.chat_scroll.setAttribute(Qt.WA_TranslucentBackground, True)
        self.chat_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.chat_container = QWidget()
        self.chat_container.setAttribute(Qt.WA_TranslucentBackground, True)
        self.chat_layout_inner = QVBoxLayout(self.chat_container)
        self.chat_layout_inner.setContentsMargins(0, 0, 0, 0)
        self.chat_layout_inner.setSpacing(12)
        self.chat_layout_inner.addStretch()

        self.chat_scroll.setWidget(self.chat_container)
        chat_layout.addWidget(self.chat_scroll, 1)

        self.typing = TypingIndicator()
        chat_layout.addWidget(self.typing)

        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 170);
                border: 1px solid rgba(0, 255, 255, 60);
                border-radius: 26px;
            }
        """)
        input_frame.setFixedHeight(60)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(22, 0, 18, 0)
        input_layout.setSpacing(12)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or speak to NOVA...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #e6f0ff;
                font-size: 14px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.voice_btn = QPushButton("🎙")
        self.voice_btn.setFixedSize(44, 44)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 30);
                border: 1px solid rgba(0, 255, 255, 80);
                border-radius: 22px;
                color: #00ffff;
                font-size: 18px;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 60); }
        """)
        self.voice_btn.clicked.connect(self._on_voice)
        input_layout.addWidget(self.voice_btn)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(88, 44)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(to right, #00ffff, #0099cc);
                border: none;
                border-radius: 22px;
                color: #000;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { background: linear-gradient(to right, #33e0ff, #0099cc); }
            QPushButton:disabled { background: #444; color: #888; }
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_frame)
        chat_panel_layout.addWidget(self.chat_frame)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.start_btn = QPushButton("▶ START")
        self.start_btn.setFixedSize(110, 40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #00ff9d;
                border: none;
                border-radius: 12px;
                color: #000000;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { opacity: 0.9; }
            QPushButton:pressed { opacity: 0.7; }
        """)
        self.start_btn.clicked.connect(self._start_nova)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setFixedSize(110, 40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                border: none;
                border-radius: 12px;
                color: #000000;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { opacity: 0.9; }
            QPushButton:pressed { opacity: 0.7; }
        """)
        self.stop_btn.clicked.connect(self._stop_nova)
        btn_row.addWidget(self.stop_btn)

        self.hide_chat_btn = QPushButton("✕ HIDE CHAT")
        self.hide_chat_btn.setFixedSize(120, 40)
        self.hide_chat_btn.setStyleSheet("""
            QPushButton {
                background: rgba(52, 73, 94, 160);
                border: none;
                border-radius: 12px;
                color: #00ffff;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { opacity: 0.9; }
        """)
        self.hide_chat_btn.clicked.connect(self._hide_chat)
        btn_row.addWidget(self.hide_chat_btn)

        btn_row.addStretch()
        chat_panel_layout.addLayout(btn_row)

        self.chat_panel.hide()
        main.addWidget(self.chat_panel)

    def _start_timers(self):
        self.dash_timer = QTimer(self)
        self.dash_timer.timeout.connect(self._update_dashboard)
        self.dash_timer.start(1000)
        self._update_dashboard()

        self.resize_timer = QTimer(self)
        self.resize_timer.timeout.connect(lambda: None)
        self.resize_timer.start(100)

        self.wave_timer = QTimer(self)
        self.wave_timer.timeout.connect(self._animate_wave)
        self.wave_timer.start(150)
        self._wave_state = 0

    def _animate_wave(self):
        states = ["▁▃▅▇▅▃▁", "▁▂▃▄▅▆▇", "▇▆▅▄▃▂▁", "▁▃▅▇▅▃▁"]
        self._wave_state = (self._wave_state + 1) % len(states)
        self.waveform_lbl.setText(states[self._wave_state])

    def _update_dashboard(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.cpu_bar.setValue(int(cpu))
            self.sys_cpu.set_value(int(cpu))
            self.sys_mem.set_value(int(ram))
            try:
                battery = psutil.sensors_battery()
                bat_text = f"{battery.percent}%" if battery else "N/A"
            except Exception:
                bat_text = "N/A"
            now = datetime.now()
            self.time_label.setText(now.strftime("%I:%M %p"))
            self.date_label.setText(now.strftime("%A %d %b %Y").upper())
        except Exception:
            pass

    def _register_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey("alt+space", lambda: threading.Thread(target=self._hotkey_listen, daemon=True).start())
        except Exception as exc:
            print(f"Hotkey registration failed: {exc}")

    def _hotkey_listen(self):
        try:
            text = listen()
        except Exception:
            text = ""
        if not text:
            return
        self._add_user_message(text)
        try:
            response = get_response(text)
        except Exception as exc:
            response = f"Error: {exc}"
        self._add_nova_message(response)
        try:
            speak(response)
        except Exception:
            pass

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

    def _show_chat(self):
        if not self.chat_visible:
            self.chat_visible = True
            self.chat_panel.show()
            self._add_nova_message("Chat terminal opened.")

    def _hide_chat(self):
        self.chat_visible = False
        self.chat_panel.hide()

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

    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return

        if text.lower() in ("show chat", "open chat"):
            self._show_chat()
            return

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
        self.status_label.setText("● LISTENING")
        self.status_label.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_ai_error(self, error_msg: str):
        self.typing.stop()
        self.core.set_mode("offline")
        self.status_label.setText("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
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
        self.status_label.setText("● LISTENING")
        self.status_label.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self._show_chat()

        def _voice_thread():
            try:
                text = listen()
            except Exception:
                text = ""
            if text:
                self._add_user_message(text)
                self._start_nova_stream()
                self._worker = NovaWorker(text)
                self._worker.chunk_received.connect(self._append_nova_stream)
                self._worker.finished.connect(self._on_ai_finished)
                self._worker.error.connect(self._on_ai_error)
                self._worker.start()
            else:
                self.core.set_mode("offline")
                self.status_label.setText("● OFFLINE")
                self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
                self.send_btn.setEnabled(True)
                self.input_field.setEnabled(True)

        threading.Thread(target=_voice_thread, daemon=True).start()

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
        self.core.set_mode("listening")
        self.status_label.setText("● LISTENING")
        self.status_label.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        threading.Thread(target=self._nova_loop, daemon=True).start()

    def _stop_nova(self):
        self.nova_running = False
        self.core.set_mode("offline")
        self.status_label.setText("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self._add_nova_message("System stopped.")
        show_notification("NOVA", "System stopped")

    def _nova_loop(self):
        while self.nova_running:
            try:
                text = listen()
            except Exception:
                text = ""
            if not text:
                continue
            self._add_user_message(text)
            self.core.set_mode("thinking")
            self.status_label.setText("● THINKING")
            self.status_label.setStyleSheet("color: #f1c40f; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
            response = ""
            try:
                for chunk in get_stream_response(text):
                    response += chunk
            except Exception as exc:
                response = f"Error: {exc}"
            if response == "EXIT_NOVA":
                self._add_nova_message("Shutting down.")
                self.core.set_mode("offline")
                self.status_label.setText("● OFFLINE")
                self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
                try:
                    speak("Shutting down")
                except Exception:
                    pass
                QTimer.singleShot(0, self.close)
                break
            self._add_nova_message(response)
            self.core.set_mode("speaking")
            self.status_label.setText("● SPEAKING")
            self.status_label.setStyleSheet("color: #9b59b6; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
            try:
                speak(response)
            except Exception:
                pass
            self.core.set_mode("listening")
            self.status_label.setText("● LISTENING")
            self.status_label.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")


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
