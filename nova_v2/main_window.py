from qfluentwidgets import FluentWindow, FluentIcon, setTheme, Theme

from pages.dashboard import DashboardPage
from pages.assistant import AssistantPage
from pages.projects import ProjectsPage
from pages.tasks import TasksPage
from pages.settings import SettingsPage

from nova_backend import NovaBackend


class MainWindow(FluentWindow):

    def __init__(self):

        super().__init__()

        self.resize(1500, 950)
        self.setMinimumSize(1200, 750)

        self.setWindowTitle("NOVA — JARVIS Interface")

        # Dark theme
        setTheme(Theme.DARK)

        # Single shared backend instance
        self.backend = NovaBackend()

        # Initialize all pages with the shared backend
        self.dashboard = DashboardPage(backend=self.backend)
        self.assistant = AssistantPage(backend=self.backend, dashboard=self.dashboard)
        self.projects = ProjectsPage(backend=self.backend)
        self.tasks = TasksPage(backend=self.backend)
        self.settings = SettingsPage(backend=self.backend)

        # Navigation rail — Jarvis style icons
        self.addSubInterface(
            self.dashboard,
            FluentIcon.HOME,
            "Dashboard"
        )

        self.addSubInterface(
            self.assistant,
            FluentIcon.CHAT,
            "Assistant"
        )

        self.addSubInterface(
            self.projects,
            FluentIcon.DOCUMENT,
            "Projects"
        )

        self.addSubInterface(
            self.tasks,
            FluentIcon.ACCEPT,
            "Tasks"
        )

        self.addSubInterface(
            self.settings,
            FluentIcon.SETTING,
            "Settings"
        )

        # Apply Jarvis-style styling to the window
        self._apply_jarvis_style()

    def _apply_jarvis_style(self):
        """Apply Jarvis/Iron Man dark glass theme to the window."""
        self.setStyleSheet("""
            QWidget {
                background: #050a14;
                color: #e8edf5;
                font-family: 'Segoe UI', 'Consolas', sans-serif;
            }
            QScrollBar:vertical {
                background: #0a1426;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #00ffff;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #33e0ff;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0;
            }
        """)
