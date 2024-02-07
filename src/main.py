import sys

from PySide6.QtWidgets import QApplication

from config import settings
from gui.main_window import ApplicationWindow

if __name__ == "__main__":
    q_app = QApplication.instance()
    if not q_app:
        q_app = QApplication(sys.argv)
    q_app.setApplicationName(settings.NAME)
    q_app.setApplicationVersion(settings.VERSION)

    app = ApplicationWindow()
    app.setWindowTitle(f"{settings.NAME} ({settings.VERSION})")
    app.show()
    app.activateWindow()
    app.raise_()
    q_app.exec()
