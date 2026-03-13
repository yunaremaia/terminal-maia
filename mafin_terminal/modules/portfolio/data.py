"""Portfolio management module."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

from mafin_terminal.data.providers import YahooFinanceProvider, Quote


class TransactionType(Enum):
    """Transaction types."""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SPLIT = "SPLIT"


@dataclass
class Transaction:
    """Portfolio transaction."""
    id: str
    symbol: str
    type: TransactionType
    quantity: float
    price: float
    date: str
    fees: float = 0.0
    notes: str = ""


@dataclass
class Position:
    """Portfolio position."""
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0


@dataclass
class PortfolioSummary:
    """Portfolio summary."""
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    cash: float
    positions_count: int


class Portfolio:
    """Portfolio manager."""

    def __init__(self, name: str = "Default"):
        self.name = name
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.cash: float = 0.0
        self._transaction_id = 0
        self._provider = YahooFinanceProvider()

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        self._transaction_id += 1
        return f"TXN{self._transaction_id:06d}"

    def add_cash(self, amount: float):
        """Add cash to portfolio."""
        self.cash += amount

    def withdraw_cash(self, amount: float) -> bool:
        """Withdraw cash from portfolio."""
        if amount <= self.cash:
            self.cash -= amount
            return True
        return False

    def buy(self, symbol: str, quantity: float, price: float, 
            date: Optional[str] = None, fees: float = 0.0) -> bool:
        """Execute a buy transaction."""
        total_cost = (quantity * price) + fees
        
        if total_cost > self.cash:
            return False
        
        self.cash -= total_cost
        
        symbol = symbol.upper()
        if symbol in self.positions:
            pos = self.positions[symbol]
            new_quantity = pos.quantity + quantity
            new_avg_cost = ((pos.quantity * pos.avg_cost) + (quantity * price)) / new_quantity
            pos.quantity = new_quantity
            pos.avg_cost = new_avg_cost
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price
            )
        
        txn = Transaction(
            id=self._generate_transaction_id(),
            symbol=symbol,
            type=TransactionType.BUY,
            quantity=quantity,
            price=price,
            date=date or datetime.now().strftime("%Y-%m-%d"),
            fees=fees
        )
        self.transactions.append(txn)
        
        return True

    def sell(self, symbol: str, quantity: float, price: float,
             date: Optional[str] = None, fees: float = 0.0) -> bool:
        """Execute a sell transaction."""
        symbol = symbol.upper()
        
        if symbol not in self.positions:
            return False
        
        pos = self.positions[symbol]
        if pos.quantity < quantity:
            return False
        
        proceeds = (quantity * price) - fees
        self.cash += proceeds
        
        pos.quantity -= quantity
        if pos.quantity == 0:
            del self.positions[symbol]
        
        txn = Transaction(
            id=self._generate_transaction_id(),
            symbol=symbol,
            type=TransactionType.SELL,
            quantity=quantity,
            price=price,
            date=date or datetime.now().strftime("%Y-%m-%d"),
            fees=fees
        )
        self.transactions.append(txn)
        
        return True

    def add_dividend(self, symbol: str, amount: float,
                     date: Optional[str] = None):
        """Record dividend income."""
        self.cash += amount
        
        txn = Transaction(
            id=self._generate_transaction_id(),
            symbol=symbol.upper(),
            type=TransactionType.DIVIDEND,
            quantity=0,
            price=amount,
            date=date or datetime.now().strftime("%Y-%m-%d")
        )
        self.transactions.append(txn)

    async def update_prices(self):
        """Update current prices for all positions."""
        if not self.positions:
            return
        
        symbols = list(self.positions.keys())
        quotes = await self._provider.get_multiple_quotes(symbols)
        
        for quote in quotes:
            if quote.symbol in self.positions:
                pos = self.positions[quote.symbol]
                pos.current_price = quote.price
                pos.market_value = pos.quantity * quote.price
                pos.unrealized_pnl = pos.market_value - (pos.quantity * pos.avg_cost)
                if pos.quantity * pos.avg_cost > 0:
                    pos.unrealized_pnl_percent = (pos.unrealized_pnl / (pos.quantity * pos.avg_cost)) * 100

    def get_positions(self) -> List[Position]:
        """Get all positions."""
        return list(self.positions.values())

    def get_summary(self) -> PortfolioSummary:
        """Get portfolio summary."""
        total_value = self.cash + sum(p.market_value for p in self.positions.values())
        total_cost = sum(p.quantity * p.avg_cost for p in self.positions.values())
        total_pnl = total_value - total_cost - self.cash
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return PortfolioSummary(
            total_value=total_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            cash=self.cash,
            positions_count=len(self.positions)
        )

    def get_transactions(self, symbol: Optional[str] = None) -> List[Transaction]:
        """Get transactions, optionally filtered by symbol."""
        if symbol:
            return [t for t in self.transactions if t.symbol == symbol.upper()]
        return list(self.transactions)


class PortfolioManager:
    """Manages multiple portfolios."""

    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}
        self._default_portfolio: Optional[Portfolio] = None

    def create_portfolio(self, name: str) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio(name)
        self.portfolios[name] = portfolio
        if self._default_portfolio is None:
            self._default_portfolio = portfolio
        return portfolio

    def get_portfolio(self, name: str) -> Optional[Portfolio]:
        """Get portfolio by name."""
        return self.portfolios.get(name)

    def get_default(self) -> Portfolio:
        """Get default portfolio."""
        if self._default_portfolio is None:
            self._default_portfolio = self.create_portfolio("Default")
        return self._default_portfolio

    def list_portfolios(self) -> List[str]:
        """List all portfolio names."""
        return list(self.portfolios.keys())

    def delete_portfolio(self, name: str) -> bool:
        """Delete a portfolio."""
        if name in self.portfolios:
            del self.portfolios[name]
            if self._default_portfolio and self._default_portfolio.name == name:
                self._default_portfolio = None
            return True
        return False


def create_portfolio(name: str = "Default") -> Portfolio:
    """Create a new portfolio."""
    return Portfolio(name)


def create_manager() -> PortfolioManager:
    """Create portfolio manager."""
    return PortfolioManager()
