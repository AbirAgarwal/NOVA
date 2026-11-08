from qfluentwidgets import FluentWindow

from pages.dashboard import DashboardPage
from pages.assistant import AssistantPage
from pages.projects import ProjectsPage
from pages.tasks import TasksPage
from pages.settings import SettingsPage

from qfluentwidgets import FluentIcon
from nova_backend import NovaBackend


class MainWindow(FluentWindow):

    def __init__(self):

        super().__init__()

        self.resize(1450, 900)

        self.setWindowTitle("NOVA – Personal AI Operating System")

        # Single shared backend instance for all pages
        self.backend = NovaBackend()

        self.dashboard = DashboardPage()
        self.assistant = AssistantPage(backend=self.backend)
        self.projects = ProjectsPage(backend=self.backend)
        self.tasks = TasksPage(backend=self.backend)
        self.settings = SettingsPage(backend=self.backend)

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
