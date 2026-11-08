import sys
import threading
import os
import math
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
# 3D REACTOR CORE (Right Side)
# ======================

class ReactorCore(QWidget):
    """Improved Jarvis-style arc reactor with multiple glowing rings."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self._angle = 0
        self._pulse = 0.0
        self._mode = "online"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def set_mode(self, mode: str):
        self._mode = mode
        self.update()

    def _animate(self):
        self._angle = (self._angle + 4) % 360
        self._pulse = (self._pulse + 0.06) % (math.pi * 2)
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

        # Outer rings - multiple layers
        for i in range(4):
            ring_r = 95 - (i * 18)
            alpha = int(50 * (1 - i * 0.2)) + int(30 * abs(math.sin(self._pulse)))
            glow = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(QPen(glow, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)

        # Middle energy ring that rotates
        mid_r = 55
        painter.setPen(QPen(color, 3))
        painter.setBrush(Qt.NoBrush)
        for i in range(8):
            ang = self._angle + i * 45
            x1 = cx + int(mid_r * 0.7 * math.cos(math.radians(ang)))
            y1 = cy + int(mid_r * 0.7 * math.sin(math.radians(ang)))
            x2 = cx + int(mid_r * math.cos(math.radians(ang)))
            y2 = cy + int(mid_r * math.sin(math.radians(ang)))
            painter.drawLine(x1, y1, x2, y2)

        # Inner core
        inner_r = int(28 + 6 * abs(math.sin(self._pulse * 2)))
        grad = QRadialGradient(cx, cy, inner_r)
        grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 255))
        grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 40))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)

        # Center dot
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 3, cy - 3, 6, 6)


# ======================
# 3D SPINNING LAPTOP HOLOGRAM (Center)
# ======================

class LaptopHologram(QWidget):
    """3D spinning laptop hologram like Jarvis armor display."""

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._angle = 0
        self._tilt = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(40)

    def _animate(self):
        self._angle = (self._angle + 3) % 360
        self._tilt = (self._tilt + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # Hologram color (cyan wireframe)
        holo = QColor(0, 255, 255, 160)
        holo_dim = QColor(0, 255, 255, 60)
        painter.setPen(QPen(holo, 2))
        painter.setBrush(Qt.NoBrush)

        # Rotation for 3D effect
        rad = math.radians(self._angle)
        tilt_rad = math.radians(self._tilt)
        scale_x = abs(math.cos(rad)) * 0.8 + 0.2  # Never fully disappear
        scale_y = abs(math.cos(tilt_rad)) * 0.6 + 0.4

        # Base size
        lap_w = int(160 * scale_x)
        lap_h = int(110 * scale_y)
        screen_h = int(70 * scale_y)
        keyboard_h = int(30 * scale_y)

        # Laptop base (keyboard area)
        base_rect = QRect(cx - lap_w // 2, cy + screen_h // 2, lap_w, keyboard_h)
        painter.drawRect(base_rect)

        # Screen
        screen_rect = QRect(cx - lap_w // 2, cy - screen_h // 2, lap_w, screen_h)
        painter.drawRect(screen_rect)

        # Hinge line
        painter.drawLine(cx - lap_w // 2, cy - screen_h // 2 + screen_h, cx + lap_w // 2, cy - screen_h // 2 + screen_h)

        # Screen inner detail
        inner = QRect(cx - lap_w // 2 + 10, cy - screen_h // 2 + 10, lap_w - 20, screen_h - 20)
        painter.setPen(QPen(holo_dim, 1))
        painter.drawRect(inner)

        # NOVA text on screen
        painter.setPen(QPen(ACCENT, 1))
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.drawText(cx - 20, cy, "NOVA")

        # Keyboard keys (small dots)
        painter.setPen(QPen(holo, 2))
        for row in range(3):
            for col in range(6):
                kx = cx - lap_w // 2 + 20 + col * 20
                ky = cy + screen_h // 2 + 8 + row * 8
                if kx < cx + lap_w // 2 - 10:
                    painter.drawPoint(kx, ky)

        # Rotating scan ring around laptop
        self._pulse = self._angle * 0.1
        ring_r = int(max(lap_w, screen_h + keyboard_h) * 0.6 + 20 * abs(math.sin(self._pulse)))
        painter.setPen(QPen(QColor(0, 255, 255, 80), 1))
        painter.drawEllipse(cx - ring_r, cy - ring_r // 2, ring_r * 2, ring_r)

        # Floating particles around
        painter.setPen(QPen(QColor(0, 255, 255, 100), 2))
        for i in range(6):
            ang = self._angle + i * 60
            px = cx + int(130 * math.cos(math.radians(ang)))
            py = cy + int(60 * math.sin(math.radians(ang)))
            painter.drawEllipse(px - 2, py - 2, 4, 4)


# ======================
# SMALL STATS (Right Side, below core)
# ======================

class MiniStat(QLabel):
    """A tiny stat display."""

    def __init__(self, name, color):
        super().__init__()
        self.name = name
        self.color = color
        self.setFixedHeight(22)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color.name()};
                font-size: 10px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
                background: transparent;
            }}
        """)
        self.setText(f"{name}: --")


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
        self.resize(1500, 900)
        self.setMinimumSize(1200, 700)
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

        # Content - Three columns: Left(empty), Center(Hologram), Right(Core+Stats)
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground, True)
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(40)

        # Left: Empty spacer (for balance) + hidden chat container
        self.left_spacer = QWidget()
        self.left_spacer.setAttribute(Qt.WA_TranslucentBackground, True)
        self.left_spacer.setMinimumWidth(100)
        content_layout.addWidget(self.left_spacer, 0)

        # Center: Spinning Laptop Hologram
        center_panel = QWidget()
        center_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignCenter)

        self.hologram = LaptopHologram()
        self.hologram.setFixedSize(300, 300)
        center_layout.addWidget(self.hologram)

        # Status below hologram
        self.status_label = QLabel("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.status_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.status_label)

        content_layout.addWidget(center_panel, 1)

        # Right: Core + Stats
        right_panel = QWidget()
        right_panel.setAttribute(Qt.WA_TranslucentBackground, True)
        right_panel.setFixedWidth(320)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        # Reactor Core
        core_container = QWidget()
        core_container.setAttribute(Qt.WA_TranslucentBackground, True)
        core_layout = QHBoxLayout(core_container)
        core_layout.setContentsMargins(0, 0, 0, 0)
        core_layout.setAlignment(Qt.AlignCenter)

        self.core = ReactorCore()
        core_layout.addWidget(self.core)
        right_layout.addWidget(core_container)

        # Stats below core (small)
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 160);
                border: 1px solid rgba(0, 255, 255, 40);
                border-radius: 12px;
            }
        """)
        stats_frame.setFixedWidth(280)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(4)

        stats_title = QLabel("SYSTEM VITALS")
        stats_title.setStyleSheet("color: #00ffff; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace; letter-spacing: 1px;")
        stats_layout.addWidget(stats_title)

        self.cpu_label = MiniStat("CPU", QColor(0, 255, 157))
        self.ram_label = MiniStat("RAM", QColor(0, 255, 255))
        self.bat_label = MiniStat("BAT", QColor(241, 196, 15))
        self.time_label = MiniStat("TIME", QColor(0, 255, 255))

        stats_layout.addWidget(self.cpu_label)
        stats_layout.addWidget(self.ram_label)
        stats_layout.addWidget(self.bat_label)
        stats_layout.addWidget(self.time_label)

        right_layout.addWidget(stats_frame, 0, Qt.AlignCenter)
        right_layout.addStretch()

        content_layout.addWidget(right_panel, 0)

        main.addWidget(content, 1)

        # Hidden Chat Panel (shown on "show chat" command)
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

        # Control buttons for chat panel
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

        # Initially hidden
        self.chat_panel.hide()
        main.addWidget(self.chat_panel)

    def _make_stat(self, name, value, color):
        # Kept for compatibility, not used in new layout
        pass

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
            current_time = datetime.now().strftime("%I:%M:%S %p")

            self.cpu_label.setText(f"CPU: {cpu}%")
            self.ram_label.setText(f"RAM: {ram}%")
            self.bat_label.setText(f"BAT: {bat_text}")
            self.time_label.setText(f"TIME: {current_time}")
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
