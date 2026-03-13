"""MaFin Terminal - Multi-monitor detection module."""

from dataclasses import dataclass
from typing import List
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QScreen
from PyQt6.QtGui import QGuiApplication


@dataclass
class MonitorInfo:
    """Information about a single monitor."""
    index: int
    x: int
    y: int
    width: int
    height: int
    name: str
    is_primary: bool
    
    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"
    
    @property
    def geometry(self) -> QRect:
        return QRect(self.x, self.y, self.width, self.height)


class MonitorDetector:
    """Detects connected monitors and their resolutions."""
    
    def __init__(self):
        self._app = QApplication.instance()
        if self._app is None:
            self._app = QApplication(sys.argv)
        else:
            if not isinstance(self._app, QApplication):
                self._app = QApplication(sys.argv)
        self._screens = self._app.screens()
        self._primary_screen = QGuiApplication.primaryScreen()
    
    def get_monitor_count(self) -> int:
        """Return the number of connected monitors."""
        return len(self._screens)
    
    def get_primary_monitor(self) -> MonitorInfo:
        """Return information about the primary monitor."""
        for i, screen in enumerate(self._screens):
            if screen == self._primary_screen:
                return self._get_monitor_info(i)
        return self._get_monitor_info(0)
    
    def get_all_monitors(self) -> List[MonitorInfo]:
        """Return information about all connected monitors."""
        monitors = []
        for i in range(len(self._screens)):
            monitors.append(self._get_monitor_info(i))
        return monitors
    
    def get_combined_geometry(self) -> QRect:
        """Return the combined geometry of all monitors."""
        combined = QRect()
        for screen in self._screens:
            geom = screen.geometry()
            combined = combined.united(geom)
        return combined
    
    def _get_monitor_info(self, index: int) -> MonitorInfo:
        """Get detailed information about a specific monitor."""
        screen = self._screens[index]
        geometry = screen.geometry()
        available_geometry = screen.availableGeometry()
        
        name = screen.name() if hasattr(screen, 'name') else f"Monitor {index + 1}"
        
        primary_screen = QGuiApplication.primaryScreen()
        is_primary = screen == primary_screen
        
        return MonitorInfo(
            index=index,
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            name=name,
            is_primary=is_primary
        )
    
    def print_monitor_info(self) -> List[MonitorInfo]:
        """Print information about all detected monitors."""
        monitors = self.get_all_monitors()
        print("=" * 60)
        print("MaFin Terminal - Monitor Detection")
        print("=" * 60)
        print(f"Total monitors detected: {len(monitors)}")
        print("-" * 60)
        
        for monitor in monitors:
            primary_str = " (PRIMARY)" if monitor.is_primary else ""
            print(f"Monitor {monitor.index + 1}{primary_str}:")
            print(f"  Name: {monitor.name}")
            print(f"  Resolution: {monitor.width} x {monitor.height}")
            print(f"  Position: ({monitor.x}, {monitor.y})")
            print()
        
        combined = self.get_combined_geometry()
        print("-" * 60)
        print(f"Combined workspace: {combined.width()} x {combined.height()}")
        print("=" * 60)
        
        return monitors


def get_monitor_info() -> List[MonitorInfo]:
    """Convenience function to get monitor information."""
    detector = MonitorDetector()
    return detector.get_all_monitors()


if __name__ == "__main__":
    detector = MonitorDetector()
    detector.print_monitor_info()
