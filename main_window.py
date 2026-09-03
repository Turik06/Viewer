"""!
@file main_window.py
@brief Main window module containing the MainWindow class.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QMainWindow, QSplitter, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """!
    @brief Main application window for Universal File Viewer.
    @details Implements a main window with a horizontal QSplitter dividing
             the viewer panel on the left and the file tree panel on the right.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize the main window and its UI components.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Universal File Viewer")
        self.resize(1024, 768)

        self._init_ui()

    def _init_ui(self) -> None:
        """!
        @brief Initialize layout with a horizontal QSplitter separating left and right panels.
        """
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(self.splitter)

        # Left panel: Viewer panel (placeholder for QStackedWidget)
        self.left_panel = QFrame(self)
        self.left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        self.left_placeholder_label = QLabel("Окно просмотра (Viewer Panel)", self.left_panel)
        self.left_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.left_placeholder_label)

        # Right panel: File tree panel (placeholder for QTreeView + QFileSystemModel)
        self.right_panel = QFrame(self)
        self.right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(self.right_panel)
        self.right_placeholder_label = QLabel("Дерево файлов (File Tree)", self.right_panel)
        self.right_placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.right_placeholder_label)

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # Viewer panel gets priority when resizing (stretch factor: left=3, right=1)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([750, 250])
