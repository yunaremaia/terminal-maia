"""Options analysis module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict
import yfinance as yf


@dataclass
class OptionContract:
    """Option contract data."""
    symbol: str
    contract_symbol: str
    strike: float
    expiry: str
    type: str
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None


@dataclass
class OptionChain:
    """Option chain for a symbol."""
    symbol: str
    expiry_date: str
    calls: List[OptionContract]
    puts: List[OptionContract]


@dataclass
class OptionsSummary:
    """Options summary data."""
    symbol: str
    current_price: float
    chains: List[OptionChain]
    nearest_expiry: Optional[str] = None


class OptionsModule:
    """Options analysis module."""

    def __init__(self):
        pass

    async def get_option_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[OptionsSummary]:
        """Get option chain for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            current_price = info.get('regularMarketPrice', 0)
            
            opt = await loop.run_in_executor(None, lambda: ticker.option_chain)
            
            if not opt or opt.empty:
                return None
            
            chains = []
            
            if 'call' in opt and not opt['call'].empty:
                calls_df = opt['call']
                calls = []
                
                for _, row in calls_df.iterrows():
                    calls.append(OptionContract(
                        symbol=symbol,
                        contract_symbol=str(row.get('contractSymbol', '')),
                        strike=float(row.get('strike', 0)),
                        expiry=str(row.get('expiration', '')),
                        type='call',
                        bid=float(row.get('bid', 0)) if row.get('bid') else 0,
                        ask=float(row.get('ask', 0)) if row.get('ask') else 0,
                        last=float(row.get('lastPrice', 0)) if row.get('lastPrice') else 0,
                        volume=int(row.get('volume', 0)) if row.get('volume') else 0,
                        open_interest=int(row.get('openInterest', 0)) if row.get('openInterest') else 0,
                        implied_volatility=float(row.get('impliedVolatility', 0)) if row.get('impliedVolatility') else 0,
                        delta=float(row.get('delta', 0)) if row.get('delta') else None,
                        gamma=float(row.get('gamma', 0)) if row.get('gamma') else None,
                        theta=float(row.get('theta', 0)) if row.get('theta') else None,
                        vega=float(row.get('vega', 0)) if row.get('vega') else None,
                        rho=float(row.get('rho', 0)) if row.get('rho') else None,
                    ))
                
                expiries = list(set(c.expiry for c in calls))
                if expiries:
                    chains.append(OptionChain(
                        symbol=symbol,
                        expiry_date=expiries[0],
                        calls=calls,
                        puts=[]
                    ))
            
            if 'put' in opt and not opt['put'].empty:
                puts_df = opt['put']
                puts = []
                
                for _, row in puts_df.iterrows():
                    puts.append(OptionContract(
                        symbol=symbol,
                        contract_symbol=str(row.get('contractSymbol', '')),
                        strike=float(row.get('strike', 0)),
                        expiry=str(row.get('expiration', '')),
                        type='put',
                        bid=float(row.get('bid', 0)) if row.get('bid') else 0,
                        ask=float(row.get('ask', 0)) if row.get('ask') else 0,
                        last=float(row.get('lastPrice', 0)) if row.get('lastPrice') else 0,
                        volume=int(row.get('volume', 0)) if row.get('volume') else 0,
                        open_interest=int(row.get('openInterest', 0)) if row.get('openInterest') else 0,
                        implied_volatility=float(row.get('impliedVolatility', 0)) if row.get('impliedVolatility') else 0,
                        delta=float(row.get('delta', 0)) if row.get('delta') else None,
                        gamma=float(row.get('gamma', 0)) if row.get('gamma') else None,
                        theta=float(row.get('theta', 0)) if row.get('theta') else None,
                        vega=float(row.get('vega', 0)) if row.get('vega') else None,
                        rho=float(row.get('rho', 0)) if row.get('rho') else None,
                    ))
                
                for chain in chains:
                    chain.puts = [p for p in puts if p.expiry == chain.expiry_date]
            
            if not chains:
                return None
            
            return OptionsSummary(
                symbol=symbol,
                current_price=current_price,
                chains=chains,
                nearest_expiry=chains[0].expiry_date if chains else None
            )
        
        except Exception as e:
            print(f"Error fetching options for {symbol}: {e}")
            return None

    def calculate_breakeven(self, strike: float, premium: float, is_call: bool) -> float:
        """Calculate breakeven price for an option."""
        if is_call:
            return strike + premium
        return strike - premium

    def calculate_max_profit(self, strike: float, premium: float, is_call: bool, 
                            position: str = "long") -> float:
        """Calculate maximum profit for an option."""
        if position == "short":
            return premium
        
        if is_call:
            return float('inf')
        return strike - premium

    def calculate_max_loss(self, premium: float, position: str = "long") -> float:
        """Calculate maximum loss for an option."""
        if position == "short":
            return float('inf')
        return premium

    def calculate_intrinsic_value(self, stock_price: float, strike: float, 
                                   is_call: bool) -> float:
        """Calculate intrinsic value of an option."""
        if is_call:
            return max(0, stock_price - strike)
        return max(0, strike - stock_price)

    def calculate_time_value(self, premium: float, intrinsic_value: float) -> float:
        """Calculate time value (extrinsic value) of an option."""
        return max(0, premium - intrinsic_value)

    def get_nearest_atm_options(self, chain: OptionChain, 
                                count: int = 5) -> Dict[str, List[OptionContract]]:
        """Get ATM (at-the-money) options."""
        if not chain.calls:
            return {'calls': [], 'puts': []}
        
        mid_price = (chain.calls[0].bid + chain.calls[0].ask) / 2
        
        sorted_calls = sorted(chain.calls, key=lambda x: abs(x.strike - mid_price))
        sorted_puts = sorted(chain.puts, key=lambda x: abs(x.strike - mid_price))
        
        return {
            'calls': sorted_calls[:count],
            'puts': sorted_puts[:count]
        }


def create_module() -> OptionsModule:
    """Create options module."""
    return OptionsModule()
