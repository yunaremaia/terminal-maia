"""Command parser for terminal commands."""

import re
from dataclasses import dataclass
from typing import Optional, List, Callable, Dict, Any
from enum import Enum


class CommandType(Enum):
    """Command types."""
    QUOTE = "quote"
    CHART = "chart"
    WATCH = "watch"
    PORTFOLIO = "portfolio"
    BUY = "buy"
    SELL = "sell"
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    RISK = "risk"
    ECONOMIC = "economic"
    NEWS = "news"
    SEARCH = "search"
    HELP = "help"
    QUIT = "quit"
    CLEAR = "clear"
    SET = "set"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """Parsed command."""
    type: CommandType
    args: List[str]
    raw_args: str
    symbol: Optional[str] = None
    options: Dict[str, str] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}


class CommandParser:
    """Command parser for terminal."""

    COMMANDS = {
        'q': CommandType.QUOTE,
        'quote': CommandType.QUOTE,
        'c': CommandType.CHART,
        'chart': CommandType.CHART,
        'w': CommandType.WATCH,
        'watch': CommandType.WATCH,
        'p': CommandType.PORTFOLIO,
        'portfolio': CommandType.PORTFOLIO,
        'buy': CommandType.BUY,
        'sell': CommandType.SELL,
        'f': CommandType.FUNDAMENTAL,
        'fund': CommandType.FUNDAMENTAL,
        'fundamental': CommandType.FUNDAMENTAL,
        't': CommandType.TECHNICAL,
        'tech': CommandType.TECHNICAL,
        'technical': CommandType.TECHNICAL,
        'r': CommandType.RISK,
        'risk': CommandType.RISK,
        'e': CommandType.ECONOMIC,
        'econ': CommandType.ECONOMIC,
        'economic': CommandType.ECONOMIC,
        'n': CommandType.NEWS,
        'news': CommandType.NEWS,
        's': CommandType.SEARCH,
        'search': CommandType.SEARCH,
        'h': CommandType.HELP,
        'help': CommandType.HELP,
        'quit': CommandType.QUIT,
        'exit': CommandType.QUIT,
        'clear': CommandType.CLEAR,
        'set': CommandType.SET,
    }

    def __init__(self):
        self._command_handlers: Dict[CommandType, Callable] = {}

    def register_handler(self, command: CommandType, handler: Callable):
        """Register a handler for a command."""
        self._command_handlers[command] = handler

    def parse(self, input_str: str) -> ParsedCommand:
        """Parse input string into command."""
        input_str = input_str.strip()
        
        if not input_str:
            return ParsedCommand(
                type=CommandType.UNKNOWN,
                args=[],
                raw_args=""
            )

        parts = self._tokenize(input_str)
        
        if not parts:
            return ParsedCommand(
                type=CommandType.UNKNOWN,
                args=[],
                raw_args=input_str
            )

        cmd = parts[0].lower()
        args = parts[1:]
        
        command_type = self.COMMANDS.get(cmd, CommandType.UNKNOWN)
        
        symbol = None
        options = {}
        
        if command_type in [CommandType.QUOTE, CommandType.CHART, CommandType.FUNDAMENTAL,
                           CommandType.TECHNICAL, CommandType.RISK, CommandType.NEWS]:
            if args:
                symbol = args[0].upper()
                args = args[1:]
        
        if command_type == CommandType.SET and len(args) >= 2:
            options = {'key': args[0], 'value': args[1]}
        
        return ParsedCommand(
            type=command_type,
            args=args,
            raw_args=" ".join(parts[1:]),
            symbol=symbol,
            options=options
        )

    def _tokenize(self, input_str: str) -> List[str]:
        """Tokenize input string."""
        tokens = []
        current = ""
        in_quotes = False
        quote_char = None
        
        for char in input_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ' ' and not in_quotes:
                if current:
                    tokens.append(current)
                    current = ""
            else:
                current += char
        
        if current:
            tokens.append(current)
        
        return tokens

    def get_help(self) -> Dict[str, str]:
        """Get help information for commands."""
        return {
            'q/quote <symbol>': 'Get quote for symbol',
            'c/chart <symbol> [period]': 'Show chart for symbol',
            'w/watch <symbol1> [<symbol2>...]': 'Add symbols to watchlist',
            'p/portfolio': 'Show portfolio',
            'buy <symbol> <quantity> <price>': 'Buy shares',
            'sell <symbol> <quantity> <price>': 'Sell shares',
            'f/fund <symbol>': 'Show fundamental analysis',
            't/tech <symbol>': 'Show technical analysis',
            'r/risk [symbol]': 'Show risk metrics',
            'e/econ': 'Show economic data',
            'n/news [symbol]': 'Show market news',
            's/search <query>': 'Search for symbols',
            'h/help': 'Show this help',
            'quit/exit': 'Exit terminal',
            'clear': 'Clear screen',
            'set <key> <value>': 'Set configuration'
        }

    def format_help(self) -> str:
        """Format help as string."""
        help_text = "Available commands:\n"
        for cmd, desc in self.get_help().items():
            help_text += f"  {cmd:40} {desc}\n"
        return help_text
