"""!
@file viewers/document.py
@brief Document viewer widgets for .docx and .pdf files.
"""

import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextBrowser, QScrollArea
)

try:
    import docx
except ImportError:
    docx = None

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    fitz = None

from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory


@ViewerFactory.register([".docx"])
class DocxViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for displaying Microsoft Word (.docx) documents.
    @details Extracts text from the document using python-docx and displays
             it in a QTextBrowser.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize DOCX viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(True)
        self._layout.addWidget(self._text_browser)

        if docx is None:
            self._text_browser.setText("Ошибка: библиотека 'python-docx' не установлена.")

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load a .docx file and display its text.
        @param filepath Path to the .docx file.
        @return True if loaded successfully, False otherwise.
        """
        self._current_filepath = filepath
        
        if docx is None:
            return False

        try:
            doc = docx.Document(filepath)
            html_content = ""
            for para in doc.paragraphs:
                # Basic formatting: just text and simple paragraphs.
                # Rich formatting could be extracted but this is a simple text dump.
                html_content += f"<p>{para.text}</p>"
            
            self._text_browser.setHtml(html_content)
            return True
        except Exception as e:
            self._text_browser.setText(f"Не удалось открыть файл: {e}")
            return False

    def clear(self) -> None:
        """!
        @brief Clear viewer content.
        """
        super().clear()
        self._text_browser.clear()


@ViewerFactory.register([".pdf"])
class PdfViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for displaying PDF documents.
    @details Renders PDF pages to images using PyMuPDF (fitz) and displays
             them with navigation controls.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize PDF viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for page image
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_area.setWidget(self._image_label)
        
        self._layout.addWidget(self._scroll_area, stretch=1)

        # Controls
        self._controls_layout = QHBoxLayout()
        self._controls_layout.setContentsMargins(5, 5, 5, 5)
        
        self._prev_btn = QPushButton("Пред. страница")
        self._prev_btn.clicked.connect(self._prev_page)
        
        self._page_label = QLabel("0 / 0")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._next_btn = QPushButton("След. страница")
        self._next_btn.clicked.connect(self._next_page)

        self._controls_layout.addWidget(self._prev_btn)
        self._controls_layout.addWidget(self._page_label)
        self._controls_layout.addWidget(self._next_btn)
        
        self._layout.addLayout(self._controls_layout)

        self._doc = None
        self._current_page = 0
        self._total_pages = 0

        if fitz is None:
            self._image_label.setText("Ошибка: библиотека 'PyMuPDF' не установлена.")

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load a .pdf file and display the first page.
        @param filepath Path to the .pdf file.
        @return True if loaded successfully, False otherwise.
        """
        self._current_filepath = filepath
        
        if fitz is None:
            return False

        try:
            if self._doc is not None:
                self._doc.close()
            self._doc = fitz.open(filepath)
            self._total_pages = len(self._doc)
            self._current_page = 0
            
            if self._total_pages > 0:
                self._render_page()
            else:
                self._image_label.setText("Документ пуст.")
            
            return True
        except Exception as e:
            self._image_label.setText(f"Не удалось открыть PDF: {e}")
            self._doc = None
            return False

    def _render_page(self) -> None:
        """!
        @brief Render the current page to QImage and show it.
        """
        if self._doc is None or self._current_page < 0 or self._current_page >= self._total_pages:
            return

        page = self._doc.load_page(self._current_page)
        
        # Increase resolution slightly (e.g., zoom factor 2)
        zoom_matrix = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert PyMuPDF pixmap to QImage
        img_format = QImage.Format.Format_RGB888
        if pix.alpha:
            img_format = QImage.Format.Format_RGBA8888
            
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        pixmap = QPixmap.fromImage(qimage)
        
        self._image_label.setPixmap(pixmap)
        self._update_controls()

    def _update_controls(self) -> None:
        """!
        @brief Update pagination controls and label.
        """
        self._page_label.setText(f"{self._current_page + 1} / {self._total_pages}")
        self._prev_btn.setEnabled(self._current_page > 0)
        self._next_btn.setEnabled(self._current_page < self._total_pages - 1)

    def _prev_page(self) -> None:
        """!
        @brief Navigate to the previous page.
        """
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def _next_page(self) -> None:
        """!
        @brief Navigate to the next page.
        """
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._render_page()

    def clear(self) -> None:
        """!
        @brief Clear viewer content and close document.
        """
        super().clear()
        if self._doc is not None:
            self._doc.close()
            self._doc = None
        self._image_label.clear()
        self._page_label.setText("0 / 0")
        self._prev_btn.setEnabled(False)
        self._next_btn.setEnabled(False)
