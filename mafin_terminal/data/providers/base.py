"""Data providers for market data."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class Quote:
    """Stock quote data."""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open_price: float
    previous_close: float
    market_cap: Optional[float] = None
    name: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class HistoricalData:
    """Historical price data."""
    symbol: str
    dates: list
    open: list
    high: list
    low: list
    close: list
    volume: list


class DataProvider(ABC):
    """Abstract base class for data providers."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._cache = {}

    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get quote for a symbol."""
        pass

    @abstractmethod
    async def get_historical(self, symbol: str, period: str = "1y") -> Optional[HistoricalData]:
        """Get historical data for a symbol."""
        pass

    @abstractmethod
    async def search_symbol(self, query: str) -> list:
        """Search for symbols."""
        pass

    async def get_multiple_quotes(self, symbols: list) -> list:
        """Get quotes for multiple symbols."""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
