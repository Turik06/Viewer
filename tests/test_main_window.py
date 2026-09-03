"""!
@file test_main_window.py
@brief Unit tests for MainWindow components.
"""

import os
import unittest
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QApplication, QSplitter, QStackedWidget, QTreeView
from main_window import MainWindow

# Ensure Qt can run in headless / CI environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"


class TestMainWindow(unittest.TestCase):
    """!
    @brief Test cases for verifying MainWindow layout and widgets.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """!
        @brief Initialize QApplication once for all tests.
        """
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        """!
        @brief Create a fresh MainWindow instance before each test.
        """
        self.window = MainWindow()

    def tearDown(self) -> None:
        """!
        @brief Clean up the window after each test.
        """
        self.window.close()

    def test_splitter_structure(self) -> None:
        """!
        @brief Verify that central widget is a horizontal QSplitter with two panels.
        """
        self.assertIsInstance(self.window.centralWidget(), QSplitter)
        self.assertEqual(self.window.splitter.count(), 2)

    def test_left_panel_stacked_widget(self) -> None:
        """!
        @brief Verify that left panel contains QStackedWidget with initial placeholder.
        """
        self.assertIsInstance(self.window.stacked_widget, QStackedWidget)
        self.assertGreaterEqual(self.window.stacked_widget.count(), 1)
        self.assertIsNotNone(self.window.placeholder_widget)

    def test_right_panel_tree_view(self) -> None:
        """!
        @brief Verify that right panel contains QTreeView connected to QFileSystemModel.
        """
        self.assertIsInstance(self.window.tree_view, QTreeView)
        self.assertIsInstance(self.window.file_model, QFileSystemModel)
        self.assertEqual(self.window.tree_view.model(), self.window.file_model)

    def test_set_root_path(self) -> None:
        """!
        @brief Verify that set_root_path updates model and tree root index.
        """
        cwd = os.getcwd()
        self.window.set_root_path(cwd)
        self.assertEqual(self.window.file_model.rootPath(), cwd)


if __name__ == "__main__":
    unittest.main()
