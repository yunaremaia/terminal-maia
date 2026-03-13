"""Quote widget for displaying stock quotes."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

from typing import List, Optional
from mafin_terminal.data.providers import Quote


class QuoteWidget(QWidget):
    """Widget for displaying stock quotes."""
    
    quote_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_quote: Optional[Quote] = None
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.symbol_label = QLabel()
        self.symbol_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.symbol_label.setStyleSheet("color: #ff6600;")
        layout.addWidget(self.symbol_label)
        
        self.name_label = QLabel()
        self.name_label.setFont(QFont("Arial", 10))
        self.name_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.name_label)
        
        price_layout = QHBoxLayout()
        
        self.price_label = QLabel()
        self.price_label.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        self.price_label.setStyleSheet("color: #ffffff;")
        price_layout.addWidget(self.price_label)
        
        self.change_label = QLabel()
        self.change_label.setFont(QFont("Courier New", 12))
        price_layout.addWidget(self.change_label)
        
        price_layout.addStretch()
        layout.addLayout(price_layout)
        
        details_layout = QHBoxLayout()
        
        details = ["Open", "High", "Low", "Prev Close", "Volume"]
        self.detail_labels = {}
        
        for detail in details:
            vbox = QVBoxLayout()
            label = QLabel(detail)
            label.setFont(QFont("Arial", 8))
            label.setStyleSheet("color: #666666;")
            value = QLabel("-")
            value.setFont(QFont("Courier New", 10))
            value.setStyleSheet("color: #cccccc;")
            vbox.addWidget(label)
            vbox.addWidget(value)
            self.detail_labels[detail] = value
            details_layout.addLayout(vbox)
        
        details_layout.addStretch()
        layout.addLayout(details_layout)
        
        layout.addStretch()
    
    def set_quote(self, quote: Quote):
        """Set quote to display."""
        self._current_quote = quote
        
        self.symbol_label.setText(quote.symbol)
        self.name_label.setText(quote.name or "")
        self.price_label.setText(f"${quote.price:,.2f}")
        
        change_color = "#00ff00" if quote.change >= 0 else "#ff0000"
        sign = "+" if quote.change >= 0 else ""
        self.change_label.setText(
            f"<span style='color: {change_color}'>{sign}{quote.change:.2f} ({sign}{quote.change_percent:.2f}%)</span>"
        )
        
        self.detail_labels["Open"].setText(f"${quote.open_price:,.2f}")
        self.detail_labels["High"].setText(f"${quote.high:,.2f}")
        self.detail_labels["Low"].setText(f"${quote.low:,.2f}")
        self.detail_labels["Prev Close"].setText(f"${quote.previous_close:,.2f}")
        self.detail_labels["Volume"].setText(f"{quote.volume:,}")
    
    def clear(self):
        """Clear display."""
        self._current_quote = None
        self.symbol_label.setText("")
        self.name_label.setText("")
        self.price_label.setText("-")
        self.change_label.setText("")
        
        for label in self.detail_labels.values():
            label.setText("-")


class QuoteTableWidget(QWidget):
    """Widget for displaying multiple quotes in a table."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Change", "Chg %", "Volume"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                color: #cccccc;
                gridline-color: #333333;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #333333;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ff6600;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
    
    def set_quotes(self, quotes: List[Quote]):
        """Set quotes to display."""
        self.table.setRowCount(len(quotes))
        
        for row, quote in enumerate(quotes):
            self.table.setItem(row, 0, QTableWidgetItem(quote.symbol))
            self.table.setItem(row, 1, QTableWidgetItem(quote.name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(f"${quote.price:,.2f}"))
            
            change_color = "#00ff00" if quote.change >= 0 else "#ff0000"
            change_item = QTableWidgetItem(f"{quote.change:+,.2f}")
            change_item.setForeground(QColor(change_color))
            self.table.setItem(row, 3, change_item)
            
            pct_item = QTableWidgetItem(f"{quote.change_percent:+,.2f}%")
            pct_item.setForeground(QColor(change_color))
            self.table.setItem(row, 4, pct_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(f"{quote.volume:,}"))
        
        self.table.resizeColumnsToContents()
    
    def clear(self):
        """Clear table."""
        self.table.setRowCount(0)
