from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QSizePolicy, QSpacerItem,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor


# ======================
# COLORS
# ======================

BG_DARK = "#050a14"
PANEL = "rgba(10, 20, 38, 180)"
ACCENT = "#00ffff"
ACCENT_DIM = "#0088aa"
TEXT = "#e8edf5"
TEXT_DIM = "#a8b3cf"
USER_COLOR = "#00ff9d"
NOVA_COLOR = ACCENT


class MessageBubble(QFrame):
    """A single chat message bubble — Jarvis style."""

    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        self.is_user = is_user
        self._build(text)

    def _build(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(720)
        self.label.setFont(QFont("Segoe UI", 12))
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if self.is_user:
            # User bubble — green, right-aligned
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 157, 60),
                        stop:1 rgba(0, 200, 120, 60)
                    );
                    border: 1px solid rgba(0, 255, 157, 100);
                    border-radius: 18px;
                    color: #000000;
                }}
            """)
            self.label.setStyleSheet("color: #000000; font-size: 13px; font-weight: 600;")
            layout.addStretch()
            layout.addWidget(self.label, 0)
        else:
            # NOVA bubble — glass cyan, left-aligned
            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(10, 20, 38, 200);
                    border: 1px solid rgba(0, 255, 255, 40);
                    border-radius: 18px;
                    color: {TEXT};
                }}
            """)
            self.label.setStyleSheet(f"color: {TEXT}; font-size: 13px;")
            layout.addWidget(self.label, 0)
            layout.addStretch()

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


