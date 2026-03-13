"""Tests for portfolio module."""

import pytest
import asyncio
from mafin_terminal.modules.portfolio import (
    Portfolio, PortfolioManager, Position, Transaction, TransactionType
)


class TestPortfolio:
    """Test Portfolio class."""
    
    @pytest.fixture
    def portfolio(self):
        """Create a test portfolio."""
        p = Portfolio("TestPortfolio")
        p.add_cash(10000)
        return p
    
    def test_portfolio_creation(self):
        """Test portfolio creation."""
        p = Portfolio("Test")
        assert p.name == "Test"
        assert p.cash == 0
        assert len(p.positions) == 0
        assert len(p.transactions) == 0
    
    def test_add_cash(self, portfolio):
        """Test adding cash."""
        portfolio.add_cash(5000)
        assert portfolio.cash == 15000
    
    def test_withdraw_cash(self, portfolio):
        """Test withdrawing cash."""
        assert portfolio.withdraw_cash(5000) is True
        assert portfolio.cash == 5000
    
    def test_withdraw_cash_insufficient(self, portfolio):
        """Test withdrawing more cash than available."""
        assert portfolio.withdraw_cash(20000) is False
        assert portfolio.cash == 10000
    
    def test_buy(self, portfolio):
        """Test buying shares."""
        result = portfolio.buy("AAPL", 10, 150.0)
        
        assert result is True
        assert portfolio.cash == 8500
        assert "AAPL" in portfolio.positions
        
        pos = portfolio.positions["AAPL"]
        assert pos.quantity == 10
        assert pos.avg_cost == 150.0
    
    def test_buy_insufficient_funds(self, portfolio):
        """Test buying with insufficient funds."""
        result = portfolio.buy("AAPL", 1000, 150.0)
        assert result is False
        assert portfolio.cash == 10000
    
    def test_buy_multiple_times(self, portfolio):
        """Test buying shares multiple times."""
        portfolio.buy("AAPL", 10, 100.0)
        portfolio.buy("AAPL", 10, 200.0)
        
        pos = portfolio.positions["AAPL"]
        assert pos.quantity == 20
        assert pos.avg_cost == 150.0
    
    def test_sell(self, portfolio):
        """Test selling shares."""
        portfolio.buy("AAPL", 10, 150.0)
        result = portfolio.sell("AAPL", 5, 200.0)
        
        assert result is True
        assert portfolio.cash == 8500 + 1000
        assert portfolio.positions["AAPL"].quantity == 5
    
    def test_sell_all(self, portfolio):
        """Test selling all shares."""
        portfolio.buy("AAPL", 10, 150.0)
        portfolio.sell("AAPL", 10, 200.0)
        
        assert "AAPL" not in portfolio.positions
    
    def test_sell_insufficient_shares(self, portfolio):
        """Test selling more shares than owned."""
        portfolio.buy("AAPL", 10, 150.0)
        result = portfolio.sell("AAPL", 20, 200.0)
        
        assert result is False
        assert portfolio.positions["AAPL"].quantity == 10
    
    def test_add_dividend(self, portfolio):
        """Test adding dividend."""
        portfolio.add_dividend("AAPL", 50.0)
        
        assert portfolio.cash == 10050
        assert len(portfolio.transactions) == 1
        assert portfolio.transactions[0].type == TransactionType.DIVIDEND
    
    def test_get_positions(self, portfolio):
        """Test getting positions."""
        portfolio.buy("AAPL", 10, 150.0)
        portfolio.buy("MSFT", 5, 300.0)
        
        positions = portfolio.get_positions()
        
        assert len(positions) == 2
        symbols = [p.symbol for p in positions]
        assert "AAPL" in symbols
        assert "MSFT" in symbols
    
    def test_get_summary(self, portfolio):
        """Test getting portfolio summary."""
        portfolio.buy("AAPL", 10, 150.0)
        
        summary = portfolio.get_summary()
        
        assert summary.cash == 8500
        assert summary.total_cost == 1500
        assert summary.positions_count == 1


class TestPortfolioManager:
    """Test PortfolioManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create portfolio manager."""
        return PortfolioManager()
    
    def test_create_portfolio(self, manager):
        """Test creating a portfolio."""
        p = manager.create_portfolio("MyPortfolio")
        
        assert p.name == "MyPortfolio"
        assert "MyPortfolio" in manager.list_portfolios()
    
    def test_get_portfolio(self, manager):
        """Test getting a portfolio."""
        manager.create_portfolio("Test")
        p = manager.get_portfolio("Test")
        
        assert p is not None
        assert p.name == "Test"
    
    def test_get_default(self, manager):
        """Test getting default portfolio."""
        p = manager.get_default()
        
        assert p is not None
        assert p.name == "Default"
    
    def test_delete_portfolio(self, manager):
        """Test deleting a portfolio."""
        manager.create_portfolio("Test")
        result = manager.delete_portfolio("Test")
        
        assert result is True
        assert "Test" not in manager.list_portfolios()
    
    def test_list_portfolios(self, manager):
        """Test listing portfolios."""
        manager.create_portfolio("P1")
        manager.create_portfolio("P2")
        
        portfolios = manager.list_portfolios()
        
        assert len(portfolios) == 2


class TestPosition:
    """Test Position dataclass."""
    
    def test_position_creation(self):
        """Test creating a position."""
        pos = Position("AAPL", 10, 150.0)
        
        assert pos.symbol == "AAPL"
        assert pos.quantity == 10
        assert pos.avg_cost == 150.0
        assert pos.current_price == 0.0
        assert pos.market_value == 0.0
    
    def test_position_with_current_price(self):
        """Test position with current price."""
        pos = Position("AAPL", 10, 150.0, current_price=200.0)
        
        assert pos.current_price == 200.0
        assert pos.market_value == 2000.0
        assert pos.unrealized_pnl == 500.0
        assert pos.unrealized_pnl_percent == pytest.approx(33.33, rel=0.1)
