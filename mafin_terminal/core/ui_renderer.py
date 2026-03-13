"""UI renderer for terminal."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Color:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TableStyle(Enum):
    """Table rendering styles."""
    SIMPLE = "simple"
    GRID = "grid"
    BORDERLESS = "borderless"
    ROUNDED = "rounded"


@dataclass
class TableColumn:
    """Table column definition."""
    header: str
    width: Optional[int] = None
    align: str = "left"


class TerminalRenderer:
    """Render UI elements to terminal."""

    def __init__(self):
        self._width = 80
        self._table_style = TableStyle.ROUNDED

    def set_width(self, width: int):
        """Set terminal width."""
        self._width = width

    def set_table_style(self, style: TableStyle):
        """Set table style."""
        self._table_style = style

    def clear_screen(self):
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    def clear_line(self):
        """Clear current line."""
        print("\033[2K", end="")

    def move_cursor(self, row: int, col: int):
        """Move cursor to position."""
        print(f"\033[{row};{col}H", end="")

    def save_cursor(self):
        """Save cursor position."""
        print("\033[s", end="")

    def restore_cursor(self):
        """Restore cursor position."""
        print("\033[u", end="")

    def render_header(self, title: str, width: Optional[int] = None):
        """Render section header."""
        w = width or self._width
        print()
        print(f"{Color.CYAN}{Color.BOLD}{'=' * w}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{title:^{w}}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'=' * w}{Color.RESET}")

    def render_subheader(self, title: str, width: Optional[int] = None):
        """Render subsection header."""
        w = width or self._width
        print(f"{Color.YELLOW}{Color.BOLD}{title}{Color.RESET}")
        print(f"{Color.YELLOW}{'-' * len(title)}{Color.RESET}")

    def render_table(self, columns: List[TableColumn], rows: List[List[Any]], 
                    style: Optional[TableStyle] = None) -> str:
        """Render a table."""
        style = style or self._table_style
        
        if not rows:
            return ""
        
        widths = []
        for i, col in enumerate(columns):
            if col.width:
                widths.append(col.width)
            else:
                max_width = len(col.header)
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                widths.append(min(max_width, 20))
        
        output = []
        
        if style == TableStyle.ROUNDED:
            output.append("┌" + "┬".join("─" * (w + 2) for w in widths) + "┐")
            header_cells = []
            for col, w in zip(columns, widths):
                header_cells.append(f" {col.header:<{w}} ")
            output.append("│" + "│".join(header_cells) + "│")
            output.append("├" + "┼".join("─" * (w + 2) for w in widths) + "┤")
        elif style == TableStyle.GRID:
            output.append("+" + "+".join("-" * (w + 2) for w in widths) + "+")
            header_cells = []
            for col, w in zip(columns, widths):
                header_cells.append(f" {col.header:<{w}} ")
            output.append("|" + "|".join(header_cells) + "|")
            output.append("+" + "+".join("-" * (w + 2) for w in widths) + "+")
        
        for row in rows:
            cells = []
            for i, w in enumerate(widths):
                value = str(row[i]) if i < len(row) else ""
                align = columns[i].align if i < len(columns) else "left"
                if align == "right":
                    cells.append(f" {value:>{w}} ")
                elif align == "center":
                    cells.append(f" {value:^{w}} ")
                else:
                    cells.append(f" {value:<{w}} ")
            
            if style == TableStyle.ROUNDED:
                output.append("│" + "│".join(cells) + "│")
            elif style == TableStyle.GRID:
                output.append("|" + "|".join(cells) + "|")
            else:
                output.append("  ".join(cells))
        
        if style == TableStyle.ROUNDED:
            output.append("└" + "┴".join("─" * (w + 2) for w in widths) + "┘")
        elif style == TableStyle.GRID:
            output.append("+" + "+".join("-" * (w + 2) for w in widths) + "+")
        
        return "\n".join(output)

    def render_quote(self, symbol: str, price: float, change: float, 
                    change_percent: float, volume: int, name: Optional[str] = None):
        """Render quote display."""
        self.render_header(f"Quote: {symbol}")
        
        if name:
            print(f"{Color.DIM}{name}{Color.RESET}")
        
        print(f"\n{Color.BOLD}Price:{Color.RESET}     ${price:,.2f}")
        
        color = Color.GREEN if change >= 0 else Color.RED
        sign = "+" if change >= 0 else ""
        print(f"{Color.BOLD}Change:{Color.RESET}    {color}{sign}{change:,.2f} ({sign}{change_percent:.2f}%){Color.RESET}")
        print(f"{Color.BOLD}Volume:{Color.RESET}    {volume:,}")
        print()

    def render_key_value(self, data: Dict[str, Any], indent: int = 0):
        """Render key-value pairs."""
        prefix = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}{Color.BOLD}{key}:{Color.RESET}")
                self.render_key_value(value, indent + 2)
            elif value is not None:
                print(f"{prefix}{Color.BOLD}{key}:{Color.RESET} {value}")

    def render_progress_bar(self, current: float, total: float, 
                           width: int = 40, label: str = ""):
        """Render progress bar."""
        if total > 0:
            percent = current / total
            filled = int(width * percent)
            bar = "█" * filled + "░" * (width - filled)
            print(f"{label}: [{bar}] {percent * 100:.1f}%")

    def render_divider(self, char: str = "─", width: Optional[int] = None):
        """Render divider line."""
        w = width or self._width
        print(f"{Color.DIM}{char * w}{Color.RESET}")

    def format_number(self, value: float, decimals: int = 2) -> str:
        """Format number with commas."""
        return f"{value:,.{decimals}f}"

    def format_percent(self, value: float, decimals: int = 2) -> str:
        """Format percentage."""
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.{decimals}f}%"


_renderer: Optional[TerminalRenderer] = None


def get_renderer() -> TerminalRenderer:
    """Get global renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = TerminalRenderer()
    return _renderer
