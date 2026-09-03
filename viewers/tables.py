"""!
@file viewers/tables.py
@brief Viewers for tabular data (CSV, TSV, Excel).
@details Provides a viewer widget that loads CSV, TSV and Excel files
         using pandas and displays them in a QTableWidget.
"""

import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt

from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory


@ViewerFactory.register([".csv", ".tsv", ".xlsx"])
class TableViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer widget for displaying tabular data files.
    @details Supports CSV, TSV and Excel (.xlsx) files. Uses pandas to read
             the data into a DataFrame and renders it in a QTableWidget with
             proper column headers. All cells are read-only.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """!
        @brief Initialize table viewer widget.
        @param parent Optional parent widget.
        """
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.table_widget = QTableWidget(self)
        self._layout.addWidget(self.table_widget)

        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.error_label)
        self.error_label.hide()

    def load_file(self, filepath: str) -> bool:
        """!
        @brief Load a tabular data file and display its contents.
        @details Reads CSV, TSV or Excel files using pandas. The resulting
                 DataFrame is rendered into a QTableWidget with column headers
                 preserved. NaN values are displayed as empty strings.
        @param filepath Path to the data file to open.
        @return True if file was loaded successfully, False otherwise.
        """
        try:
            if filepath.lower().endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.lower().endswith('.tsv'):
                df = pd.read_csv(filepath, sep='\t')
            elif filepath.lower().endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                raise ValueError("Неподдерживаемый формат таблицы")

            self.table_widget.clear()
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels([str(c) for c in df.columns])

            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    # Handle NaN values
                    val = df.iat[row, col]
                    item_text = "" if pd.isna(val) else str(val)
                    item = QTableWidgetItem(item_text)
                    # Make cells read-only for viewer
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    self.table_widget.setItem(row, col, item)

            self._current_filepath = filepath
            self.error_label.hide()
            self.table_widget.show()
            return True

        except Exception as e:
            self._current_filepath = filepath
            self.table_widget.hide()
            self.error_label.setText(f"Ошибка загрузки таблицы:\n{e}")
            self.error_label.show()
            return False

    def clear(self) -> None:
        """!
        @brief Clear viewer content and reset table state.
        """
        super().clear()
        self.table_widget.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.error_label.hide()
