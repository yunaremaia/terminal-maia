"""MaFin Terminal GUI package."""

from .monitor_detector import MonitorDetector, MonitorInfo, get_monitor_info
from .main_window import MainWindow, launch_terminal

__all__ = [
    "MonitorDetector",
    "MonitorInfo", 
    "get_monitor_info",
    "MainWindow",
    "launch_terminal",
]
