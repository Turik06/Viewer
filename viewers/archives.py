"""!
@file viewers/archives.py
@brief Viewers for archive files (ZIP, TAR, GZ).
@details Provides a viewer widget that lists the contents of archive files
         without extracting them, using the standard library zipfile and
         tarfile modules.
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
    @brief Viewer widget for displaying the contents of archive files.
    @details Supports ZIP, TAR and GZ archives. Lists files contained in
             the archive in a QTreeWidget with their names and sizes, without
             actually extracting any data.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize archive viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(["Имя файла", "Размер (байт)"])
        self._layout.addWidget(self.tree_widget)

        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.error_label)
        self.error_label.hide()

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load an archive file and display its contents list.
        @details Detects the archive type (ZIP or TAR/GZ) and lists all
                 contained files with their names and sizes. For raw .gz files
                 that are not tar archives, a single entry is displayed.
        @param filepath Path to the archive file to open.
        @return True if file was loaded successfully, False otherwise.
        """
        self._current_filepath = filepath
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

    def clear(self) -> None:
        """!
        @brief Clear viewer content and reset tree widget.
        """
        super().clear()
        self.tree_widget.clear()
        self.error_label.hide()
