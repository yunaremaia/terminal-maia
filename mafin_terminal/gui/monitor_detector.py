"""MaFin Terminal - Multi-monitor detection module."""

from dataclasses import dataclass
from typing import List
import sys

from PyQt6.QtWidgets import QApplication, QDesktopWidget
from PyQt6.QtCore import QRect


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
        self._desktop = QDesktopWidget()
    
    def get_monitor_count(self) -> int:
        """Return the number of connected monitors."""
        return self._desktop.screenCount()
    
    def get_primary_monitor(self) -> MonitorInfo:
        """Return information about the primary monitor."""
        primary_index = self._desktop.primaryScreen()
        return self._get_monitor_info(primary_index)
    
    def get_all_monitors(self) -> List[MonitorInfo]:
        """Return information about all connected monitors."""
        monitors = []
        for i in range(self._desktop.screenCount()):
            monitors.append(self._get_monitor_info(i))
        return monitors
    
    def get_combined_geometry(self) -> QRect:
        """Return the combined geometry of all monitors."""
        combined = QRect()
        for i in range(self._desktop.screenCount()):
            geom = self._desktop.screenGeometry(i)
            combined = combined.united(geom)
        return combined
    
    def _get_monitor_info(self, index: int) -> MonitorInfo:
        """Get detailed information about a specific monitor."""
        geometry = self._desktop.screenGeometry(index)
        available_geometry = self._desktop.availableGeometry(index)
        
        name = self._desktop.screen(index).name() if hasattr(self._desktop.screen(index), 'name') else f"Monitor {index + 1}"
        
        is_primary = index == self._desktop.primaryScreen()
        
        return MonitorInfo(
            index=index,
            x=geometry.x(),
            y=geometry.y(),
            width=geometry.width(),
            height=geometry.height(),
            name=name,
            is_primary=is_primary
        )
    
    def print_monitor_info(self) -> None:
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
