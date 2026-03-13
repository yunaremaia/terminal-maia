"""Yahoo Finance data provider."""

import asyncio
from datetime import datetime
from typing import Optional
import yfinance as yf

from .base import DataProvider, Quote, HistoricalData


class YahooFinanceProvider(DataProvider):
    """Yahoo Finance data provider."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)

    async def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get quote for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, ticker.info)
            
            if not info or 'regularMarketPrice' not in info:
                return None

            return Quote(
                symbol=symbol.upper(),
                price=info.get('regularMarketPrice', 0),
                change=info.get('regularMarketChange', 0),
                change_percent=info.get('regularMarketChangePercent', 0),
                volume=info.get('regularMarketVolume', 0),
                high=info.get('regularMarketDayHigh', 0),
                low=info.get('regularMarketDayLow', 0),
                open_price=info.get('regularMarketOpen', 0),
                previous_close=info.get('regularMarketPreviousClose', 0),
                market_cap=info.get('marketCap'),
                name=info.get('shortName', info.get('longName')),
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_historical(self, symbol: str, period: str = "1y") -> Optional[HistoricalData]:
        """Get historical data for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            hist = await loop.run_in_executor(
                None, 
                lambda: ticker.history(period=period)
            )
            
            if hist.empty:
                return None

            return HistoricalData(
                symbol=symbol.upper(),
                dates=hist.index.strftime('%Y-%m-%d').tolist(),
                open=hist['Open'].tolist(),
                high=hist['High'].tolist(),
                low=hist['Low'].tolist(),
                close=hist['Close'].tolist(),
                volume=hist['Volume'].tolist()
            )
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None

    async def search_symbol(self, query: str) -> list:
        """Search for symbols."""
        try:
            loop = asyncio.get_event_loop()
            tickers = await loop.run_in_executor(
                None,
                lambda: yf.search(query)
            )
            
            if tickers is None:
                return []
            
            results = []
            for t in tickers.get('quotes', []):
                results.append({
                    'symbol': t.get('symbol', ''),
                    'name': t.get('shortname', t.get('longname', '')),
                    'exchange': t.get('exchange', ''),
                    'type': t.get('quoteType', '')
                })
            return results
        except Exception as e:
            print(f"Error searching for {query}: {e}")
            return []

    async def get_market_movers(self, market: str = "^GSPC") -> dict:
        """Get market movers (gainers, losers, most active)."""
        try:
            loop = asyncio.get_event_loop()
            
            gainers = await loop.run_in_executor(
                None,
                lambda: yf.market.movers(market=market)['gainers']
            )
            losers = await loop.run_in_executor(
                None,
                lambda: yf.market.movers(market=market)['losers']
            )
            most_active = await loop.run_in_executor(
                None,
                lambda: yf.market.movers(market=market)['most_active']
            )
            
            return {
                'gainers': gainers.to_dict('records') if gainers is not None else [],
                'losers': losers.to_dict('records') if losers is not None else [],
                'most_active': most_active.to_dict('records') if most_active is not None else []
            }
        except Exception as e:
            print(f"Error fetching market movers: {e}")
            return {'gainers': [], 'losers': [], 'most_active': []}
