import sys
import threading
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea
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

BG_DARK = QColor(5, 10, 20)          # Deep space black
PANEL = QColor(10, 20, 38, 220)      # Glass panel
PANEL_BORDER = QColor(0, 255, 255, 60)  # Cyan border
ACCENT = QColor(0, 255, 255)         # Cyan neon
ACCENT_DIM = QColor(0, 136, 170)     # Dim cyan
TEXT = QColor(232, 237, 245)         # Off white
TEXT_DIM = QColor(168, 179, 207)     # Gray text
GLOW = QColor(0, 255, 255, 40)       # Cyan glow
SUCCESS = QColor(0, 255, 157)        # Green
THINKING = QColor(241, 196, 15)      # Yellow
SPEAKING = QColor(155, 89, 182)      # Purple
OFFLINE = QColor(231, 76, 60)        # Red
ONLINE = QColor(0, 255, 157)         # Green


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
# REACTOR CORE WIDGET
# ======================

class ReactorCore(QWidget):
    """Animated Jarvis-style arc reactor core in the center."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(220, 220)
        self._angle = 0
        self._pulse = 0.0
        self._mode = "online"  # online, listening, thinking, speaking, offline
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30)

    def set_mode(self, mode: str):
        self._mode = mode
        self.update()

    def _animate(self):
        self._angle = (self._angle + 3) % 360
        self._pulse = (self._pulse + 0.05) % (3.14159 * 2)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2
        radius = min(cx, cy) - 10

        # Mode color
        mode_colors = {
            "online": ONLINE,
            "listening": ACCENT,
            "thinking": THINKING,
            "speaking": SPEAKING,
            "offline": OFFLINE,
        }
        color = mode_colors.get(self._mode, ACCENT)

        # Outer glow rings
        for i in range(3):
            ring_radius = radius - (i * 8)
            alpha = int(60 * (1 - i * 0.25)) + int(40 * abs(__import__("math").sin(self._pulse)))
            glow = QColor(color.red(), color.green(), color.blue(), alpha)
            painter.setPen(QPen(glow, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - ring_radius, cy - ring_radius, ring_radius * 2, ring_radius * 2)

        # Inner core
        inner_radius = int(radius * 0.35 + 5 * abs(__import__("math").sin(self._pulse * 2)))
        gradient = QRadialGradient(cx, cy, inner_radius)
        gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 255))
        gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 60))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color, 3))
        painter.drawEllipse(cx - inner_radius, cy - inner_radius, inner_radius * 2, inner_radius * 2)

        # Rotating scan lines
        painter.setPen(QPen(color, 2))
        for i in range(6):
            angle = self._angle + i * 60
            import math
            x1 = cx + int(inner_radius * 0.6 * math.cos(math.radians(angle)))
            y1 = cy + int(inner_radius * 0.6 * math.sin(math.radians(angle)))
            x2 = cx + int(radius * 0.9 * math.cos(math.radians(angle)))
            y2 = cy + int(radius * 0.9 * math.sin(math.radians(angle)))
            painter.drawLine(x1, y1, x2, y2)

        # Center dot
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 4, cy - 4, 8, 8)


# ======================
# GLASS PANEL
# ======================

class GlassPanel(QFrame):
    """A translucent glassmorphism panel with neon border."""

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
# CHAT BUBBLE
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
            # User bubble — green, right side
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
            # NOVA bubble — glass cyan, left side
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

        self.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Maximum
        )

        # Start fully transparent for fade-in
        self.setWindowOpacity(0.0)

    # ------------------------------------------------------------------
    # Floating / fade animation
    # ------------------------------------------------------------------
    def _start_floating_animation(self):
        # Fade in
        self._fade_in = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_in.setDuration(600)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        # Float upward slightly as we fade in
        self._float_up = QPropertyAnimation(self, b"pos", self)
        self._float_up.setDuration(700)
        self._float_up.setStartValue(self.pos() + QPoint(0, 12))
        self._float_up.setEndValue(self.pos())
        self._float_up.setEasingCurve(QEasingCurve.OutCubic)

        self._group = QParallelAnimationGroup(self)
        self._group.addAnimation(self._fade_in)
        self._group.addAnimation(self._float_up)
        self._group.start()

        # After TTL, fade out and remove
        QTimer.singleShot(self.ttl_ms, self._fade_out_and_remove)

    def _fade_out_and_remove(self):
        self._fade_out = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_out.setDuration(800)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)

        # Drift further up as fading out
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
        # Notify parent layout to clean up
        parent_layout = self.parentWidget().layout() if self.parentWidget() else None
        if parent_layout:
            parent_layout.removeWidget(self)
        self.deleteLater()


# ======================
# TYPING INDICATOR
# ======================

class TypingIndicator(QWidget):
    """Animated 'NOVA is processing...' indicator."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)

        self.label = QLabel("NOVA is processing")
        self.label.setStyleSheet(f"color: #00ffff; font-size: 11px; font-weight: bold; font-family: 'Consolas', monospace;")
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
# HUD SCAN LINES OVERLAY
# ======================

