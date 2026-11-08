from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QInputDialog, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class TasksPage(QWidget):
    """Task management page — add, complete, and delete tasks."""

    def __init__(self, backend=None):
        super().__init__()
        self.setObjectName("tasks")

        from nova_backend import NovaBackend
        self.backend = backend or NovaBackend()

        self._build_ui()
        self._refresh_tasks()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(30, 20, 30, 20)
        main.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Tasks")
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00D4FF;")
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(90, 34)
        refresh_btn.setStyleSheet(self._button_style("#00D4FF"))
        refresh_btn.clicked.connect(self._refresh_tasks)
        header.addWidget(refresh_btn)

        main.addLayout(header)

        # Task list
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
        list_header.addWidget(QLabel("Your Tasks"))
        list_header.addStretch()
        list_layout.addLayout(list_header)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
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
                padding: 14px;
                margin: 4px;
            }
            QListWidget::item:selected {
                background: rgba(0, 212, 255, 40);
                border: 1px solid #00D4FF;
            }
        """)
        list_layout.addWidget(self.task_list)

        main.addWidget(list_frame, 1)

        # Input + Add button
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        self.task_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 10);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                color: #E8EDF5;
                padding: 8px 14px;
                font-size: 13px;
            }
        """)
        self.task_input.returnPressed.connect(self._add_task)
        input_layout.addWidget(self.task_input, 1)

        self.add_btn = QPushButton("Add Task")
        self.add_btn.setFixedSize(110, 38)
        self.add_btn.setStyleSheet(self._button_style("#00D4FF"))
        self.add_btn.clicked.connect(self._add_task)
        input_layout.addWidget(self.add_btn)

        main.addLayout(input_layout)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.complete_btn = QPushButton("✔ Mark Complete")
        self.complete_btn.setFixedHeight(40)
        self.complete_btn.setStyleSheet(self._button_style("#22c55e"))
        self.complete_btn.clicked.connect(self._complete_selected)
        btn_layout.addWidget(self.complete_btn)

        self.delete_btn = QPushButton("🗑 Delete Selected")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setStyleSheet(self._button_style("#ef4444"))
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

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
    # Task operations
    # ------------------------------------------------------------------
    def _refresh_tasks(self):
        self.task_list.clear()
        result = self.backend.list_tasks()
        if result and result != "No tasks found.":
            for line in result.split("\n"):
                item = QListWidgetItem(line)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                # Determine completed status from the ☑ / ☐ prefix
                if line.startswith("☑"):
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.task_list.addItem(item)
        self.status_label.setText("")

    def _add_task(self):
        text = self.task_input.text().strip()
        if not text:
            return
        result = self.backend.add_task(text)
        self.status_label.setText(result)
        self.task_input.clear()
        self._refresh_tasks()

    def _complete_selected(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.information(self, "NOVA", "Please select a task first.")
            return
        row = self.task_list.row(item)
        result = self.backend.complete_task(row + 1)
        self.status_label.setText(result)
        self._refresh_tasks()

    def _delete_selected(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.information(self, "NOVA", "Please select a task first.")
            return
        row = self.task_list.row(item)
        reply = QMessageBox.question(
            self, "Delete Task",
            "Are you sure you want to delete this task?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            result = self.backend.delete_task(row + 1)
            self.status_label.setText(result)
            self._refresh_tasks()

    def _on_task_toggled(self, item: QListWidgetItem, state):
        row = self.task_list.row(item)
        if state == Qt.Checked:
            self.backend.complete_task(row + 1)
        else:
            # Re-open task — delete and re-add as incomplete
            memory = self.backend.load_memory()
            tasks = memory.get("tasks", [])
            if row < len(tasks):
                task_text = tasks[row]["text"]
                # Remove and re-add
                tasks.pop(row)
                memory["tasks"] = tasks
                self.backend.save_memory(memory)
                self.backend.add_task(task_text)
        self._refresh_tasks()
