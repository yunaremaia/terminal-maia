"""Economic data module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict
import yfinance as yf


@dataclass
class EconomicIndicator:
    """Economic indicator data."""
    name: str
    value: Optional[float]
    previous_value: Optional[float]
    change: Optional[float]
    change_percent: Optional[float]
    unit: str
    country: str


@dataclass
class CentralBankRate:
    """Central bank interest rate."""
    bank: str
    rate: float
    previous_rate: float
    change: float
    date: str


@dataclass
class IndexData:
    """Global market index data."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float


class EconomicModule:
    """Economic data module."""

    INDICES = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ',
        '^RUT': 'Russell 2000',
        '^FTSE': 'FTSE 100',
        '^GDAXI': 'DAX',
        '^N225': 'Nikkei 225',
        '^HSI': 'Hang Seng'
    }

    CURRENCIES = {
        'EURUSD=X': 'EUR/USD',
        'GBPUSD=X': 'GBP/USD',
        'USDJPY=X': 'USD/JPY',
        'USDCHF=X': 'USD/CHF',
        'AUDUSD=X': 'AUD/USD',
        'USDCAD=X': 'USD/CAD'
    }

    COMMODITIES = {
        'GC=F': 'Gold',
        'SI=F': 'Silver',
        'CL=F': 'Crude Oil',
        'NG=F': 'Natural Gas',
        'HG=F': 'Copper',
        'ZC=F': 'Corn',
        'ZW=F': 'Wheat',
        'ZS=F': 'Soybeans'
    }

    TREASURIES = {
        '^TNX': '10Y Treasury',
        '^FVX': '5Y Treasury',
        '^IRX': '13W Treasury',
        '^TYX': '30Y Treasury'
    }

    def __init__(self):
        pass

    async def get_indices(self) -> List[IndexData]:
        """Get global market indices."""
        results = []
        loop = asyncio.get_event_loop()
        
        for symbol, name in self.INDICES.items():
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if info and 'regularMarketPrice' in info:
                    results.append(IndexData(
                        symbol=symbol,
                        name=name,
                        price=info.get('regularMarketPrice', 0),
                        change=info.get('regularMarketChange', 0),
                        change_percent=info.get('regularMarketChangePercent', 0)
                    ))
            except Exception:
                continue
        
        return results

    async def get_currencies(self) -> List[IndexData]:
        """Get major currency pairs."""
        results = []
        loop = asyncio.get_event_loop()
        
        for symbol, name in self.CURRENCIES.items():
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if info and 'regularMarketPrice' in info:
                    results.append(IndexData(
                        symbol=symbol,
                        name=name,
                        price=info.get('regularMarketPrice', 0),
                        change=info.get('regularMarketChange', 0),
                        change_percent=info.get('regularMarketChangePercent', 0)
                    ))
            except Exception:
                continue
        
        return results

    async def get_commodities(self) -> List[IndexData]:
        """Get major commodities."""
        results = []
        loop = asyncio.get_event_loop()
        
        for symbol, name in self.COMMODITIES.items():
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if info and 'regularMarketPrice' in info:
                    results.append(IndexData(
                        symbol=symbol,
                        name=name,
                        price=info.get('regularMarketPrice', 0),
                        change=info.get('regularMarketChange', 0),
                        change_percent=info.get('regularMarketChangePercent', 0)
                    ))
            except Exception:
                continue
        
        return results

    async def get_treasury_yields(self) -> List[IndexData]:
        """Get US Treasury yields."""
        results = []
        loop = asyncio.get_event_loop()
        
        for symbol, name in self.TREASURIES.items():
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if info and 'regularMarketPrice' in info:
                    results.append(IndexData(
                        symbol=symbol,
                        name=name,
                        price=info.get('regularMarketPrice', 0),
                        change=info.get('regularMarketChange', 0),
                        change_percent=info.get('regularMarketChangePercent', 0)
                    ))
            except Exception:
                continue
        
        return results

    async def get_market_overview(self) -> Dict:
        """Get complete market overview."""
        indices = await self.get_indices()
        currencies = await self.get_currencies()
        commodities = await self.get_commodities()
        treasuries = await self.get_treasury_yields()
        
        return {
            'indices': indices,
            'currencies': currencies,
            'commodities': commodities,
            'treasuries': treasuries
        }

    def get_economic_calendar(self) -> List[Dict]:
        """Get upcoming economic events (placeholder)."""
        return [
            {'date': '2024-01-15', 'event': 'US Non-Farm Payrolls', 'forecast': '180K', 'previous': '216K'},
            {'date': '2024-01-16', 'event': 'US CPI (MoM)', 'forecast': '0.2%', 'previous': '0.1%'},
            {'date': '2024-01-17', 'event': 'FOMC Meeting Minutes', 'forecast': '-', 'previous': '-'},
            {'date': '2024-01-25', 'event': 'US GDP (QoQ)', 'forecast': '2.0%', 'previous': '2.3%'},
        ]


def create_module() -> EconomicModule:
    """Create economic module."""
    return EconomicModule()
