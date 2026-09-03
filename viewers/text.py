"""!
@file viewers/text.py
@brief Text file viewer.
"""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QPlainTextEdit
from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory


@ViewerFactory.register([
    ".txt", ".md", ".py", ".cpp", ".h", ".php", ".sql", ".sh",
    ".json", ".xml", ".yaml", ".yml", ".ini", "Dockerfile", "Makefile"
])
class TextViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for text and code files.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        
        # Monospaced font
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)
        
        self._layout.addWidget(self.text_edit)
        
    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load and display text file content.
        @param filepath Path to the file to open.
        @return True if file was loaded successfully, False otherwise.
        """
        encodings = ['utf-8', 'cp1251']
        content = None
        
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.text_edit.setPlainText(f"Не удалось открыть файл:\n{str(e)}")
                self._current_filepath = filepath
                return False
                
        if content is not None:
            self.text_edit.setPlainText(content)
            self._current_filepath = filepath
            return True
        else:
            self.text_edit.setPlainText("Неподдерживаемая кодировка или битый файл")
            self._current_filepath = filepath
            return False

    def clear(self):
        """!
        @brief Clear viewer content.
        """
        super().clear()
        self.text_edit.clear()
