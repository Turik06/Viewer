"""!
@file main.py
@brief Application entry point for Universal File Viewer.
"""

import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main() -> None:
    """!
    @brief Application entry point.
    @details Initializes the Qt application, displays MainWindow, and runs the event loop.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
