"""!
@file viewers/archives.py
@brief Viewers for archive files (ZIP, TAR, GZ).
"""

import zipfile
import tarfile
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import Qt

from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory

@ViewerFactory.register([".zip", ".tar", ".gz", ".tar.gz"])
class ArchiveViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer for displaying contents of archive files.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Имя файла", "Размер (байт)"])
        self.layout.addWidget(self.tree_widget)
        
        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.error_label)
        self.error_label.hide()
        
    def load_file(self, filepath: str) -> bool:
        self.tree_widget.clear()
        try:
            if zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zf:
                    for info in zf.infolist():
                        item = QTreeWidgetItem([info.filename, str(info.file_size)])
                        self.tree_widget.addTopLevelItem(item)
            elif tarfile.is_tarfile(filepath):
                with tarfile.open(filepath, 'r:*') as tf:
                    for info in tf.getmembers():
                        item = QTreeWidgetItem([info.name, str(info.size)])
                        self.tree_widget.addTopLevelItem(item)
            else:
                # Handle raw .gz file that is not a tarball
                if filepath.lower().endswith('.gz') and not filepath.lower().endswith('.tar.gz'):
                    item = QTreeWidgetItem([filepath, "Сжатый файл"])
                    self.tree_widget.addTopLevelItem(item)
                else:
                    raise ValueError("Неподдерживаемый формат архива")
            
            self.error_label.hide()
            self.tree_widget.show()
            return True
            
        except Exception as e:
            self.tree_widget.hide()
            self.error_label.setText(f"Ошибка чтения архива:\n{e}")
            self.error_label.show()
            return False
