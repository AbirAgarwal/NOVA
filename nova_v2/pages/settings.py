from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGroupBox, QComboBox, QCheckBox,
    QSpinBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

# ======================
# COLORS
# ======================

BG_DARK = "#050a14"
PANEL = "rgba(10, 20, 38, 160)"
ACCENT = "#00ffff"
TEXT = "#e8edf5"
TEXT_DIM = "#a8b3cf"


class SettingsPage(QWidget):
    """Jarvis-style settings page — AI model, voice, interface, memory."""

    def __init__(self, backend=None):
        super().__init__()
        self.setObjectName("settings")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()

        self._build_ui()
        self._load_memory_summary()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 20, 30, 20)
        main.setSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Header
        title = QLabel("SYSTEM SETTINGS")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {ACCENT}; letter-spacing: 2px; font-family: 'Consolas', monospace;")
        content_layout.addWidget(title)

        # --- AI Settings ---
        ai_group = self._group_box("AI BRAIN")
        ai_layout = QVBoxLayout(ai_group)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["qwen3:1.8b", "qwen3:4b", "phi3:mini", "gemma2:2b", "tinyllama"])
        self.model_combo.setCurrentText("qwen3:1.8b")
        self.model_combo.setStyleSheet(self._combo_style())
        self.model_combo.currentTextChanged.connect(self._on_model_change)
        ai_layout.addWidget(self._label_row("Ollama Model:", self.model_combo))

        self.stream_cb = QCheckBox("Enable streaming responses")
        self.stream_cb.setChecked(True)
        self.stream_cb.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-family: 'Consolas', monospace;")
        ai_layout.addWidget(self.stream_cb)

        content_layout.addWidget(ai_group)

        # --- Voice Settings ---
        voice_group = self._group_box("VOICE SYSTEMS")
        voice_layout = QVBoxLayout(voice_group)

        self.voice_rate = QSpinBox()
        self.voice_rate.setRange(50, 300)
        self.voice_rate.setValue(175)
        self.voice_rate.setSuffix(" WPM")
        self.voice_rate.setStyleSheet(self._spin_style())
        voice_layout.addWidget(self._label_row("Speech Rate:", self.voice_rate))

        self.voice_cb = QCheckBox("Enable text-to-speech")
        self.voice_cb.setChecked(True)
        self.voice_cb.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-family: 'Consolas', monospace;")
        voice_layout.addWidget(self.voice_cb)

        self.listen_cb = QCheckBox("Enable voice input (microphone)")
        self.listen_cb.setChecked(True)
        self.listen_cb.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-family: 'Consolas', monospace;")
        voice_layout.addWidget(self.listen_cb)

        content_layout.addWidget(voice_group)

        # --- Interface Settings ---
        ui_group = self._group_box("INTERFACE")
        ui_layout = QVBoxLayout(ui_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText("Dark")
        self.theme_combo.setStyleSheet(self._combo_style())
        ui_layout.addWidget(self._label_row("Theme:", self.theme_combo))

        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["Cyan (#00ffff)", "Blue (#3b82f6)", "Purple (#8b5cf6)", "Emerald (#10b981)"])
        self.accent_combo.setCurrentText("Cyan (#00ffff)")
        self.accent_combo.setStyleSheet(self._combo_style())
        ui_layout.addWidget(self._label_row("Accent Color:", self.accent_combo))

        content_layout.addWidget(ui_group)

        # --- Memory Summary ---
        mem_group = self._group_box("MEMORY CORE")
        mem_layout = QVBoxLayout(mem_group)

        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setFixedHeight(210)
        self.memory_display.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(5, 10, 20, 140);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 12px;
                color: {TEXT};
                padding: 14px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }}
        """)
        mem_layout.addWidget(self.memory_display)

        btn_layout = QHBoxLayout()
        refresh_mem_btn = QPushButton("REFRESH MEMORY")
        refresh_mem_btn.setFixedSize(140, 36)
        refresh_mem_btn.setStyleSheet(self._button_style(ACCENT))
        refresh_mem_btn.clicked.connect(self._load_memory_summary)
        btn_layout.addWidget(refresh_mem_btn)

        clear_mem_btn = QPushButton("CLEAR MEMORY")
        clear_mem_btn.setFixedSize(140, 36)
        clear_mem_btn.setStyleSheet(self._button_style("#ef4444"))
        clear_mem_btn.clicked.connect(self._clear_memory)
        btn_layout.addWidget(clear_mem_btn)
        btn_layout.addStretch()

        mem_layout.addLayout(btn_layout)
        content_layout.addWidget(mem_group)

        # --- System Actions ---
        sys_group = self._group_box("SYSTEM DIAGNOSTICS")
        sys_layout = QVBoxLayout(sys_group)

        sys_btn_layout = QHBoxLayout()

        briefing_btn = QPushButton("MORNING BRIEFING")
        briefing_btn.setFixedSize(150, 38)
        briefing_btn.setStyleSheet(self._button_style("#6366f1"))
        briefing_btn.clicked.connect(self._morning_briefing)
        sys_btn_layout.addWidget(briefing_btn)

        status_btn = QPushButton("STATUS REPORT")
        status_btn.setFixedSize(150, 38)
        status_btn.setStyleSheet(self._button_style("#6366f1"))
        status_btn.clicked.connect(self._status_report)
        sys_btn_layout.addWidget(status_btn)

        sys_btn_layout.addStretch()
        sys_layout.addLayout(sys_btn_layout)
        content_layout.addWidget(sys_group)

        content_layout.addStretch()

        scroll.setWidget(content)
        main.addWidget(scroll)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _group_box(title_text: str) -> QGroupBox:
        group = QGroupBox(title_text)
        group.setStyleSheet(f"""
            QGroupBox {{
                background: {PANEL};
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 16px;
                margin-top: 24px;
                font-size: 15px;
                font-weight: bold;
                color: {ACCENT};
                font-family: 'Consolas', monospace;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                top: 10px;
                padding: 0 8px;
            }}
        """)
        return group

    @staticmethod
    def _label_row(label_text: str, widget) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px; font-weight: 500; font-family: 'Consolas', monospace;")
        label.setFixedWidth(140)
        row.addWidget(label)
        row.addWidget(widget)
        row.addStretch()
        return container

    @staticmethod
    def _button_style(accent: str) -> str:
        return f"""
            QPushButton {{
                background: {accent};
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

    @staticmethod
    def _combo_style() -> str:
        return f"""
            QComboBox {{
                background: rgba(255, 255, 255, 8);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 8px;
                color: {TEXT};
                padding: 6px 12px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
                min-width: 200px;
            }}
            QComboBox:hover {{
                border: 1px solid {ACCENT};
            }}
        """

    @staticmethod
    def _spin_style() -> str:
        return f"""
            QSpinBox {{
                background: rgba(255, 255, 255, 8);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 8px;
                color: {TEXT};
                padding: 6px 12px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
                min-width: 120px;
            }}
            QSpinBox:hover {{
                border: 1px solid {ACCENT};
            }}
        """

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _on_model_change(self, model_name: str):
        self.backend.set_ai_model(model_name)

    def _load_memory_summary(self):
        try:
            stats = self.backend.get_stats()
            about = self.backend.about_user()
            lines = [
                f"USER: {about.split('.')[0] if about else 'Unknown'}",
                f"PROJECTS: {stats.get('projects', 0)}",
                f"TASKS: {stats.get('tasks', 0)}",
                f"GOALS: {stats.get('goals', 0)}",
                f"SKILLS: {stats.get('skills', 0)}",
                f"NOTES: {stats.get('notes', 0)}",
                f"JOURNAL: {stats.get('journal', 0)}",
                "",
                "AI MODEL: " + self.model_combo.currentText(),
                "STREAMING: ENABLED" if self.stream_cb.isChecked() else "STREAMING: DISABLED",
                "TTS: ENABLED" if self.voice_cb.isChecked() else "TTS: DISABLED",
                "VOICE INPUT: ENABLED" if self.listen_cb.isChecked() else "VOICE INPUT: DISABLED",
            ]
            self.memory_display.setText("\n".join(lines))
        except Exception as exc:
            self.memory_display.setText(f"Error loading memory: {exc}")

    def _clear_memory(self):
        reply = QMessageBox.question(
            self, "Clear Memory",
            "Are you sure you want to clear all saved memory? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            import json, os
            NOVA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            mem_file = os.path.join(NOVA_ROOT, "memory.json")
            default = {
                "user": {"name": "Abir", "preferences": {}},
                "facts": [], "projects": [], "skills": [],
                "goals": [], "notes": [], "tasks": [],
                "project_notes": {}, "journal": []
            }
            with open(mem_file, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)
            self._load_memory_summary()
            QMessageBox.information(self, "NOVA", "Memory cleared.")

    def _morning_briefing(self):
        try:
            briefing = self.backend.morning_briefing()
            QMessageBox.information(self, "Morning Briefing", briefing)
        except Exception as exc:
            QMessageBox.warning(self, "NOVA", f"Error: {exc}")

    def _status_report(self):
        try:
            report = self.backend.status_report()
            QMessageBox.information(self, "Status Report", report)
        except Exception as exc:
            QMessageBox.warning(self, "NOVA", f"Error: {exc}")
