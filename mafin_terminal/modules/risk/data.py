"""Risk analysis module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import numpy as np
import yfinance as yf


@dataclass
class RiskMetrics:
    """Portfolio risk metrics."""
    volatility: Optional[float]
    beta: Optional[float]
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    max_drawdown: Optional[float]
    var_95: Optional[float]
    cvar_95: Optional[float]


@dataclass
class PositionRisk:
    """Risk metrics for a single position."""
    symbol: str
    weight: float
    beta: float
    volatility: float
    var_95: float


class RiskAnalysisModule:
    """Risk analysis module."""

    def __init__(self):
        self._risk_free_rate = 0.05

    async def get_risk_metrics(self, symbol: str, period: str = "1y") -> Optional[RiskMetrics]:
        """Get risk metrics for a symbol."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period=period))
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            if hist.empty:
                return None
            
            returns = hist['Close'].pct_change().dropna()
            
            volatility = returns.std() * np.sqrt(252)
            beta = info.get('beta', None)
            
            mean_return = returns.mean() * 252
            sharpe = (mean_return - self._risk_free_rate) / volatility if volatility > 0 else None
            
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
            sortino = (mean_return - self._risk_free_rate) / downside_std if downside_std > 0 else None
            
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            var_95 = np.percentile(returns, 5)
            cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else None
            
            return RiskMetrics(
                volatility=volatility,
                beta=beta,
                sharpe_ratio=sharpe,
                sortino_ratio=sortino,
                max_drawdown=max_drawdown,
                var_95=var_95,
                cvar_95=cvar_95
            )
        except Exception as e:
            print(f"Error calculating risk metrics for {symbol}: {e}")
            return None

    async def calculate_portfolio_risk(self, symbols: List[str], weights: List[float]) -> RiskMetrics:
        """Calculate portfolio-level risk metrics."""
        try:
            if len(symbols) != len(weights):
                raise ValueError("Number of symbols must match number of weights")
            
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            loop = asyncio.get_event_loop()
            
            all_returns = []
            betas = []
            volatilities = []
            
            for symbol in symbols:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                hist = await loop.run_in_executor(None, lambda: ticker.history(period="1y"))
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if not hist.empty:
                    returns = hist['Close'].pct_change().dropna()
                    all_returns.append(returns)
                    volatilities.append(returns.std() * np.sqrt(252))
                    betas.append(info.get('beta', 1.0) or 1.0)
            
            if not all_returns:
                return None
            
            aligned_returns = all_returns[0].copy()
            for returns in all_returns[1:]:
                aligned_returns = aligned_returns.add(returns, fill_value=0)
            aligned_returns = aligned_returns.dropna() / len(all_returns)
            
            portfolio_return = aligned_returns.mean() * 252
            portfolio_vol = aligned_returns.std() * np.sqrt(252)
            
            weighted_beta = sum(w * b for w, b in zip(weights, betas))
            
            sharpe = (portfolio_return - self._risk_free_rate) / portfolio_vol if portfolio_vol > 0 else None
            
            downside = aligned_returns[aligned_returns < 0]
            downside_std = downside.std() * np.sqrt(252) if len(downside) > 0 else 0
            sortino = (portfolio_return - self._risk_free_rate) / downside_std if downside_std > 0 else None
            
            cumulative = (1 + aligned_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            var_95 = np.percentile(aligned_returns, 5)
            cvar_95 = aligned_returns[aligned_returns <= var_95].mean()
            
            return RiskMetrics(
                volatility=portfolio_vol,
                beta=weighted_beta,
                sharpe_ratio=sharpe,
                sortino_ratio=sortino,
                max_drawdown=max_drawdown,
                var_95=var_95,
                cvar_95=cvar_95
            )
        except Exception as e:
            print(f"Error calculating portfolio risk: {e}")
            return None

    async def get_correlation_matrix(self, symbols: List[str]) -> Optional[Dict]:
        """Calculate correlation matrix for symbols."""
        try:
            loop = asyncio.get_event_loop()
            
            all_returns = []
            valid_symbols = []
            
            for symbol in symbols:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                hist = await loop.run_in_executor(None, lambda: ticker.history(period="1y"))
                
                if not hist.empty:
                    returns = hist['Close'].pct_change().dropna()
                    all_returns.append(returns)
                    valid_symbols.append(symbol)
            
            if len(valid_symbols) < 2:
                return None
            
            df = all_returns[0].to_frame(valid_symbols[0])
            for i, returns in enumerate(all_returns[1:], 1):
                df[valid_symbols[i]] = returns
            
            corr_matrix = df.corr()
            
            return {
                'symbols': valid_symbols,
                'matrix': corr_matrix.to_dict()
            }
        except Exception as e:
            print(f"Error calculating correlation matrix: {e}")
            return None

    def run_stress_test(self, portfolio_weights: Dict[str, float], 
                        scenario: str = "crash") -> Dict:
        """Run stress test on portfolio."""
        scenarios = {
            'crash': {'market': -0.30, 'volatility_mult': 2.0},
            'rally': {'market': 0.20, 'volatility_mult': 0.8},
            'volatility_spike': {'market': -0.10, 'volatility_mult': 3.0},
            'interest_rate_hike': {'market': -0.15, 'volatility_mult': 1.5}
        }
        
        scenario_params = scenarios.get(scenario, scenarios['crash'])
        market_impact = scenario_params['market']
        
        results = {}
        for symbol, weight in portfolio_weights.items():
            symbol_impact = market_impact * (weight * 1.2)
            results[symbol] = {
                'weight': weight,
                'estimated_impact': symbol_impact
            }
        
        total_impact = sum(r['estimated_impact'] for r in results.values())
        
        return {
            'scenario': scenario,
            'position_impacts': results,
            'portfolio_impact': total_impact,
            'params': scenario_params
        }


def create_module() -> RiskAnalysisModule:
    """Create risk analysis module."""
    return RiskAnalysisModule()
