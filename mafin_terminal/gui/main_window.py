"""MaFin Terminal - Main GUI window with multi-monitor support."""

import sys
from typing import Optional

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QKeyEvent, QPainter, QColor, QFont

from .monitor_detector import MonitorDetector, MonitorInfo


class MainWindow(QMainWindow):
    """Main window for MaFin Terminal with fullscreen multi-monitor support."""
    
    def __init__(self):
        super().__init__()
        
        self.monitor_detector = MonitorDetector()
        self.monitors = self.monitor_detector.get_all_monitors()
        
        self._setup_window()
        self._setup_ui()
        self._apply_fullscreen()
        
        self._update_time()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("MaFin Terminal - Professional Financial Terminal")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #ff6600;
            }
            QLabel {
                color: #ff6600;
            }
        """)
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        self._create_welcome_screen()
        self._create_main_dashboard()
        
        self.stacked_widget.setCurrentIndex(0)
    
    def _create_welcome_screen(self):
        """Create the welcome screen showing monitor detection."""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        
        title = QLabel("MaFin Terminal")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Professional Financial Terminal")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        monitor_info = QLabel("Detecting monitors...")
        monitor_info.setFont(QFont("Courier New", 12))
        monitor_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(monitor_info)
        
        monitor_text = ""
        for monitor in self.monitors:
            primary = " (PRIMARY)" if monitor.is_primary else ""
            monitor_text += f"Monitor {monitor.index + 1}{primary}: {monitor.width}x{monitor.height}\n"
        
        combined = self.monitor_detector.get_combined_geometry()
        monitor_text += f"\nTotal Workspace: {combined.width()}x{combined.height()}"
        
        monitor_info.setText(monitor_text)
        
        layout.addSpacing(40)
        
        status = QLabel("Press ENTER to continue...")
        status.setFont(QFont("Arial", 14))
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)
        
        self.stacked_widget.addWidget(welcome_widget)
    
    def _create_main_dashboard(self):
        """Create the main dashboard screen."""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        header = QLabel("MaFin Terminal - Dashboard")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header)
        
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Courier New", 14))
        layout.addWidget(self.time_label)
        
        self.monitor_label = QLabel()
        self.monitor_label.setFont(QFont("Courier New", 12))
        layout.addWidget(self.monitor_label)
        
        info_text = f"Displaying on {len(self.monitors)} monitor(s)"
        combined = self.monitor_detector.get_combined_geometry()
        self.monitor_label.setText(f"{info_text} | Resolution: {combined.width()}x{combined.height()}")
        
        layout.addSpacing(20)
        
        placeholder = QLabel("Financial data modules will appear here...")
        placeholder.setFont(QFont("Arial", 14))
        layout.addWidget(placeholder)
        
        self.stacked_widget.addWidget(dashboard)
    
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
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.stacked_widget.currentIndex() == 0:
                self.stacked_widget.setCurrentIndex(1)
        elif event.key() == Qt.Key.Key_Escape:
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
