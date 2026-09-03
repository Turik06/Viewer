"""!
@file viewers/image.py
@brief Image file viewer.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImageReader
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QSizePolicy
from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory


@ViewerFactory.register([
    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg", ".webp", ".tiff", ".ico"
])
class ImageViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for image files.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Background color to look nicer for images
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #2e2e2e; }")
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)
        
        self.scroll_area.setWidget(self.image_label)
        self._layout.addWidget(self.scroll_area)
        
        self._pixmap = None
        self._scale_factor = 1.0

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load and display image file content.
        @param filepath Path to the file to open.
        @return True if file was loaded successfully, False otherwise.
        """
        try:
            reader = QImageReader(filepath)
            reader.setAutoTransform(True)
            image = reader.read()
            if image.isNull():
                self.image_label.setText(f"Не удалось прочитать изображение:\n{reader.errorString()}")
                self.image_label.adjustSize()
                self._current_filepath = filepath
                return False
                
            self._pixmap = QPixmap.fromImage(image)
            self._scale_factor = 1.0
            
            self._fit_to_window()
            
            self._current_filepath = filepath
            return True
        except Exception as e:
            self.image_label.setText(f"Ошибка при открытии файла:\n{str(e)}")
            self.image_label.adjustSize()
            self._current_filepath = filepath
            return False

    def _fit_to_window(self):
        """!
        @brief Scale image to fit the scroll area viewport.
        """
        if self._pixmap is None or self._pixmap.isNull():
            return
            
        view_size = self.scroll_area.viewport().size()
        pixmap_size = self._pixmap.size()
        
        if pixmap_size.width() == 0 or pixmap_size.height() == 0:
            return

        scale_w = view_size.width() / pixmap_size.width()
        scale_h = view_size.height() / pixmap_size.height()
        scale = min(scale_w, scale_h)
        
        if scale > 1.0:
            scale = 1.0
            
        self._scale_factor = scale
        self._apply_scale()

    def _apply_scale(self):
        """!
        @brief Apply the current scale factor to the image label.
        """
        if self._pixmap:
            new_size = self._pixmap.size() * self._scale_factor
            self.image_label.resize(new_size)
            self.image_label.setPixmap(self._pixmap)

    def resizeEvent(self, event):
        """!
        @brief Handle widget resize events.
        """
        super().resizeEvent(event)
        self._fit_to_window()

    def clear(self):
        """!
        @brief Clear viewer content.
        """
        super().clear()
        self.image_label.clear()
        self.image_label.adjustSize()
        self._pixmap = None
