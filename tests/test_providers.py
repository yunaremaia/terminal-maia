"""Tests for data providers."""

import pytest
import asyncio
from mafin_terminal.data.providers import YahooFinanceProvider, Quote, HistoricalData


class TestYahooFinanceProvider:
    """Test Yahoo Finance provider."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return YahooFinanceProvider()
    
    @pytest.mark.asyncio
    async def test_get_quote(self, provider):
        """Test getting a quote."""
        quote = await provider.get_quote("AAPL")
        
        assert quote is not None
        assert quote.symbol == "AAPL"
        assert quote.price > 0
        assert isinstance(quote.change, float)
        assert isinstance(quote.change_percent, float)
        assert quote.volume >= 0
    
    @pytest.mark.asyncio
    async def test_get_quote_invalid_symbol(self, provider):
        """Test getting quote for invalid symbol."""
        quote = await provider.get_quote("INVALID_SYMBOL_XYZ")
        assert quote is None
    
    @pytest.mark.asyncio
    async def test_get_historical(self, provider):
        """Test getting historical data."""
        hist = await provider.get_historical("AAPL", "5d")
        
        assert hist is not None
        assert hist.symbol == "AAPL"
        assert len(hist.close) > 0
        assert len(hist.open) == len(hist.close)
        assert len(hist.high) == len(hist.close)
        assert len(hist.low) == len(hist.close)
    
    @pytest.mark.asyncio
    async def test_search_symbol(self, provider):
        """Test symbol search."""
        results = await provider.search_symbol("Apple")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert any(r.get('symbol') == 'AAPL' for r in results)
    
    @pytest.mark.asyncio
    async def test_get_multiple_quotes(self, provider):
        """Test getting multiple quotes."""
        quotes = await provider.get_multiple_quotes(["AAPL", "MSFT"])
        
        assert len(quotes) == 2
        symbols = [q.symbol for q in quotes]
        assert "AAPL" in symbols
        assert "MSFT" in symbols


class TestQuote:
    """Test Quote dataclass."""
    
    def test_quote_creation(self):
        """Test creating a quote."""
        quote = Quote(
            symbol="AAPL",
            price=150.0,
            change=2.5,
            change_percent=1.5,
            volume=1000000,
            high=152.0,
            low=148.0,
            open_price=149.0,
            previous_close=147.5
        )
        
        assert quote.symbol == "AAPL"
        assert quote.price == 150.0
        assert quote.change == 2.5
        assert quote.change_percent == 1.5
        assert quote.volume == 1000000
    
    def test_quote_optional_fields(self):
        """Test quote with optional fields."""
        quote = Quote(
            symbol="AAPL",
            price=150.0,
            change=2.5,
            change_percent=1.5,
            volume=1000000,
            high=152.0,
            low=148.0,
            open_price=149.0,
            previous_close=147.5,
            market_cap=2500000000000,
            name="Apple Inc."
        )
        
        assert quote.market_cap == 2500000000000
        assert quote.name == "Apple Inc."
