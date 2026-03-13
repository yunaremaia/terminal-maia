"""News module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import yfinance as yf


@dataclass
class NewsItem:
    """News article."""
    title: str
    publisher: str
    link: str
    published: str
    summary: Optional[str] = None


@dataclass
class MarketNews:
    """Market news summary."""
    symbol: Optional[str]
    news: List[NewsItem]


class NewsModule:
    """News module."""

    def __init__(self):
        pass

    async def get_symbol_news(self, symbol: str, limit: int = 10) -> MarketNews:
        """Get news for a specific symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            news = await loop.run_in_executor(
                None,
                lambda: ticker.news
            )
            
            if not news:
                return MarketNews(symbol=symbol.upper(), news=[])
            
            news_items = []
            for item in news[:limit]:
                news_items.append(NewsItem(
                    title=item.get('title', 'N/A'),
                    publisher=item.get('publisher', 'N/A'),
                    link=item.get('link', ''),
                    published=item.get('pubDate', ''),
                    summary=item.get('summary', None)
                ))
            
            return MarketNews(symbol=symbol.upper(), news=news_items)
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return MarketNews(symbol=symbol.upper(), news=[])

    async def get_market_news(self, limit: int = 20) -> List[NewsItem]:
        """Get general market news."""
        try:
            loop = asyncio.get_event_loop()
            
            tickers = ['^GSPC', '^DJI', '^IXIC']
            all_news = []
            
            for symbol in tickers:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                news = await loop.run_in_executor(
                    None,
                    lambda: ticker.news
                )
                if news:
                    all_news.extend(news)
            
            seen_titles = set()
            unique_news = []
            
            for item in all_news:
                title = item.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(NewsItem(
                        title=title,
                        publisher=item.get('publisher', 'N/A'),
                        link=item.get('link', ''),
                        published=item.get('pubDate', ''),
                        summary=item.get('summary', None)
                    ))
            
            return unique_news[:limit]
        except Exception as e:
            print(f"Error fetching market news: {e}")
            return []

    async def get_earnings_calendar(self, symbol: str) -> List[Dict]:
        """Get upcoming earnings for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            calendar = await loop.run_in_executor(
                None,
                lambda: ticker.calendar
            )
            
            if calendar is None or calendar.empty:
                return []
            
            earnings = []
            for idx, row in calendar.iterrows():
                if hasattr(idx, 'strftime'):
                    earnings.append({
                        'date': str(idx),
                        'eps_estimate': row.get('EPS Estimate', None),
                        'reported_eps': row.get('EPS', None),
                        'surprise': row.get('Surprise', None)
                    })
            
            return earnings
        except Exception as e:
            print(f"Error fetching earnings calendar for {symbol}: {e}")
            return []

    def analyze_sentiment(self, news_items: List[NewsItem]) -> Dict:
        """Analyze sentiment from news (basic keyword-based)."""
        if not news_items:
            return {'sentiment': 'neutral', 'score': 0, 'count': 0}
        
        positive_words = ['surge', 'soar', 'rally', 'gain', 'rise', 'bullish', 
                         'beat', 'exceed', 'growth', 'profit', 'optimistic']
        negative_words = ['fall', 'drop', 'decline', 'crash', 'bearish', 'loss',
                         'miss', 'warning', 'concern', 'risk', 'fear']
        
        positive_count = 0
        negative_count = 0
        
        for item in news_items:
            title = item.title.lower()
            for word in positive_words:
                if word in title:
                    positive_count += 1
                    break
            for word in negative_words:
                if word in title:
                    negative_count += 1
                    break
        
        total = len(news_items)
        score = (positive_count - negative_count) / total if total > 0 else 0
        
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive': positive_count,
            'negative': negative_count,
            'count': total
        }


def create_module() -> NewsModule:
    """Create news module."""
    return NewsModule()
