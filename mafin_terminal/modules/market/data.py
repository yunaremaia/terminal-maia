"""Market data module for quotes and market information."""

import asyncio
from typing import Optional, List, Dict
from dataclasses import dataclass

from mafin_terminal.data.providers import YahooFinanceProvider, Quote, HistoricalData


@dataclass
class MarketMovers:
    """Market movers data."""
    gainers: List[Dict]
    losers: List[Dict]
    most_active: List[Dict]


class MarketData:
    """Market data handler."""

    def __init__(self):
        self.provider = YahooFinanceProvider()
        self._watchlist: List[str] = []

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get quote for a symbol."""
        return await self.provider.get_quote(symbol)

    async def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols."""
        return await self.provider.get_multiple_quotes(symbols)

    async def get_historical(self, symbol: str, period: str = "1y") -> Optional[HistoricalData]:
        """Get historical data for a symbol."""
        return await self.provider.get_historical(symbol, period)

    async def get_market_movers(self, market: str = "^GSPC") -> MarketMovers:
        """Get market movers."""
        data = await self.provider.get_market_movers(market)
        return MarketMovers(
            gainers=data.get('gainers', []),
            losers=data.get('losers', []),
            most_active=data.get('most_active', [])
        )

    async def search_symbol(self, query: str) -> List[Dict]:
        """Search for symbols."""
        return await self.provider.search_symbol(query)

    def add_to_watchlist(self, symbol: str):
        """Add symbol to watchlist."""
        if symbol.upper() not in self._watchlist:
            self._watchlist.append(symbol.upper())

    def remove_from_watchlist(self, symbol: str):
        """Remove symbol from watchlist."""
        if symbol.upper() in self._watchlist:
            self._watchlist.remove(symbol.upper())

    def get_watchlist(self) -> List[str]:
        """Get current watchlist."""
        return self._watchlist.copy()

    async def get_watchlist_quotes(self) -> List[Quote]:
        """Get quotes for all symbols in watchlist."""
        if not self._watchlist:
            return []
        return await self.provider.get_multiple_quotes(self._watchlist)


class MarketModule:
    """Market module for terminal."""

    def __init__(self):
        self.market_data = MarketData()
        self._current_symbol: Optional[str] = None

    async def quote(self, symbol: str) -> Optional[Quote]:
        """Get quote for symbol."""
        self._current_symbol = symbol.upper()
        return await self.market_data.get_quote(symbol)

    async def watch(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols."""
        return await self.market_data.get_multiple_quotes(symbols)

    async def movers(self, market: str = "^GSPC") -> MarketMovers:
        """Get market movers."""
        return await self.market_data.get_market_movers(market)

    async def chart(self, symbol: str, period: str = "1y") -> Optional[HistoricalData]:
        """Get chart data for symbol."""
        return await self.market_data.get_historical(symbol, period)

    async def search(self, query: str) -> List[Dict]:
        """Search for symbols."""
        return await self.market_data.search_symbol(query)

    def add_watch(self, symbol: str):
        """Add symbol to watchlist."""
        self.market_data.add_to_watchlist(symbol)

    def remove_watch(self, symbol: str):
        """Remove symbol from watchlist."""
        self.market_data.remove_from_watchlist(symbol)

    async def get_watchlist(self) -> List[Quote]:
        """Get watchlist quotes."""
        return await self.market_data.get_watchlist_quotes()


def create_module() -> MarketModule:
    """Create market module instance."""
    return MarketModule()
