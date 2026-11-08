from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QInputDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class ProjectsPage(QWidget):
    """Project management page — add, list, open, and track projects."""

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
        title = QLabel("Projects")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00D4FF;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(90, 34)
        refresh_btn.setStyleSheet(self._button_style("#00D4FF"))
        refresh_btn.clicked.connect(self._refresh_projects)
        header.addWidget(refresh_btn)

        main.addLayout(header)

        # Stats / summary
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #A8B3CF; font-size: 13px;")
        main.addWidget(self.summary_label)

        # Project list
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background: rgba(20, 25, 40, 160);
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 16px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)

        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("Your Projects"))
        list_header.addStretch()
        list_layout.addLayout(list_header)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #E8EDF5;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                background: rgba(255, 255, 255, 8);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 10px;
                padding: 12px;
                margin: 4px;
            }
            QListWidget::item:selected {
                background: rgba(0, 212, 255, 40);
                border: 1px solid #00D4FF;
                color: #00D4FF;
            }
        """)
        self.project_list.itemDoubleClicked.connect(self._on_project_double_clicked)
        list_layout.addWidget(self.project_list)

        main.addWidget(list_frame, 1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.add_btn = QPushButton("➕ Add Project")
        self.add_btn.setFixedHeight(40)
        self.add_btn.setStyleSheet(self._button_style("#00D4FF"))
        self.add_btn.clicked.connect(self._add_project)
        btn_layout.addWidget(self.add_btn)

        self.open_btn = QPushButton("📂 Open Selected")
        self.open_btn.setFixedHeight(40)
        self.open_btn.setStyleSheet(self._button_style("#6366f1"))
        self.open_btn.clicked.connect(self._open_selected)
        btn_layout.addWidget(self.open_btn)

        self.delete_btn = QPushButton("🗑 Delete Selected")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setStyleSheet(self._button_style("#ef4444"))
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.notes_btn = QPushButton("📝 Add Note to Project")
        self.notes_btn.setFixedHeight(40)
        self.notes_btn.setStyleSheet(self._button_style("#8b5cf6"))
        self.notes_btn.clicked.connect(self._add_project_note)
        btn_layout.addWidget(self.notes_btn)

        main.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #00D4FF; font-size: 12px; font-weight: bold;")
        main.addWidget(self.status_label)

    @staticmethod
    def _button_style(accent: str) -> str:
        return f"""
            QPushButton {{
                background: {accent};
                border: none;
                border-radius: 10px;
                color: #000000;
                font-size: 13px;
                font-weight: bold;
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
            self.summary_label.setText(f"{len(projects)} project(s) saved")
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
            # Remove from memory by clearing and re-adding remaining
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
