from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont

import psutil
from datetime import datetime


# ======================
# COLORS (Jarvis / Iron Man)
# ======================

BG_DARK = "#050a14"
PANEL = "rgba(10, 20, 38, 200)"
ACCENT = "#00ffff"
ACCENT_DIM = "#0088aa"
TEXT = "#e8edf5"
TEXT_DIM = "#a8b3cf"
GLOW = "rgba(0, 255, 255, 60)"


class PulseLabel(QLabel):
    """A label that pulses its color to indicate AI core activity."""

    def __init__(self, text, color=ACCENT):
        super().__init__(text)
        self.base_color = color
        self._pulse = True
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(500)
        self.setStyleSheet(f"color: {color};")

    def _animate(self):
        if self._pulse:
            self.setStyleSheet(f"color: {self.base_color};")
        else:
            self.setStyleSheet(f"color: #1a2a4a;")
        self._pulse = not self._pulse

    def set_active_color(self, color: str):
        self.base_color = color


class GlassCard(QFrame):
    """A futuristic glass-style information card."""

    def __init__(self, title, icon, value="--", accent=ACCENT):
        super().__init__()
        self.setMinimumHeight(170)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(f"""
            QFrame {{
                background: {PANEL};
                border: 1px solid rgba(255, 255, 255, 18);
                border-radius: 22px;
            }}
            QFrame:hover {{
                background: rgba(20, 35, 60, 220);
                border: 1px solid {accent};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Icon row
        icon_row = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 30px; color: {accent};")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_row.addWidget(icon_label, 1)
        layout.addLayout(icon_row)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; font-weight: 600;")
        layout.addWidget(title_label)

        # Value
        self.value = QLabel(value)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet(f"color: {accent}; font-size: 32px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(self.value)

        # Subtle glow
        self.setGraphicsEffect(None)


class CoreWidget(QFrame):
    """Animated NOVA AI core — pulses like Jarvis."""

    def __init__(self):
        super().__init__()
        self.setFixedSize(160, 160)
        self.setStyleSheet("""
            QFrame {
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 255, 40),
                    stop:0.4 rgba(0, 255, 255, 10),
                    stop:1 rgba(0, 255, 255, 0)
                );
                border: 2px solid #00ffff;
                border-radius: 80px;
            }
        """)

        self.inner = QLabel("◉", self)
        self.inner.setFixedSize(120, 120)
        self.inner.move(20, 20)
        self.inner.setAlignment(Qt.AlignCenter)
        self.inner.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 64px;
                background: transparent;
            }
        """)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulse)
        self._timer.start(400)
        self._state = True

    def _pulse(self):
        if self._state:
            self.setStyleSheet("""
                QFrame {
                    background: qradialgradient(
                        cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(0, 255, 255, 70),
                        stop:0.4 rgba(0, 255, 255, 20),
                        stop:1 rgba(0, 255, 255, 0)
                    );
                    border: 2px solid #33e0ff;
                    border-radius: 80px;
                }
            """)
            self.inner.setStyleSheet("color: #33e0ff; font-size: 68px; background: transparent;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qradialgradient(
                        cx:0.5, cy:0.5, radius:0.5,
                        stop:0 rgba(0, 255, 255, 30),
                        stop:0.4 rgba(0, 255, 255, 5),
                        stop:1 rgba(0, 255, 255, 0)
                    );
                    border: 2px solid #00ffff;
                    border-radius: 80px;
                }
            """)
            self.inner.setStyleSheet("color: #00ffff; font-size: 64px; background: transparent;")
        self._state = not self._state

    def set_mode(self, mode: str):
        """Change core color based on system mode."""
        colors = {
            "online": "#00ff9d",
            "listening": "#00ffff",
            "thinking": "#f1c40f",
            "speaking": "#9b59b6",
            "offline": "#e74c3c",
        }
        color = colors.get(mode, ACCENT)
        self.inner.setStyleSheet(f"color: {color}; font-size: 64px; background: transparent;")
        self.setStyleSheet(f"""
            QFrame {{
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5,
                    stop:0 rgba(0, 255, 255, 30),
                    stop:0.4 rgba(0, 255, 255, 5),
                    stop:1 rgba(0, 255, 255, 0)
                ));
                border: 2px solid {color};
                border-radius: 80px;
            }}
        """)


class DashboardPage(QWidget):
    """Jarvis-style system dashboard with AI core and live monitoring."""

    def __init__(self, backend=None):
        super().__init__()
        self.setObjectName("dashboard")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()

        self._build_ui()
        self._start_timer()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 30, 40, 30)
        main.setSpacing(25)

        # --- Header: NOVA branding + core ---
        header = QHBoxLayout()
        header.setSpacing(25)

        self.core = CoreWidget()
        header.addWidget(self.core, 0)

        branding = QVBoxLayout()
        branding.setSpacing(4)

        title = QLabel("NOVA")
        title.setStyleSheet(f"font-size: 44px; font-weight: bold; color: {ACCENT}; letter-spacing: 2px;")
        branding.addWidget(title)

        subtitle = QLabel("JUST A RATHER VERY INTELLIGENT SYSTEM")
        subtitle.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; letter-spacing: 3px; font-family: 'Consolas', monospace;")
        branding.addWidget(subtitle)

        header.addLayout(branding, 1)

        # Mode indicator
        self.mode_label = QLabel("● ONLINE")
        self.mode_label.setStyleSheet(f"color: #00ff9d; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        header.addWidget(self.mode_label, 0)

        main.addLayout(header)

        # --- Dashboard cards ---
        cards = QHBoxLayout()
        cards.setSpacing(20)

        self.cpu_card = GlassCard("CPU", "⬡", "--%", ACCENT)
        self.ram_card = GlassCard("RAM", "⬢", "--%", "#00ffff")
        self.battery_card = GlassCard("BATTERY", "⚡", "--%", "#f1c40f")
        self.time_card = GlassCard("TIME", "⟳", "--:--", ACCENT)

        cards.addWidget(self.cpu_card)
        cards.addWidget(self.ram_card)
        cards.addWidget(self.battery_card)
        cards.addWidget(self.time_card)

        main.addLayout(cards)

        # --- System terminal ---
        terminal_frame = QFrame()
        terminal_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(5, 10, 20, 210);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 15);
            }}
        """)

        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setContentsMargins(20, 15, 20, 15)

        term_title = QLabel("SYSTEM TERMINAL")
        term_title.setStyleSheet(f"color: {ACCENT}; font-size: 14px; font-weight: bold; font-family: 'Consolas', monospace;")
        terminal_layout.addWidget(term_title)

        self.chat = QLabel()
        self.chat.setWordWrap(True)
        self.chat.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {TEXT};
                font-size: 13px;
                font-family: 'Consolas', monospace;
                padding: 10px;
            }}
        """)
        self.chat.setText("► NOVA Core v1.5 — JARVIS Edition\n► System online. Awaiting input.\n")
        terminal_layout.addWidget(self.chat)

        main.addWidget(terminal_frame, 1)

    # ------------------------------------------------------------------
    # Timer / updates
    # ------------------------------------------------------------------
    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(1000)
        self.update_dashboard()

    def update_dashboard(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            self.cpu_card.value.setText(f"{cpu}%")
            self.ram_card.value.setText(f"{ram}%")

            try:
                battery = psutil.sensors_battery()
                if battery:
                    self.battery_card.value.setText(f"{battery.percent}%")
                else:
                    self.battery_card.value.setText("N/A")
            except Exception:
                self.battery_card.value.setText("N/A")

            self.time_card.value.setText(datetime.now().strftime("%H:%M:%S"))
        except Exception:
            pass

    def set_mode(self, mode: str):
        self.core.set_mode(mode)
        colors = {
            "online": "#00ff9d",
            "listening": "#00ffff",
            "thinking": "#f1c40f",
            "speaking": "#9b59b6",
            "offline": "#e74c3c",
        }
        self.mode_label.setText(f"● {mode.upper()}")
        self.mode_label.setStyleSheet(f"color: {colors.get(mode, ACCENT)}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")

    def log(self, message: str):
        current = self.chat.text()
        lines = current.split("\n")
        if len(lines) > 12:
            lines = lines[-12:]
        lines.append(f"► {message}")
        self.chat.setText("\n".join(lines))
