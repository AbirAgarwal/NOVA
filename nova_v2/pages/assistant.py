from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QSizePolicy, QSpacerItem,
    QTextEdit, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette


class MessageBubble(QFrame):
    """A single chat message bubble."""

    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        self.is_user = is_user
        self._build(text)

    def _build(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(700)
        self.label.setFont(QFont("Segoe UI", 12))
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if self.is_user:
            # User bubble — blue, right-aligned
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00D4FF, stop:1 #0099CC
                    );
                    border-radius: 16px;
                    color: #000000;
                }
            """)
            self.label.setStyleSheet("color: #000000; font-size: 13px; font-weight: 500;")
            layout.addStretch()
            layout.addWidget(self.label, 0)
        else:
            # NOVA bubble — glass, left-aligned
            self.setStyleSheet("""
                QFrame {
                    background: rgba(40, 48, 72, 200);
                    border: 1px solid rgba(255, 255, 255, 20);
                    border-radius: 16px;
                    color: #E8EDF5;
                }
            """)
            self.label.setStyleSheet("color: #E8EDF5; font-size: 13px;")
            layout.addWidget(self.label, 0)
            layout.addStretch()

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


class TypingIndicator(QFrame):
    """Animated 'NOVA is typing...' indicator."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)

        self.dots = QLabel("●●●")
        self.dots.setStyleSheet("color: #00D4FF; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.dots)
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._state = 0

    def start(self):
        self._timer.start(400)
        self.show()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _animate(self):
        states = ["●●●", "●●○", "●○○", "○○●"]
        self.dots.setText(states[self._state % len(states)])
        self._state += 1


class AIWorker(QThread):
    """Background thread for streaming AI responses so the UI stays responsive."""

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
    """AI chat interface — the core of NOVA v2."""

    def __init__(self, backend=None):
        super().__init__()
        self.setObjectName("assistant")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()

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
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00D4FF;")
        header.addWidget(title)
        header.addStretch()

        voice_btn = QPushButton("🎙 Voice")
        voice_btn.setFixedSize(100, 36)
        voice_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 212, 255, 30);
                border: 1px solid #00D4FF;
                border-radius: 18px;
                color: #00D4FF;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 60);
            }
            QPushButton:pressed {
                background: rgba(0, 212, 255, 90);
            }
        """)
        voice_btn.clicked.connect(self._on_voice)
        header.addWidget(voice_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(80, 36)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 15);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 18px;
                color: #E8EDF5;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
            }
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
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()

        scroll.setWidget(self.chat_container)
        main.addWidget(scroll, 1)

        # Typing indicator (hidden by default)
        self.typing = TypingIndicator()
        self.typing.hide()
        main.addWidget(self.typing)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(20, 25, 40, 180);
                border: 1px solid rgba(255, 255, 255, 25);
                border-radius: 25px;
            }
        """)
        input_frame.setFixedHeight(60)

        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 0, 15, 0)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command or ask NOVA...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #E8EDF5;
                font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedSize(90, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D4FF, stop:1 #0099CC
                );
                border: none;
                border-radius: 20px;
                color: #000000;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33E0FF, stop:1 #0099CC
                );
            }
            QPushButton:pressed {
                background: #0077AA;
            }
            QPushButton:disabled {
                background: #555555;
                color: #AAAAAA;
            }
        """)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        main.addWidget(input_frame)

        # Welcome message
        self._add_nova_message("Hello! I'm NOVA, your personal AI operating companion. How can I help you today?")

    # ------------------------------------------------------------------
    # Chat helpers
    # ------------------------------------------------------------------
    def _add_user_message(self, text: str):
        bubble = MessageBubble(text, is_user=True)
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _add_nova_message(self, text: str):
        bubble = MessageBubble(text, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)
        return bubble

    def _start_nova_stream(self):
        """Begin a streaming NOVA message bubble."""
        self._current_nova_bubble = MessageBubble("", is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self._current_nova_bubble)
        self._current_nova_text = ""
        self.typing.start()
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _append_nova_stream(self, chunk: str):
        self._current_nova_text += chunk
        self._current_nova_bubble.label.setText(self._current_nova_text)
        QTimer.singleShot(30, self._scroll_to_bottom)

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
        self.send_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self._worker = None

    def _on_ai_error(self, error_msg: str):
        self.typing.stop()
        if self._current_nova_bubble:
            self._current_nova_bubble.label.setText(
                f"Sorry, I ran into an error: {error_msg}"
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
        # Remove all bubbles except the stretch
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._add_nova_message("Chat cleared. How can I help you?")
