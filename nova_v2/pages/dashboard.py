from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import psutil
from datetime import datetime


class GlassCard(QFrame):
    def __init__(self, title, icon):
        super().__init__()

        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QFrame{
                background:rgba(40,48,72,185);
                border:1px solid rgba(255,255,255,35);
                border-radius:20px;
            }

            QFrame:hover{
                background:rgba(55,65,95,220);
                border:1px solid #00D4FF;
            }
        """)

        self.setMinimumHeight(160)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20,20,20,20)

        iconLabel = QLabel(icon)
        iconLabel.setAlignment(Qt.AlignCenter)
        iconLabel.setStyleSheet("font-size:34px;")

        titleLabel = QLabel(title)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("""
            color:#A8B3CF;
            font-size:16px;
        """)

        self.value = QLabel("--")
        self.value.setAlignment(Qt.AlignCenter)

        self.value.setStyleSheet("""
            color:#00D4FF;
            font-size:30px;
            font-weight:bold;
        """)

        layout.addWidget(iconLabel)
        layout.addWidget(titleLabel)
        layout.addWidget(self.value)


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("dashboard")

        main = QVBoxLayout(self)

        main.setContentsMargins(40,30,40,30)

        main.setSpacing(25)

        # ======================
        # TITLE
        # ======================

        title = QLabel("NOVA")

        title.setStyleSheet("""
            font-size:48px;
            font-weight:bold;
            color:#00D4FF;
        """)

        subtitle = QLabel("Artificial Intelligence Operating System")

        subtitle.setStyleSheet("""
            color:#8A94B2;
            font-size:18px;
        """)

        main.addWidget(title)
        main.addWidget(subtitle)

        # ======================
        # DASHBOARD CARDS
        # ======================

        cards = QHBoxLayout()

        cards.setSpacing(20)

        self.cpu = GlassCard("CPU", "🖥")
        self.ram = GlassCard("RAM", "💾")
        self.battery = GlassCard("Battery", "🔋")
        self.time = GlassCard("Time", "🕒")

        cards.addWidget(self.cpu)
        cards.addWidget(self.ram)
        cards.addWidget(self.battery)
        cards.addWidget(self.time)

        main.addLayout(cards)

        # ======================
        # TERMINAL
        # ======================

        terminalFrame = QFrame()

        terminalFrame.setStyleSheet("""
            QFrame{
                background:rgba(20,25,40,190);
                border-radius:20px;
                border:1px solid rgba(255,255,255,25);
            }
        """)

        terminalLayout = QVBoxLayout(terminalFrame)

        terminalTitle = QLabel("SYSTEM TERMINAL")

        terminalTitle.setStyleSheet("""
            color:#00D4FF;
            font-size:18px;
            font-weight:bold;
        """)

        terminalLayout.addWidget(terminalTitle)

        self.chat = QTextEdit()

        self.chat.setReadOnly(True)

        self.chat.setStyleSheet("""
            QTextEdit{
                background:transparent;
                border:none;
                color:white;
                font-size:15px;
                selection-background-color:#00D4FF;
            }
        """)

        self.chat.append("► NOVA initialized.")
        self.chat.append("► Ready.")

        terminalLayout.addWidget(self.chat)

        main.addWidget(terminalFrame)

        # ======================
        # TIMER
        # ======================

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_dashboard)

        self.timer.start(1000)

        self.update_dashboard()

    # ======================
    # UPDATE DASHBOARD
    # ======================

    def update_dashboard(self):

        self.cpu.value.setText(
            f"{psutil.cpu_percent()}%"
        )

        self.ram.value.setText(
            f"{psutil.virtual_memory().percent}%"
        )

        try:
            battery = psutil.sensors_battery()

            if battery:
                self.battery.value.setText(
                    f"{battery.percent}%"
                )
            else:
                self.battery.value.setText("N/A")

        except:
            self.battery.value.setText("N/A")

        self.time.value.setText(
            datetime.now().strftime("%H:%M:%S")
        )