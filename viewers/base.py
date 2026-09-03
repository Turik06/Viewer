"""!
@file viewers/base.py
@brief Abstract base class and common components for file viewer widgets.
"""

from abc import ABCMeta, abstractmethod
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ViewerMeta(type(QWidget), ABCMeta):
    """!
    @brief Metaclass resolving PyQt QWidget and abc.ABCMeta conflict.
    @details Ensures abstract base classes derived from QWidget can properly
             utilize abc.abstractmethod without metaclass conflicts in Python.
    """
    pass


class BaseViewerWidget(QWidget, metaclass=ViewerMeta):
    """!
    @brief Abstract base class for all file viewer widgets.
    @details Defines the unified interface for loading, displaying, and clearing
             content inside the Universal File Viewer. Subclasses must implement
             the load_file method.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize base viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._current_filepath: str | None = None

    @property
    def current_filepath(self) -> str | None:
        """!
        @brief Get currently loaded file path.
        @return File path string or None if no file is currently loaded.
        """
        return self._current_filepath

    @abstractmethod
    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load and display file content.
        @param filepath Path to the file to open.
        @return True if file was loaded successfully, False otherwise.
        """
        pass

    def clear(self) -> None:
        """!
        @brief Clear viewer content and reset state.
        @details Default implementation resets current filepath. Subclasses should
                 override this to clear their respective UI controls.
        """
        self._current_filepath = None


class MessageViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for displaying informational or error messages.
    @details Used when a file format is unsupported, a file cannot be read,
             or an informative placeholder is needed.
    """

    def __init__(
        self,
        message: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """!
        @brief Initialize message viewer widget.
        @param message Initial message text to display.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self._layout.addWidget(self.label)

    def set_message(self, message: str) -> None:
        """!
        @brief Update displayed message.
        @param message New message string.
        """
        self.label.setText(message)

    def message(self) -> str:
        """!
        @brief Get currently displayed message.
        @return Current message string.
        """
        return self.label.text()

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Handler for load_file on message viewer.
        @param filepath Path to the file.
        @return Always False as this widget only presents messages.
        """
        self._current_filepath = filepath
        return False

    def clear(self) -> None:
        """!
        @brief Reset message text and file path.
        """
        super().clear()
        self.label.clear()