class HUDOverlay(QWidget):
    """Full-screen HUD overlay with scan lines and grid."""

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

        # Scan lines
        pen = QPen(QColor(0, 255, 255, 15), 1)
        painter.setPen(pen)
        for y in range(0, self.height(), 4):
            painter.drawLine(0, (y + self._offset) % self.height(), self.width(), (y + self._offset) % self.height())

        # Corner brackets
        pen = QPen(QColor(0, 255, 255, 80), 2)
        painter.setPen(pen)
        size = 40
        # Top-left
        painter.drawLine(20, 20, 20 + size, 20)
        painter.drawLine(20, 20, 20, 20 + size)
        # Top-right
        painter.drawLine(self.width() - 20 - size, 20, self.width() - 20, 20)
        painter.drawLine(self.width() - 20, 20, self.width() - 20, 20 + size)
        # Bottom-left
        painter.drawLine(20, self.height() - 20 - size, 20, self.height() - 20)
        painter.drawLine(20, self.height() - 20, 20 + size, self.height() - 20)
        # Bottom-right
        painter.drawLine(self.width() - 20 - size, self.height() - 20, self.width() - 20, self.height() - 20)
        painter.drawLine(self.width() - 20, self.height() - 20 - size, self.width() - 20, self.height() - 20)


# ======================
# MAIN JARVIS WINDOW
# ======================

