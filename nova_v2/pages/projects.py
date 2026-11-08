from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# ======================
# COLORS
# ======================

BG_DARK = "#050a14"
PANEL = "rgba(10, 20, 38, 180)"
ACCENT = "#00ffff"
TEXT = "#e8edf5"
TEXT_DIM = "#a8b3cf"


class ProjectsPage(QWidget):
    """Jarvis-style project management page."""

    def __init__(self, backend=None):
        super().__init__()
        self.setObjectName("projects")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()

        self._build_ui()
        self._refresh_projects()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 20, 30, 20)
        main.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("PROJECTS")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {ACCENT}; letter-spacing: 2px; font-family: 'Consolas', monospace;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setFixedSize(95, 34)
        refresh_btn.setStyleSheet(self._button_style(ACCENT))
        refresh_btn.clicked.connect(self._refresh_projects)
        header.addWidget(refresh_btn)

        main.addLayout(header)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; font-family: 'Consolas', monospace;")
        main.addWidget(self.summary_label)

        # Project list
        list_frame = QFrame()
        list_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(5, 10, 20, 160);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 16px;
            }}
        """)
        list_layout = QVBoxLayout(list_frame)

        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("ACTIVE PROJECTS"))
        list_header.addStretch()
        list_layout.addLayout(list_header)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                color: {TEXT};
                font-size: 14px;
                font-family: 'Consolas', monospace;
                outline: none;
            }}
            QListWidget::item {{
                background: rgba(255, 255, 255, 6);
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 10px;
                padding: 14px;
                margin: 5px;
            }}
            QListWidget::item:selected {{
                background: rgba(0, 255, 255, 35);
                border: 1px solid {ACCENT};
                color: {ACCENT};
            }}
        """)
        self.project_list.itemDoubleClicked.connect(self._on_project_double_clicked)
        list_layout.addWidget(self.project_list)

        main.addWidget(list_frame, 1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.add_btn = QPushButton("➕ ADD PROJECT")
        self.add_btn.setFixedHeight(42)
        self.add_btn.setStyleSheet(self._button_style(ACCENT))
        self.add_btn.clicked.connect(self._add_project)
        btn_layout.addWidget(self.add_btn)

        self.open_btn = QPushButton("📂 OPEN SELECTED")
        self.open_btn.setFixedHeight(42)
        self.open_btn.setStyleSheet(self._button_style("#6366f1"))
        self.open_btn.clicked.connect(self._open_selected)
        btn_layout.addWidget(self.open_btn)

        self.delete_btn = QPushButton("🗑 DELETE")
        self.delete_btn.setFixedHeight(42)
        self.delete_btn.setStyleSheet(self._button_style("#ef4444"))
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.notes_btn = QPushButton("📝 ADD NOTE")
        self.notes_btn.setFixedHeight(42)
        self.notes_btn.setStyleSheet(self._button_style("#8b5cf6"))
        self.notes_btn.clicked.connect(self._add_project_note)
        btn_layout.addWidget(self.notes_btn)

        main.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        main.addWidget(self.status_label)

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

    # ------------------------------------------------------------------
    # Project operations
    # ------------------------------------------------------------------
    def _refresh_projects(self):
        self.project_list.clear()
        result = self.backend.list_projects_memory()
        if result and result != "No projects stored.":
            projects = [p.strip() for p in result.split(",") if p.strip()]
            for project in projects:
                item = QListWidgetItem(project)
                self.project_list.addItem(item)
            self.summary_label.setText(f"{len(projects)} project(s) in memory")
        else:
            self.summary_label.setText("No projects stored yet.")
        self.status_label.setText("")

    def _add_project(self):
        name, ok = QInputDialog.getText(
            self, "Add Project", "Project name:"
        )
        if ok and name.strip():
            result = self.backend.add_project(name.strip())
            self.status_label.setText(result)
            self._refresh_projects()

    def _open_selected(self):
        item = self.project_list.currentItem()
        if not item:
            QMessageBox.information(self, "NOVA", "Please select a project first.")
            return
        project_name = item.text()
        result = self.backend.open_project(project_name)
        self.status_label.setText(result)
        QMessageBox.information(self, "NOVA", result)

    def _delete_selected(self):
        item = self.project_list.currentItem()
        if not item:
            QMessageBox.information(self, "NOVA", "Please select a project first.")
            return
        project_name = item.text()
        reply = QMessageBox.question(
            self, "Delete Project",
            f"Are you sure you want to delete '{project_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            memory = self.backend.load_memory()
            if project_name in memory.get("projects", []):
                memory["projects"].remove(project_name)
                self.backend.save_memory(memory)
            self._refresh_projects()
            self.status_label.setText(f"Deleted project: {project_name}")

    def _add_project_note(self):
        item = self.project_list.currentItem()
        if not item:
            QMessageBox.information(self, "NOVA", "Please select a project first.")
            return
        project_name = item.text()
        note, ok = QInputDialog.getMultiLineText(
            self, "Add Note", f"Note for '{project_name}':"
        )
        if ok and note.strip():
            result = self.backend.add_project_note(project_name, note.strip())
            self.status_label.setText(result)

    def _on_project_double_clicked(self, item: QListWidgetItem):
        project_name = item.text()
        result = self.backend.show_project(project_name)
        QMessageBox.information(self, f"Project: {project_name}", result)
