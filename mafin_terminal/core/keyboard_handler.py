"""Keyboard handler for terminal input."""

from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class KeyMode(Enum):
    """Keyboard input mode."""
    COMMAND = "command"
    NAVIGATION = "navigation"
    INSERT = "insert"


@dataclass
class KeyBinding:
    """Key binding configuration."""
    key: int
    modifiers: int = 0
    callback: Optional[Callable] = None
    description: str = ""


class KeyboardHandler:
    """Handle keyboard input for the terminal."""

    def __init__(self):
        self._key_bindings: Dict[int, Callable] = {}
        self._mode = KeyMode.COMMAND
        self._input_buffer = ""
        self._history: list = []
        self._history_index = -1
        self._max_history = 100
        
        self._setup_default_bindings()

    def _setup_default_bindings(self):
        """Setup default key bindings."""
        self._mode_bindings = {
            KeyMode.COMMAND: {},
            KeyMode.NAVIGATION: {},
            KeyMode.INSERT: {}
        }

    def register_binding(self, key: int, callback: Callable, mode: KeyMode = KeyMode.COMMAND):
        """Register a key binding."""
        self._mode_bindings[mode][key] = callback

    def unregister_binding(self, key: int, mode: KeyMode = KeyMode.COMMAND):
        """Unregister a key binding."""
        if key in self._mode_bindings[mode]:
            del self._mode_bindings[mode][key]

    def handle_key(self, key: int, modifiers: int = 0) -> bool:
        """Handle key press."""
        bindings = self._mode_bindings.get(self._mode, {})
        
        if key in bindings:
            callback = bindings[key]
            if callback:
                callback()
            return True
        
        return False

    def set_mode(self, mode: KeyMode):
        """Set keyboard mode."""
        self._mode = mode

    def get_mode(self) -> KeyMode:
        """Get current keyboard mode."""
        return self._mode

    def add_to_history(self, command: str):
        """Add command to history."""
        if command and command.strip():
            self._history.append(command)
            if len(self._history) > self._max_history:
                self._history.pop(0)
            self._history_index = len(self._history)

    def get_previous_command(self) -> Optional[str]:
        """Get previous command from history."""
        if self._history and self._history_index > 0:
            self._history_index -= 1
            return self._history[self._history_index]
        return None

    def get_next_command(self) -> Optional[str]:
        """Get next command from history."""
        if self._history and self._history_index < len(self._history) - 1:
            self._history_index += 1
            return self._history[self._history_index]
        else:
            self._history_index = len(self._history)
            return ""

    def clear_history(self):
        """Clear command history."""
        self._history = []
        self._history_index = -1

    def get_bindings_summary(self) -> Dict[str, list]:
        """Get summary of all key bindings."""
        summary = {}
        for mode, bindings in self._mode_bindings.items():
            mode_name = mode.value
            summary[mode_name] = []
            for key, callback in bindings.items():
                summary[mode_name].append({
                    'key': key,
                    'callback': callback.__name__ if callback else None
                })
        return summary


class TerminalShortcuts:
    """Predefined terminal shortcuts."""

    @staticmethod
    def setup_default_shortcuts(handler: KeyboardHandler):
        """Setup default terminal shortcuts."""
        
        def go_up():
            print("↑")
        
        def go_down():
            print("↓")
        
        def go_left():
            print("←")
        
        def go_right():
            print("→")
        
        def page_up():
            print("Page Up")
        
        def page_down():
            print("Page Down")
        
        def home():
            print("Home")
        
        def end():
            print("End")
        
        def tab():
            print("Tab")
        
        def escape():
            print("Escape")


def create_handler() -> KeyboardHandler:
    """Create keyboard handler."""
    return KeyboardHandler()
