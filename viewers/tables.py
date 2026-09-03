"""!
@file viewers/tables.py
@brief Viewers for tabular data (CSV, Excel).
"""

import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt

from viewers.base import BaseViewerWidget
from viewers.factory import ViewerFactory

@ViewerFactory.register([".csv", ".tsv", ".xlsx"])
class TableViewerWidget(BaseViewerWidget):
    """!
    @brief Viewer for displaying tabular data (CSV, TSV, Excel) using QTableWidget.
    """
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.table_widget = QTableWidget(self)
        self.layout.addWidget(self.table_widget)
        
        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.error_label)
        self.error_label.hide()
        
    def load_file(self, filepath: str) -> bool:
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
            
            self.error_label.hide()
            self.table_widget.show()
            return True
            
        except Exception as e:
            self.table_widget.hide()
            self.error_label.setText(f"Ошибка загрузки таблицы:\n{e}")
            self.error_label.show()
            return False
