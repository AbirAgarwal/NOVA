import sys

from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme

from main_window import MainWindow

app = QApplication(sys.argv)

setTheme(Theme.DARK)

window = MainWindow()
window.show()

sys.exit(app.exec())