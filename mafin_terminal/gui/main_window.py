"""MaFin Terminal - Main GUI window with multi-monitor support."""

import asyncio
import sys
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QStackedWidget, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QGridLayout, QSplitter, QTextBrowser, QTabWidget,
    QComboBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal, QThread
from PyQt6.QtGui import QKeyEvent, QColor, QFont, QPalette, QIcon

from .monitor_detector import MonitorDetector, MonitorInfo
from .widgets import QuoteWidget, QuoteTableWidget, ChartWidget


class DataLoaderThread(QThread):
    """Background thread for loading data."""
    
    data_loaded = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, module_type: str, module, symbol: str = None):
        super().__init__()
        self.module_type = module_type
        self.module = module
        self.symbol = symbol
    
    def run(self):
        """Load data in background."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if self.module_type == 'quote':
                result = loop.run_until_complete(self.module.get_quote(self.symbol))
                self.data_loaded.emit('quote', result)
            
            elif self.module_type == 'quotes':
                result = loop.run_until_complete(self.module.get_multiple_quotes(self.symbol))
                self.data_loaded.emit('quotes', result)
            
            elif self.module_type == 'chart':
                result = loop.run_until_complete(self.module.get_historical(self.symbol, "1y"))
                self.data_loaded.emit('chart', result)
            
            elif self.module_type == 'technical':
                result = loop.run_until_complete(self.module.analyze(self.symbol))
                self.data_loaded.emit('technical', result)
            
            elif self.module_type == 'fundamental':
                result = loop.run_until_complete(self.module.analyze(self.symbol))
                self.data_loaded.emit('fundamental', result)
            
            elif self.module_type == 'economic':
                result = loop.run_until_complete(self.module.get_market_overview())
                self.data_loaded.emit('economic', result)
            
            elif self.module_type == 'news':
                result = loop.run_until_complete(self.module.get_market_news(20))
                self.data_loaded.emit('news', result)
            
            elif self.module_type == 'movers':
                result = loop.run_until_complete(self.module.get_market_movers())
                self.data_loaded.emit('movers', result)
        
        except Exception as e:
            self.error_occurred.emit(str(e))
        
        loop.close()


class NavigationButton(QPushButton):
    """Custom navigation button."""
    
    def __init__(self, text: str, icon: str = ""):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: none;
                padding: 10px;
                text-align: left;
                font-size: 13px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                color: #ff6600;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)


class MainWindow(QMainWindow):
    """Main window for MaFin Terminal with fullscreen multi-monitor support."""
    
    def __init__(self):
        super().__init__()
        
        self.monitor_detector = MonitorDetector()
        self.monitors = self.monitor_detector.get_all_monitors()
        
        self._modules = {}
        self._current_symbol = "AAPL"
        self._data_threads = []
        
        self._setup_window()
        self._setup_modules()
        self._setup_ui()
        self._apply_fullscreen()
        
        self._update_time()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
        
        self._load_initial_data()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("MaFin Terminal - Professional Financial Terminal")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #ff6600;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border-color: #ff6600;
            }
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
                color: #ff6600;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ff6600;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QTabWidget::pane {
                background-color: #1a1a1a;
                border: 1px solid #333333;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #cccccc;
                padding: 8px 15px;
                border: 1px solid #333333;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: #ff6600;
                border-bottom-color: #1a1a1a;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTextBrowser {
                background-color: #1a1a1a;
                color: #cccccc;
                border: none;
            }
        """)
    
    def _setup_modules(self):
        """Setup data modules."""
        try:
            from mafin_terminal.modules.market import MarketModule
            from mafin_terminal.modules.portfolio import PortfolioManager
            from mafin_terminal.modules.technical import TechnicalAnalysisModule
            from mafin_terminal.modules.fundamental import FundamentalModule
            from mafin_terminal.modules.risk import RiskAnalysisModule
            from mafin_terminal.modules.economic import EconomicModule
            from mafin_terminal.modules.news import NewsModule
            
            self._modules['market'] = MarketModule()
            self._modules['portfolio'] = PortfolioManager()
            self._modules['technical'] = TechnicalAnalysisModule()
            self._modules['fundamental'] = FundamentalModule()
            self._modules['risk'] = RiskAnalysisModule()
            self._modules['economic'] = EconomicModule()
            self._modules['news'] = NewsModule()
            
            portfolio = self._modules['portfolio'].create_portfolio("Default")
            portfolio.add_cash(100000)
            portfolio.buy("AAPL", 100, 150.0)
            portfolio.buy("MSFT", 50, 350.0)
            portfolio.buy("GOOGL", 20, 140.0)
            
        except Exception as e:
            print(f"Error loading modules: {e}")
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        content = self._create_content_area()
        main_layout.addWidget(content, 1)
    
    def _create_sidebar(self) -> QWidget:
        """Create sidebar navigation."""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #222222;
                border-right: 1px solid #333333;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        title = QLabel("MaFin Terminal")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff6600; padding: 10px;")
        layout.addWidget(title)
        
        layout.addWidget(self._create_separator())
        
        nav_buttons = [
            ("Dashboard", "home"),
            ("Quotes", "quote"),
            ("Charts", "chart"),
            ("Watchlist", "watch"),
            ("Portfolio", "portfolio"),
            ("Technical", "technical"),
            ("Fundamental", "fundamental"),
            ("Risk", "risk"),
            ("Economic", "economic"),
            ("News", "news"),
        ]
        
        self.nav_button_map = {}
        
        for text, key in nav_buttons:
            btn = NavigationButton(text)
            btn.clicked.connect(lambda checked, k=key: self._navigate_to(k))
            layout.addWidget(btn)
            self.nav_button_map[key] = btn
        
        layout.addStretch()
        
        layout.addWidget(self._create_separator())
        
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Symbol (e.g., AAPL)")
        self.symbol_input.setText("AAPL")
        self.symbol_input.returnPressed.connect(self._on_symbol_changed)
        layout.addWidget(self.symbol_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._on_symbol_changed)
        layout.addWidget(search_btn)
        
        return sidebar
    
    def _create_separator(self) -> QFrame:
        """Create a horizontal separator."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #333333;")
        sep.setFixedHeight(1)
        return sep
    
    def _create_content_area(self) -> QWidget:
        """Create main content area."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        header = QHBoxLayout()
        
        self.screen_title = QLabel("Dashboard")
        self.screen_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.screen_title.setStyleSheet("color: #ff6600;")
        header.addWidget(self.screen_title)
        
        header.addStretch()
        
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Courier New", 12))
        header.addWidget(self.time_label)
        
        layout.addLayout(header)
        
        layout.addWidget(self._create_separator())
        
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)
        
        self._create_dashboard_screen()
        self._create_quotes_screen()
        self._create_chart_screen()
        self._create_watchlist_screen()
        self._create_portfolio_screen()
        self._create_technical_screen()
        self._create_fundamental_screen()
        self._create_risk_screen()
        self._create_economic_screen()
        self._create_news_screen()
        
        return content
    
    def _create_dashboard_screen(self) -> QWidget:
        """Create dashboard screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        top_row = QHBoxLayout()
        
        self.dashboard_quote = QuoteWidget()
        top_row.addWidget(self.dashboard_quote, 1)
        
        market_widget = QWidget()
        market_layout = QVBoxLayout(market_widget)
        
        market_label = QLabel("Market Movers")
        market_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        market_label.setStyleSheet("color: #ff6600;")
        market_layout.addWidget(market_label)
        
        self.movers_table = QTableWidget()
        self.movers_table.setColumnCount(5)
        self.movers_table.setHorizontalHeaderLabels(["Symbol", "Price", "Change", "Chg %", "Volume"])
        self.movers_table.setMaximumHeight(200)
        market_layout.addWidget(self.movers_table)
        
        top_row.addWidget(market_widget, 1)
        
        layout.addLayout(top_row)
        
        bottom_row = QHBoxLayout()
        
        portfolio_widget = QWidget()
        portfolio_layout = QVBoxLayout(portfolio_widget)
        
        portfolio_label = QLabel("Portfolio Summary")
        portfolio_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        portfolio_label.setStyleSheet("color: #ff6600;")
        portfolio_layout.addWidget(portfolio_label)
        
        self.portfolio_summary = QLabel("Loading...")
        self.portfolio_summary.setFont(QFont("Courier New", 12))
        portfolio_layout.addWidget(self.portfolio_summary)
        
        bottom_row.addWidget(portfolio_widget, 1)
        
        news_widget = QWidget()
        news_layout = QVBoxLayout(news_widget)
        
        news_label = QLabel("Market News")
        news_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        news_label.setStyleSheet("color: #ff6600;")
        news_layout.addWidget(news_label)
        
        self.dashboard_news = QTextBrowser()
        self.dashboard_news.setMaximumHeight(200)
        news_layout.addWidget(self.dashboard_news)
        
        bottom_row.addWidget(news_widget, 1)
        
        layout.addLayout(bottom_row)
        
        layout.addStretch()
        
        self.content_stack.addWidget(widget)
    
    def _create_quotes_screen(self) -> QWidget:
        """Create quotes screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.quotes_table = QuoteTableWidget()
        layout.addWidget(self.quotes_table)
        
        self.content_stack.addWidget(widget)
    
    def _create_chart_screen(self) -> QWidget:
        """Create chart screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)
        
        self.content_stack.addWidget(widget)
    
    def _create_watchlist_screen(self) -> QWidget:
        """Create watchlist screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        controls = QHBoxLayout()
        
        add_label = QLabel("Add to Watchlist:")
        controls.addWidget(add_label)
        
        self.watchlist_input = QLineEdit()
        self.watchlist_input.setPlaceholderText("Symbol")
        self.watchlist_input.setFixedWidth(100)
        controls.addWidget(self.watchlist_input)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_to_watchlist)
        controls.addWidget(add_btn)
        
        controls.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_watchlist)
        controls.addWidget(refresh_btn)
        
        layout.addLayout(controls)
        
        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(7)
        self.watchlist_table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Change", "Chg %", "Volume", "Action"])
        layout.addWidget(self.watchlist_table)
        
        self.content_stack.addWidget(widget)
    
    def _create_portfolio_screen(self) -> QWidget:
        """Create portfolio screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        summary = QHBoxLayout()
        
        self.portfolio_total = QLabel("Total: $0.00")
        self.portfolio_total.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.portfolio_total.setStyleSheet("color: #ff6600;")
        summary.addWidget(self.portfolio_total)
        
        summary.addStretch()
        
        self.portfolio_pnl = QLabel("P&L: $0.00 (0.00%)")
        self.portfolio_pnl.setFont(QFont("Courier New", 12))
        summary.addWidget(self.portfolio_pnl)
        
        layout.addLayout(summary)
        
        layout.addWidget(self._create_separator())
        
        positions_label = QLabel("Positions")
        positions_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(positions_label)
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels(["Symbol", "Qty", "Avg Cost", "Current", "Market Value", "P&L", "P&L %"])
        layout.addWidget(self.positions_table)
        
        self.content_stack.addWidget(widget)
    
    def _create_technical_screen(self) -> QWidget:
        """Create technical analysis screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.technical_info = QTextBrowser()
        layout.addWidget(self.technical_info)
        
        self.content_stack.addWidget(widget)
    
    def _create_fundamental_screen(self) -> QWidget:
        """Create fundamental analysis screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.fundamental_info = QTextBrowser()
        layout.addWidget(self.fundamental_info)
        
        self.content_stack.addWidget(widget)
    
    def _create_risk_screen(self) -> QWidget:
        """Create risk analysis screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.risk_info = QTextBrowser()
        layout.addWidget(self.risk_info)
        
        self.content_stack.addWidget(widget)
    
    def _create_economic_screen(self) -> QWidget:
        """Create economic data screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.economic_tabs = QTabWidget()
        layout.addWidget(self.economic_tabs)
        
        self.content_stack.addWidget(widget)
    
    def _create_news_screen(self) -> QWidget:
        """Create news screen."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.news_browser = QTextBrowser()
        layout.addWidget(self.news_browser)
        
        self.content_stack.addWidget(widget)
    
    def _navigate_to(self, screen: str):
        """Navigate to a screen."""
        screens = {
            'home': 0,
            'quote': 1,
            'chart': 2,
            'watch': 3,
            'portfolio': 4,
            'technical': 5,
            'fundamental': 6,
            'risk': 7,
            'economic': 8,
            'news': 9,
        }
        
        if screen in screens:
            self.content_stack.setCurrentIndex(screens[screen])
            self._update_screen_title(screen)
            
            if screen == 'home':
                self._load_dashboard_data()
            elif screen == 'quote':
                self._load_quote_data()
            elif screen == 'chart':
                self._load_chart_data()
            elif screen == 'watch':
                self._refresh_watchlist()
            elif screen == 'portfolio':
                self._load_portfolio_data()
            elif screen == 'technical':
                self._load_technical_data()
            elif screen == 'fundamental':
                self._load_fundamental_data()
            elif screen == 'risk':
                self._load_risk_data()
            elif screen == 'economic':
                self._load_economic_data()
            elif screen == 'news':
                self._load_news_data()
    
    def _update_screen_title(self, screen: str):
        """Update screen title."""
        titles = {
            'home': 'Dashboard',
            'quote': 'Quotes',
            'chart': 'Charts',
            'watch': 'Watchlist',
            'portfolio': 'Portfolio',
            'technical': 'Technical Analysis',
            'fundamental': 'Fundamental Analysis',
            'risk': 'Risk Analysis',
            'economic': 'Economic Data',
            'news': 'Market News',
        }
        self.screen_title.setText(titles.get(screen, 'Dashboard'))
    
    def _load_initial_data(self):
        """Load initial data."""
        self._load_dashboard_data()
    
    def _load_dashboard_data(self):
        """Load dashboard data."""
        self._load_quote_data()
        self._load_portfolio_data()
        self._load_news_data()
    
    def _on_symbol_changed(self):
        """Handle symbol change."""
        symbol = self.symbol_input.text().strip().upper()
        if symbol:
            self._current_symbol = symbol
            self._load_quote_data()
            self._load_chart_data()
    
    def _load_quote_data(self):
        """Load quote data."""
        if 'market' not in self._modules:
            return
        
        thread = DataLoaderThread('quote', self._modules['market'], self._current_symbol)
        thread.data_loaded.connect(self._on_quote_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_quote_loaded(self, data_type: str, data):
        """Handle quote data loaded."""
        if data_type == 'quote' and data:
            self.dashboard_quote.set_quote(data)
    
    def _load_chart_data(self):
        """Load chart data."""
        if 'market' not in self._modules:
            return
        
        thread = DataLoaderThread('chart', self._modules['market'], self._current_symbol)
        thread.data_loaded.connect(self._on_chart_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_chart_loaded(self, data_type: str, data):
        """Handle chart data loaded."""
        if data_type == 'chart' and data:
            self.chart_widget.set_data(data)
            self.chart_widget.set_symbol(self._current_symbol)
    
    def _load_portfolio_data(self):
        """Load portfolio data."""
        if 'portfolio' not in self._modules:
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        portfolio = self._modules['portfolio'].get_default()
        loop.run_until_complete(portfolio.update_prices())
        
        summary = portfolio.get_summary()
        positions = portfolio.get_positions()
        
        self.portfolio_total.setText(f"Total: ${summary.total_value:,.2f}")
        
        pnl_color = "#00ff00" if summary.total_pnl >= 0 else "#ff0000"
        self.portfolio_pnl.setText(f"<span style='color: {pnl_color}'>P&L: ${summary.total_pnl:+,.2f} ({summary.total_pnl_percent:+,.2f}%)</span>")
        
        self.positions_table.setRowCount(len(positions))
        
        for row, pos in enumerate(positions):
            self.positions_table.setItem(row, 0, QTableWidgetItem(pos.symbol))
            self.positions_table.setItem(row, 1, QTableWidgetItem(f"{pos.quantity:.0f}"))
            self.positions_table.setItem(row, 2, QTableWidgetItem(f"${pos.avg_cost:,.2f}"))
            self.positions_table.setItem(row, 3, QTableWidgetItem(f"${pos.current_price:,.2f}"))
            self.positions_table.setItem(row, 4, QTableWidgetItem(f"${pos.market_value:,.2f}"))
            
            pnl_color = "#00ff00" if pos.unrealized_pnl >= 0 else "#ff0000"
            pnl_item = QTableWidgetItem(f"${pos.unrealized_pnl:+,.2f}")
            pnl_item.setForeground(QColor(pnl_color))
            self.positions_table.setItem(row, 5, pnl_item)
            
            pnl_pct_item = QTableWidgetItem(f"{pos.unrealized_pnl_percent:+,.2f}%")
            pnl_pct_item.setForeground(QColor(pnl_color))
            self.positions_table.setItem(row, 6, pnl_pct_item)
        
        self.positions_table.resizeColumnsToContents()
        
        loop.close()
    
    def _load_technical_data(self):
        """Load technical analysis data."""
        if 'technical' not in self._modules:
            return
        
        thread = DataLoaderThread('technical', self._modules['technical'], self._current_symbol)
        thread.data_loaded.connect(self._on_technical_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_technical_loaded(self, data_type: str, data):
        """Handle technical data loaded."""
        if data_type == 'technical' and data:
            html = f"""
            <h2 style='color: #ff6600;'>Technical Analysis - {data.symbol}</h2>
            <p><b>Current Price:</b> ${data.current_price:.2f}</p>
            
            <h3 style='color: #ff6600;'>Moving Averages</h3>
            <table>
                <tr><td>SMA 20:</td><td>${data.sma_20:.2f if data.sma_20 else 'N/A'}</td></tr>
                <tr><td>SMA 50:</td><td>${data.sma_50:.2f if data.sma_50 else 'N/A'}</td></tr>
                <tr><td>SMA 200:</td><td>${data.sma_200:.2f if data.sma_200 else 'N/A'}</td></tr>
                <tr><td>EMA 12:</td><td>${data.ema_12:.2f if data.ema_12 else 'N/A'}</td></tr>
                <tr><td>EMA 26:</td><td>${data.ema_26:.2f if data.ema_26 else 'N/A'}</td></tr>
            </table>
            
            <h3 style='color: #ff6600;'>Momentum</h3>
            <table>
                <tr><td>RSI (14):</td><td>{data.rsi:.2f if data.rsi else 'N/A'}</td></tr>
                <tr><td>MACD:</td><td>{data.macd:.4f if data.macd else 'N/A'}</td></tr>
                <tr><td>MACD Signal:</td><td>{data.macd_signal:.4f if data.macd_signal else 'N/A'}</td></tr>
                <tr><td>MACD Histogram:</td><td>{data.macd_histogram:.4f if data.macd_histogram else 'N/A'}</td></tr>
            </table>
            
            <h3 style='color: #ff6600;'>Volatility</h3>
            <table>
                <tr><td>BB Upper:</td><td>${data.bb_upper:.2f if data.bb_upper else 'N/A'}</td></tr>
                <tr><td>BB Middle:</td><td>${data.bb_middle:.2f if data.bb_middle else 'N/A'}</td></tr>
                <tr><td>BB Lower:</td><td>${data.bb_lower:.2f if data.bb_lower else 'N/A'}</td></tr>
                <tr><td>ATR:</td><td>{data.atr:.2f if data.atr else 'N/A'}</td></tr>
                <tr><td>ADX:</td><td>{data.adx:.2f if data.adx else 'N/A'}</td></tr>
            </table>
            """
            self.technical_info.setHtml(html)
    
    def _load_fundamental_data(self):
        """Load fundamental analysis data."""
        if 'fundamental' not in self._modules:
            return
        
        thread = DataLoaderThread('fundamental', self._modules['fundamental'], self._current_symbol)
        thread.data_loaded.connect(self._on_fundamental_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_fundamental_loaded(self, data_type: str, data):
        """Handle fundamental data loaded."""
        if data_type == 'fundamental' and data:
            profile = data.get('profile')
            metrics = data.get('metrics')
            analyst = data.get('analyst')
            
            html = f"<h2 style='color: #ff6600;'>Fundamental Analysis - {self._current_symbol}</h2>"
            
            if profile:
                html += f"""
                <h3 style='color: #ff6600;'>Company Profile</h3>
                <p><b>Name:</b> {profile.name}</p>
                <p><b>Industry:</b> {profile.industry}</p>
                <p><b>Sector:</b> {profile.sector}</p>
                <p><b>CEO:</b> {profile.ceo or 'N/A'}</p>
                """
            
            if metrics:
                html += """
                <h3 style='color: #ff6600;'>Key Metrics</h3>
                <table>
                """
                if metrics.market_cap:
                    html += f"<tr><td>Market Cap:</td><td>${metrics.market_cap:,.0f}</td></tr>"
                if metrics.pe_ratio:
                    html += f"<tr><td>P/E Ratio:</td><td>{metrics.pe_ratio:.2f}</td></tr>"
                if metrics.eps:
                    html += f"<tr><td>EPS:</td><td>${metrics.eps:.2f}</td></tr>"
                if metrics.dividend_yield:
                    html += f"<tr><td>Dividend Yield:</td><td>{metrics.dividend_yield * 100:.2f}%</td></tr>"
                if metrics.beta:
                    html += f"<tr><td>Beta:</td><td>{metrics.beta:.2f}</td></tr>"
                if metrics.roe:
                    html += f"<tr><td>ROE:</td><td>{metrics.roe * 100:.2f}%</td></tr>"
                if metrics.profit_margin:
                    html += f"<tr><td>Profit Margin:</td><td>{metrics.profit_margin * 100:.2f}%</td></tr>"
                html += "</table>"
            
            if analyst:
                html += f"""
                <h3 style='color: #ff6600;'>Analyst Ratings</h3>
                <p><b>Rating:</b> {analyst.rating}</p>
                <p><b>Target Price:</b> ${analyst.target_price if analyst.target_price else 'N/A'}</p>
                <p><b>High Target:</b> ${analyst.high_target if analyst.high_target else 'N/A'}</p>
                <p><b>Low Target:</b> ${analyst.low_target if analyst.low_target else 'N/A'}</p>
                """
            
            self.fundamental_info.setHtml(html)
    
    def _load_risk_data(self):
        """Load risk analysis data."""
        if 'risk' not in self._modules:
            return
        
        thread = DataLoaderThread('risk', self._modules['risk'], self._current_symbol)
        thread.data_loaded.connect(self._on_risk_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_risk_loaded(self, data_type: str, data):
        """Handle risk data loaded."""
        if data_type == 'risk' and data:
            html = f"""
            <h2 style='color: #ff6600;'>Risk Analysis - {self._current_symbol}</h2>
            <table>
                <tr><td>Volatility:</td><td>{data.volatility * 100:.2f}%</td></tr>
                <tr><td>Beta:</td><td>{data.beta if data.beta else 'N/A'}</td></tr>
                <tr><td>Sharpe Ratio:</td><td>{data.sharpe_ratio:.2f if data.sharpe_ratio else 'N/A'}</td></tr>
                <tr><td>Sortino Ratio:</td><td>{data.sortino_ratio:.2f if data.sortino_ratio else 'N/A'}</td></tr>
                <tr><td>Max Drawdown:</td><td>{data.max_drawdown * 100:.2f}%</td></tr>
                <tr><td>VaR (95%):</td><td>{data.var_95 * 100:.2f}%</td></tr>
                <tr><td>CVaR (95%):</td><td>{data.cvar_95 * 100:.2f if data.cvar_95 else 'N/A'}%</td></tr>
            </table>
            """
            self.risk_info.setHtml(html)
    
    def _load_economic_data(self):
        """Load economic data."""
        if 'economic' not in self._modules:
            return
        
        thread = DataLoaderThread('economic', self._modules['economic'])
        thread.data_loaded.connect(self._on_economic_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_economic_loaded(self, data_type: str, data):
        """Handle economic data loaded."""
        if data_type == 'economic' and data:
            self.economic_tabs.clear()
            
            for category, items in [('Indices', data.get('indices', [])), 
                                    ('Currencies', data.get('currencies', [])),
                                    ('Commodities', data.get('commodities', [])),
                                    ('Treasuries', data.get('treasuries', []))]:
                tab = QWidget()
                layout = QVBoxLayout(tab)
                
                table = QTableWidget()
                table.setColumnCount(4)
                table.setHorizontalHeaderLabels(["Symbol", "Name", "Price", "Change %"])
                table.setRowCount(len(items))
                
                for row, item in enumerate(items):
                    table.setItem(row, 0, QTableWidgetItem(item.symbol))
                    table.setItem(row, 1, QTableWidgetItem(item.name))
                    table.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
                    
                    change_color = "#00ff00" if item.change_percent >= 0 else "#ff0000"
                    change_item = QTableWidgetItem(f"{item.change_percent:+.2f}%")
                    change_item.setForeground(QColor(change_color))
                    table.setItem(row, 3, change_item)
                
                table.resizeColumnsToContents()
                layout.addWidget(table)
                self.economic_tabs.addTab(tab, category)
    
    def _load_news_data(self):
        """Load news data."""
        if 'news' not in self._modules:
            return
        
        thread = DataLoaderThread('news', self._modules['news'])
        thread.data_loaded.connect(self._on_news_loaded)
        thread.start()
        self._data_threads.append(thread)
    
    def _on_news_loaded(self, data_type: str, data):
        """Handle news data loaded."""
        if data_type == 'news' and data:
            html = "<h2 style='color: #ff6600;'>Market News</h2>"
            
            for item in data[:15]:
                html += f"""
                <p style='margin-bottom: 5px;'>
                    <b>{item.title}</b><br>
                    <span style='color: #888888; font-size: 11px;'>{item.publisher} - {item.published[:10] if item.published else ''}</span>
                </p>
                <hr style='border-color: #333333;'>
                """
            
            self.news_browser.setHtml(html)
            self.dashboard_news.setHtml(html[:2000] + "...")
    
    def _add_to_watchlist(self):
        """Add symbol to watchlist."""
        symbol = self.watchlist_input.text().strip().upper()
        if symbol and 'market' in self._modules:
            self._modules['market'].market_data.add_to_watchlist(symbol)
            self.watchlist_input.clear()
            self._refresh_watchlist()
    
    def _refresh_watchlist(self):
        """Refresh watchlist."""
        if 'market' not in self._modules:
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        quotes = loop.run_until_complete(
            self._modules['market'].market_data.get_watchlist_quotes()
        )
        
        self.watchlist_table.setRowCount(len(quotes))
        
        for row, quote in enumerate(quotes):
            self.watchlist_table.setItem(row, 0, QTableWidgetItem(quote.symbol))
            self.watchlist_table.setItem(row, 1, QTableWidgetItem(quote.name or ""))
            self.watchlist_table.setItem(row, 2, QTableWidgetItem(f"${quote.price:.2f}"))
            
            change_color = "#00ff00" if quote.change >= 0 else "#ff0000"
            change_item = QTableWidgetItem(f"{quote.change:+.2f}")
            change_item.setForeground(QColor(change_color))
            self.watchlist_table.setItem(row, 3, change_item)
            
            pct_item = QTableWidgetItem(f"{quote.change_percent:+.2f}%")
            pct_item.setForeground(QColor(change_color))
            self.watchlist_table.setItem(row, 4, pct_item)
            
            self.watchlist_table.setItem(row, 5, QTableWidgetItem(f"{quote.volume:,}"))
        
        self.watchlist_table.resizeColumnsToContents()
        
        loop.close()
    
    def _apply_fullscreen(self):
        """Apply fullscreen mode across all monitors."""
        combined = self.monitor_detector.get_combined_geometry()
        
        self.setGeometry(combined)
        self.showFullScreen()
        
        print(f"MaFin Terminal starting in fullscreen mode")
        print(f"Monitors detected: {len(self.monitors)}")
        for m in self.monitors:
            print(f"  Monitor {m.index + 1}: {m.width}x{m.height} at ({m.x}, {m.y})")
    
    def _update_time(self):
        """Update the time display."""
        current_time = QTime.currentTime()
        time_str = current_time.toString("HH:mm:ss")
        self.time_label.setText(f"Time: {time_str}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self._apply_fullscreen()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        print("MaFin Terminal shutting down...")
        
        for thread in self._data_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        
        event.accept()


def launch_terminal():
    """Launch the MaFin Terminal application."""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_terminal()
