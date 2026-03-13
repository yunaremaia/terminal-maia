"""Screen manager for multi-window management."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class ScreenType(Enum):
    """Screen types."""
    WELCOME = "welcome"
    DASHBOARD = "dashboard"
    QUOTE = "quote"
    CHART = "chart"
    PORTFOLIO = "portfolio"
    WATCHLIST = "watchlist"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    RISK = "risk"
    ECONOMIC = "economic"
    NEWS = "news"
    SETTINGS = "settings"


@dataclass
class Screen:
    """Screen definition."""
    id: str
    type: ScreenType
    title: str
    widget: Any = None
    data: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 0
    on_activate: Optional[Callable] = None
    on_deactivate: Optional[Callable] = None


class ScreenManager:
    """Manage terminal screens."""

    def __init__(self):
        self._screens: Dict[str, Screen] = {}
        self._screen_stack: List[str] = []
        self._current_screen: Optional[str] = None
        self._default_screen: Optional[str] = None

    def register_screen(self, screen: Screen):
        """Register a screen."""
        self._screens[screen.id] = screen
        
        if self._default_screen is None:
            self._default_screen = screen.id

    def unregister_screen(self, screen_id: str):
        """Unregister a screen."""
        if screen_id in self._screens:
            del self._screens[screen_id]
            if screen_id in self._screen_stack:
                self._screen_stack.remove(screen_id)
            if self._current_screen == screen_id:
                self._current_screen = None

    def get_screen(self, screen_id: str) -> Optional[Screen]:
        """Get screen by ID."""
        return self._screens.get(screen_id)

    def get_current_screen(self) -> Optional[Screen]:
        """Get current screen."""
        if self._current_screen:
            return self._screens.get(self._current_screen)
        return None

    def navigate_to(self, screen_id: str, **kwargs) -> bool:
        """Navigate to a screen."""
        if screen_id not in self._screens:
            return False
        
        current = self.get_current_screen()
        if current and current.on_deactivate:
            current.on_deactivate()
        
        self._current_screen = screen_id
        screen = self._screens[screen_id]
        
        if kwargs:
            screen.data.update(kwargs)
        
        if screen.on_activate:
            screen.on_activate()
        
        if screen_id not in self._screen_stack:
            self._screen_stack.append(screen_id)
        
        return True

    def navigate_back(self) -> bool:
        """Navigate back to previous screen."""
        if len(self._screen_stack) <= 1:
            return False
        
        current = self.get_current_screen()
        if current and current.on_deactivate:
            current.on_deactivate()
        
        self._screen_stack.pop()
        
        prev_id = self._screen_stack[-1]
        self._current_screen = prev_id
        
        prev_screen = self.get_current_screen()
        if prev_screen and prev_screen.on_activate:
            prev_screen.on_activate()
        
        return True

    def navigate_home(self) -> bool:
        """Navigate to default screen."""
        if self._default_screen:
            self._screen_stack = [self._default_screen]
            return self.navigate_to(self._default_screen)
        return False

    def get_screen_list(self) -> List[str]:
        """Get list of all screen IDs."""
        return list(self._screens.keys())

    def get_navigation_history(self) -> List[str]:
        """Get navigation history."""
        return self._screen_stack.copy()

    def clear_history(self):
        """Clear navigation history."""
        if self._current_screen:
            self._screen_stack = [self._current_screen]
        else:
            self._screen_stack = []

    def refresh_current_screen(self):
        """Refresh current screen data."""
        current = self.get_current_screen()
        if current and hasattr(current.widget, 'refresh'):
            current.widget.refresh()

    def set_default_screen(self, screen_id: str):
        """Set default screen."""
        if screen_id in self._screens:
            self._default_screen = screen_id


def create_screen(screen_type: ScreenType, title: str, widget: Any = None) -> Screen:
    """Create a screen."""
    return Screen(
        id=screen_type.value,
        type=screen_type,
        title=title,
        widget=widget
    )


def create_manager() -> ScreenManager:
    """Create screen manager."""
    return ScreenManager()