class JarvisWindow(QMainWindow):
    """NOVA — Jarvis-style AI Operating Companion."""

    def __init__(self):
        super().__init__()

        gui_controller.GUI_ROOT = self

        # Window setup — frameless and translucent
        self.setWindowTitle("NOVA — JARVIS Interface")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 700)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.nova_running = False
        self.current_ai_model = "qwen3:1.8b"
        self._worker = None
        self._current_nova_bubble = None
        self._current_nova_text = ""
        self._drag_pos = None

        self._build_ui()
        self._start_timers()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Central widget with translucent background
        self.central = QWidget()
        self.central.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCentralWidget(self.central)

        main = QVBoxLayout(self.central)
        main.setContentsMargins(40, 30, 40, 30)
        main.setSpacing(20)

        # --- HUD Overlay (full screen) ---
        self.hud = HUDOverlay(self.central)
        self.hud.setGeometry(0, 0, self.width(), self.height())
        self.hud.raise_()

        # --- Title Bar (custom, draggable) ---
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setAttribute(Qt.WA_TranslucentBackground, True)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("◉ NOVA CORE")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffff; letter-spacing: 2px;")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        # Window controls
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

        # --- Content Area ---
        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground, True)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Status + Model row
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        # Status indicator
        self.status_label = QLabel("● OFFLINE")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
        top_row.addWidget(self.status_label)

        top_row.addStretch()

        # Model selector
        model_label = QLabel("AI Model:")
        model_label.setStyleSheet("color: #a8b3cf; font-size: 11px; font-family: 'Consolas', monospace;")
        top_row.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen3:1.8b", "qwen3:4b", "phi3:mini", "gemma2:2b", "tinyllama"])
        self.model_combo.setCurrentText("qwen3:1.8b")
        self.model_combo.setFixedWidth(150)
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: rgba(10, 20, 38, 160);
                border: 1px solid rgba(0, 255, 255, 60);
                border-radius: 8px;
                color: #e8edf5;
                padding: 4px 10px;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.model_combo.currentTextChanged.connect(self._on_model_change)
        top_row.addWidget(self.model_combo)

        content_layout.addLayout(top_row)

        # --- Reactor Core ---
        core_container = QWidget()
        core_container.setAttribute(Qt.WA_TranslucentBackground, True)
        core_layout = QHBoxLayout(core_container)
        core_layout.setContentsMargins(0, 0, 0, 0)
        core_layout.setAlignment(Qt.AlignCenter)

        self.core = ReactorCore()
        core_layout.addWidget(self.core)

        content_layout.addWidget(core_container)

        # --- Dashboard Row ---
        dash = QHBoxLayout()
        dash.setSpacing(15)

        self.cpu_label = self._make_stat("CPU", "0%", QColor(0, 255, 157))
        self.ram_label = self._make_stat("RAM", "0%", QColor(0, 255, 255))
        self.bat_label = self._make_stat("BAT", "0%", QColor(241, 196, 15))
        self.time_label = self._make_stat("TIME", "00:00", QColor(0, 255, 255))

        dash.addWidget(self.cpu_label)
        dash.addWidget(self.ram_label)
        dash.addWidget(self.bat_label)
        dash.addWidget(self.time_label)

        content_layout.addLayout(dash)

        # --- Chat Area ---
        chat_frame = GlassPanel()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(20, 15, 20, 15)
        chat_layout.setSpacing(10)

        self.chat_title = QLabel("SYSTEM TERMINAL")
        self.chat_title.setStyleSheet("color: #00ffff; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        chat_layout.addWidget(self.chat_title)

        # Scrollable chat
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

        # Typing indicator
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
        input_layout.setSpacing(12)

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

        content_layout.addWidget(chat_frame, 1)

        # --- Control Buttons ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.start_btn = QPushButton("▶ START")
        self.start_btn.setFixedSize(120, 40)
        self.start_btn.setStyleSheet(self._btn_style("#00ff9d"))
        self.start_btn.clicked.connect(self._start_nova)
        btn_row.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setFixedSize(120, 40)
        self.stop_btn.setStyleSheet(self._btn_style("#e74c3c"))
        self.stop_btn.clicked.connect(self._stop_nova)
        btn_row.addWidget(self.stop_btn)

        self.tray_btn = QPushButton("⬇ TRAY")
        self.tray_btn.setFixedSize(100, 40)
        self.tray_btn.setStyleSheet(self._btn_style("#34495e"))
        self.tray_btn.clicked.connect(self._minimize_to_tray)
        btn_row.addWidget(self.tray_btn)

        btn_row.addStretch()

        content_layout.addLayout(btn_row)

        main.addWidget(content, 1)

        # Welcome message
        self._add_nova_message("System online. I am NOVA — your Jarvis-style AI companion. How may I assist you?")

    def _make_stat(self, name, value, color):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 20, 38, 140);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 12px;
            }
        """)
        panel.setFixedSize(150, 70)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: #a8b3cf; font-size: 10px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(name_lbl)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {color.name()}; font-size: 20px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(val_lbl)

        panel.value_label = val_lbl
        return panel

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

        # Resize HUD on window resize
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

            self.cpu_label.value_label.setText(f"{cpu}%")
            self.ram_label.value_label.setText(f"{ram}%")
            self.bat_label.value_label.setText(bat_text)
            self.time_label.value_label.setText(current_time)

            stats = get_stats()
            # Could add memory stats here too
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Window dragging (frameless)
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

        self.core.set_mode("thinking")
        self.set_status("thinking", f"User: {text}")

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
                self.set_status("offline", "No speech detected.")
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
        self.status_label.setStyleSheet(f"color: {hex_color.name()}; font-size: 13px; font-weight: bold; font-family: 'Consolas', monospace;")
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
            self.set_status("thinking", "Thinking...")
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
            self.set_status("speaking", "Speaking...")
            try:
                speak(response)
            except Exception:
                pass
            self.set_status("listening", "Listening...")

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
# ENTRY POINT
# ======================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette for any non-styled widgets
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