class TypingIndicator(QFrame):
    """Animated 'NOVA is thinking...' indicator."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        self.label = QLabel("NOVA is processing...")
        self.label.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(self.label)
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._state = 0

    def start(self):
        self._timer.start(350)
        self.show()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _animate(self):
        states = ["▋", "▋▊", "▋▊▌", "▋▊▌▍", "▋▊▌▍▎", "▋▊▌▍▎▏", "▋▊▌▍▎", "▋▊▌▍", "▋▊▌", "▋▊", "▋"]
        self.label.setText(f"NOVA is processing {states[self._state % len(states)]}")
        self._state += 1


class AIWorker(QThread):
    """Background thread for streaming AI responses."""

    chunk_received = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, backend, text: str):
        super().__init__()
        self.backend = backend
        self.text = text

    def run(self):
        try:
            full_reply = ""
            for chunk in self.backend.get_stream_response(self.text):
                full_reply += chunk
                self.chunk_received.emit(chunk)
            self.finished.emit(full_reply)
        except Exception as exc:
            self.error.emit(str(exc))


class AssistantPage(QWidget):
    """Jarvis-style AI chat interface with streaming and voice."""

    def __init__(self, backend=None, dashboard=None):
        super().__init__()
        self.setObjectName("assistant")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()
        self.dashboard = dashboard

        self._worker = None
        self._current_nova_bubble = None
        self._current_nova_text = ""

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 20, 30, 20)
        main.setSpacing(15)

        # Header
        header = QHBoxLayout()

        title = QLabel("NOVA Assistant")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {ACCENT}; letter-spacing: 1px;")
        header.addWidget(title)
        header.addStretch()

        voice_btn = QPushButton("🎙 VOICE")
        voice_btn.setFixedSize(100, 36)
        voice_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 255, 255, 25);
                border: 1px solid {ACCENT};
                border-radius: 18px;
                color: {ACCENT};
                font-size: 11px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                background: rgba(0, 255, 255, 50);
            }}
            QPushButton:pressed {{
                background: rgba(0, 255, 255, 80);
            }}
        """)
        voice_btn.clicked.connect(self._on_voice)
        header.addWidget(voice_btn)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setFixedSize(80, 36)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 12);
                border: 1px solid rgba(255, 255, 255, 25);
                border-radius: 18px;
                color: {TEXT};
                font-size: 11px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 25);
            }}
        """)
        clear_btn.clicked.connect(self._clear_chat)
        header.addWidget(clear_btn)

        main.addLayout(header)

        # Scrollable chat area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()

        scroll.setWidget(self.chat_container)
        main.addWidget(scroll, 1)

        # Typing indicator (hidden by default)
        self.typing = TypingIndicator()
        self.typing.hide()
        main.addWidget(self.typing)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(5, 10, 20, 190);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 28px;
            }}
        """)
        input_frame.setFixedHeight(64)

        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(22, 0, 16, 0)
        input_layout.setSpacing(12)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or speak to NOVA...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TEXT};
                font-size: 14px;
                font-family: 'Consolas', monospace;
            }}
        """)
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("SEND")
        self.send_btn.setFixedSize(86, 44)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 #0099cc
                );
                border: none;
                border-radius: 22px;
                color: #000000;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33e0ff, stop:1 #0099cc
                );
            }}
            QPushButton:pressed {{
                background: #0077aa;
            }}
            QPushButton:disabled {{
                background: #444444;
                color: #888888;
            }}
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        main.addWidget(input_frame)

        # Welcome message
        self._add_nova_message("System online. I am NOVA — your personal AI operating companion. How may I assist you today?")

    # ------------------------------------------------------------------
    # Chat helpers
    # ------------------------------------------------------------------
    def _add_user_message(self, text: str):
        bubble = MessageBubble(text, is_user=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _add_nova_message(self, text: str):
        bubble = MessageBubble(text, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)
        return bubble

    def _start_nova_stream(self):
        self._current_nova_bubble = MessageBubble("", is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self._current_nova_bubble)
        self._current_nova_text = ""
        self.typing.start()
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _append_nova_stream(self, chunk: str):
        self._current_nova_text += chunk
        self._current_nova_bubble.label.setText(self._current_nova_text)
        QTimer.singleShot(20, self._scroll_to_bottom)

    def _finish_nova_stream(self, full_text: str):
        self._current_nova_text = full_text
        self._current_nova_bubble.label.setText(full_text)
        self.typing.stop()
        self._current_nova_bubble = None
        self._current_nova_text = ""
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _on_send(self):
        text = self.input_field.text().strip()
        if not text:
            return

        if self.dashboard:
            self.dashboard.set_mode("thinking")
            self.dashboard.log(f"User: {text}")

        self._add_user_message(text)
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        self._start_nova_stream()

        self._worker = AIWorker(self.backend, text)
        self._worker.chunk_received.connect(self._append_nova_stream)
        self._worker.finished.connect(self._on_ai_finished)
        self._worker.error.connect(self._on_ai_error)
        self._worker.start()

    def _on_ai_finished(self, full_text: str):
        self._finish_nova_stream(full_text)
        if self.dashboard:
            self.dashboard.set_mode("listening")
            self.dashboard.log(f"NOVA: {full_text}")
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_ai_error(self, error_msg: str):
        self.typing.stop()
        if self.dashboard:
            self.dashboard.set_mode("offline")
            self.dashboard.log(f"Error: {error_msg}")
        if self._current_nova_bubble:
            self._current_nova_bubble.label.setText(
                f"Error: {error_msg}"
            )
            self._current_nova_bubble = None
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_voice(self):
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)

        try:
            text = self.backend.listen()
            if text:
                self.input_field.setText(text)
                self._add_user_message(text)
                self._start_nova_stream()
                self._worker = AIWorker(self.backend, text)
                self._worker.chunk_received.connect(self._append_nova_stream)
                self._worker.finished.connect(self._on_ai_finished)
                self._worker.error.connect(self._on_ai_error)
                self._worker.start()
            else:
                self.send_btn.setEnabled(True)
                self.input_field.setEnabled(True)
        except Exception as exc:
            self._add_nova_message(f"Voice error: {exc}")
            self.send_btn.setEnabled(True)
            self.input_field.setEnabled(True)

    def _clear_chat(self):
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._add_nova_message("Chat cleared. How can I help you?")
