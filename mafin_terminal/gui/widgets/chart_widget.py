"""Chart widget for displaying price charts."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush

from typing import Optional, List
from datetime import datetime


class ChartWidget(QWidget):
    """Simple chart widget for displaying price data."""
    
    timeframe_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._symbol = ""
        self._timeframe = "1y"
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QHBoxLayout()
        
        self.title_label = QLabel("Chart")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #ff6600;")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
        self.timeframe_combo.setCurrentText("1y")
        self.timeframe_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                padding: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.timeframe_combo.currentTextChanged.connect(self._on_timeframe_changed)
        header.addWidget(self.timeframe_combo)
        
        layout.addLayout(header)
        
        self.chart_area = QWidget()
        self.chart_area.setStyleSheet("background-color: #1a1a1a;")
        layout.addWidget(self.chart_area)
        
        info_layout = QHBoxLayout()
        
        self.ohlc_label = QLabel("O: -  H: -  L: -  C: -")
        self.ohlc_label.setFont(QFont("Courier New", 10))
        self.ohlc_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.ohlc_label)
        
        info_layout.addStretch()
        
        self.volume_label = QLabel("Vol: -")
        self.volume_label.setFont(QFont("Courier New", 10))
        self.volume_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(self.volume_label)
        
        layout.addLayout(info_layout)
    
    def _on_timeframe_changed(self, text: str):
        """Handle timeframe change."""
        self._timeframe = text
        self.timeframe_changed.emit(text)
    
    def set_data(self, data):
        """Set chart data."""
        self._data = data
        self.update()
    
    def set_symbol(self, symbol: str):
        """Set chart symbol."""
        self._symbol = symbol
        self.title_label.setText(f"Chart - {symbol}")
        self.update()
    
    def paintEvent(self, event):
        """Paint the chart."""
        super().paintEvent(event)
        
        if not self._data or not hasattr(self._data, 'close') or len(self._data.close) == 0:
            self._paint_empty()
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.chart_area.rect()
        chart_rect = rect.adjusted(10, 10, -10, -10)
        
        prices = self._data.close
        volumes = self._data.volume if hasattr(self._data, 'volume') else []
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        volume_max = max(volumes) if volumes else 1
        
        chart_height = int(chart_rect.height() * 0.7)
        volume_height = chart_rect.height() - chart_height
        
        candle_width = max(1, (chart_rect.width() / len(prices)) - 2)
        
        green_brush = QBrush(QColor(0, 180, 0))
        red_brush = QBrush(QColor(180, 0, 0))
        green_pen = QPen(QColor(0, 200, 0))
        red_pen = QPen(QColor(200, 0, 0))
        
        for i, (o, h, l, c) in enumerate(zip(
            self._data.open, self._data.high, self._data.low, self._data.close
        )):
            x = chart_rect.left() + (i * (candle_width + 2)) + candle_width // 2
            
            if i >= len(self._data.high) or i >= len(self._data.low):
                continue
            
            high_y = chart_rect.top() + int((1 - (self._data.high[i] - min_price) / price_range) * chart_height)
            low_y = chart_rect.top() + int((1 - (self._data.low[i] - min_price) / price_range) * chart_height)
            open_y = chart_rect.top() + int((1 - (o - min_price) / price_range) * chart_height)
            close_y = chart_rect.top() + int((1 - (c - min_price) / price_range) * chart_height)
            
            if c >= o:
                painter.setPen(green_pen)
                painter.setBrush(green_brush)
            else:
                painter.setPen(red_pen)
                painter.setBrush(red_brush)
            
            painter.drawLine(x, high_y, x, low_y)
            painter.drawRect(int(x - candle_width // 2), min(open_y, close_y), 
                           candle_width, max(1, abs(close_y - open_y)))
        
        if volumes:
            volume_pen = QPen(QColor(100, 100, 100, 100))
            painter.setPen(volume_pen)
            
            for i, vol in enumerate(volumes):
                x = chart_rect.left() + (i * (candle_width + 2))
                vol_h = int((vol / volume_max) * volume_height * 0.8)
                y = chart_rect.bottom() - vol_h
                painter.drawRect(int(x), y, int(candle_width), vol_h)
    
    def _paint_empty(self):
        """Paint empty chart placeholder."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.chart_area.rect()
        center_x = rect.center().x()
        center_y = rect.center().y()
        
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.drawText(center_x - 50, center_y, "No data available")


class MiniChartWidget(QWidget):
    """Mini chart for watchlist items."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._color = QColor(0, 180, 0)
        self.setMinimumHeight(30)
    
    def set_data(self, data, is_positive: bool = True):
        """Set mini chart data."""
        self._data = data
        self._color = QColor(0, 180, 0) if is_positive else QColor(180, 0, 0)
        self.update()
    
    def paintEvent(self, event):
        """Paint mini chart."""
        super().paintEvent(event)
        
        if not self._data or len(self._data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        prices = self._data[-20:] if len(self._data) > 20 else self._data
        min_p = min(prices)
        max_p = max(prices)
        range_p = max_p - min_p if max_p != min_p else 1
        
        pen = QPen(self._color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        points = []
        for i, price in enumerate(prices):
            x = rect.left() + (i / (len(prices) - 1)) * rect.width()
            y = rect.bottom() - ((price - min_p) / range_p) * rect.height()
            points.append((x, y))
        
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]), 
                           int(points[i+1][0]), int(points[i+1][1]))
