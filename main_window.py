"""!
@file main_window.py
@brief Main window module containing the MainWindow class.
"""

from PyQt6.QtCore import QDir, Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QFileSystemModel
from viewers.factory import ViewerFactory
from viewers.base import MessageViewerWidget
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """!
    @brief Main application window for Universal File Viewer.
    @details Implements a main window with a horizontal QSplitter dividing
             the viewer panel (QStackedWidget) on the left and the file tree panel
             (QTreeView + QFileSystemModel) on the right.
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

        # Left panel: Viewer panel containing QStackedWidget
        self.left_panel = QFrame(self)
        self.left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget(self.left_panel)
        self.stacked_widget.setObjectName("stackedWidget")

        # Default placeholder view in QStackedWidget
        self.placeholder_widget = QWidget(self.stacked_widget)
        self.placeholder_widget.setObjectName("placeholderWidget")
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_label = QLabel("Выберите файл для просмотра", self.placeholder_widget)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.placeholder_label)

        self.stacked_widget.addWidget(self.placeholder_widget)
        left_layout.addWidget(self.stacked_widget)

        # Right panel: File tree panel (QTreeView + QFileSystemModel)
        self.right_panel = QFrame(self)
        self.right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.file_model = QFileSystemModel(self)
        current_path = QDir.currentPath()
        self.file_model.setRootPath(current_path)

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.file_model)

        self.tree_view = QTreeView(self.right_panel)
        self.tree_view.setObjectName("treeView")
        self.tree_view.setModel(self.proxy_model)
        
        # Enable sorting and set root index
        self.tree_view.setSortingEnabled(True)
        source_root_index = self.file_model.index(current_path)
        proxy_root_index = self.proxy_model.mapFromSource(source_root_index)
        self.tree_view.setRootIndex(proxy_root_index)
        self.tree_view.setAnimated(True)

        self.tree_view.clicked.connect(self._on_tree_clicked)

        right_layout.addWidget(self.tree_view)

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # Viewer panel gets priority when resizing (stretch factor: left=3, right=1)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([750, 250])

    def set_root_path(self, path: str) -> None:
        """!
        @brief Set the root path for the file tree model and view.
        @param path Filesystem path to display in the tree view.
        """
        source_root_index = self.file_model.setRootPath(path)
        proxy_root_index = self.proxy_model.mapFromSource(source_root_index)
        self.tree_view.setRootIndex(proxy_root_index)


    def _on_tree_clicked(self, index: QModelIndex) -> None:
        """!
        @brief Handle click on file tree item.
        @param index Proxy model index of the clicked item.
        """
        source_index = self.proxy_model.mapToSource(index)
        if not source_index.isValid():
            return
            
        file_info = self.file_model.fileInfo(source_index)
        if not file_info.isFile():
            return
            
        filepath = file_info.absoluteFilePath()
        
        # Clear existing viewer widget if it's not the placeholder
        current_widget = self.stacked_widget.currentWidget()
        if current_widget is not self.placeholder_widget:
            self.stacked_widget.removeWidget(current_widget)
            current_widget.deleteLater()
            
        viewer = ViewerFactory.create_viewer_or_fallback(filepath, self.stacked_widget)
        
        try:
            viewer.load_file(filepath)
        except Exception as e:
            viewer.deleteLater()
            viewer = MessageViewerWidget(f"Не удалось открыть файл:\n{e}", self.stacked_widget)
            
        self.stacked_widget.addWidget(viewer)
        self.stacked_widget.setCurrentWidget(viewer)
