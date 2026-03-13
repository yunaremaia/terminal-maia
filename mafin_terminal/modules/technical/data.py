"""Technical analysis module with indicators."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import numpy as np

from mafin_terminal.data.providers import YahooFinanceProvider


@dataclass
class IndicatorValue:
    """Indicator value with timestamp."""
    name: str
    value: float
    timestamp: str


@dataclass
class TechnicalAnalysis:
    """Complete technical analysis for a symbol."""
    symbol: str
    current_price: float
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index."""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices: List[float], 
                   fast: int = 12, slow: int = 26, signal: int = 9
                   ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Calculate MACD."""
    if len(prices) < slow:
        return None, None, None
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    if ema_fast is None or ema_slow is None:
        return None, None, None
    
    macd_line = ema_fast - ema_slow
    
    macd_values = []
    for i in range(slow, len(prices) + 1):
        ef = calculate_ema(prices[:i], fast)
        es = calculate_ema(prices[:i], slow)
        if ef and es:
            macd_values.append(ef - es)
    
    if len(macd_values) < signal:
        return macd_line, None, None
    
    signal_line = np.mean(macd_values[-signal:])
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: List[float], 
                              period: int = 20, 
                              std_dev: float = 2.0
                              ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Calculate Bollinger Bands."""
    if len(prices) < period:
        return None, None, None
    
    sma = np.mean(prices[-period:])
    std = np.std(prices[-period:])
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    return upper, sma, lower


def calculate_atr(high: List[float], low: List[float], close: List[float], 
                  period: int = 14) -> Optional[float]:
    """Calculate Average True Range."""
    if len(high) < period + 1:
        return None
    
    tr = []
    for i in range(1, len(high)):
        h_l = high[i] - low[i]
        h_c = abs(high[i] - close[i-1])
        l_c = abs(low[i] - close[i-1])
        tr.append(max(h_l, h_c, l_c))
    
    if len(tr) < period:
        return None
    
    return np.mean(tr[-period:])


def calculate_adx(high: List[float], low: List[float], close: List[float],
                   period: int = 14) -> Optional[float]:
    """Calculate Average Directional Index."""
    if len(high) < period + 1:
        return None
    
    plus_dm = []
    minus_dm = []
    tr = []
    
    for i in range(1, len(high)):
        high_diff = high[i] - high[i-1]
        low_diff = low[i-1] - low[i]
        
        plus_dm.append(high_diff if high_diff > low_diff and high_diff > 0 else 0)
        minus_dm.append(low_diff if low_diff > high_diff and low_diff > 0 else 0)
        
        tr.append(max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        ))
    
    if len(tr) < period:
        return None
    
    plus_di = 100 * (np.mean(plus_dm[-period:]) / np.mean(tr[-period:]))
    minus_di = 100 * (np.mean(minus_dm[-period:]) / np.mean(tr[-period:]))
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
    
    return dx


class TechnicalAnalysisModule:
    """Technical analysis module."""

    def __init__(self):
        self._provider = YahooFinanceProvider()

    async def analyze(self, symbol: str) -> Optional[TechnicalAnalysis]:
        """Perform complete technical analysis."""
        hist = await self._provider.get_historical(symbol, period="1y")
        
        if hist is None or len(hist.close) < 50:
            return None
        
        prices = hist.close
        high = hist.high
        low = hist.low
        
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        sma_200 = calculate_sma(prices, 200) if len(prices) >= 200 else None
        ema_12 = calculate_ema(prices, 12)
        ema_26 = calculate_ema(prices, 26)
        rsi = calculate_rsi(prices)
        macd, macd_signal, macd_hist = calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices)
        atr = calculate_atr(high, low, prices)
        adx = calculate_adx(high, low, prices)
        
        return TechnicalAnalysis(
            symbol=symbol.upper(),
            current_price=prices[-1],
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            ema_12=ema_12,
            ema_26=ema_26,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            atr=atr,
            adx=adx
        )

    async def get_chart_data(self, symbol: str, period: str = "1y"):
        """Get chart data for a symbol."""
        return await self._provider.get_historical(symbol, period)

    def get_indicator_value(self, indicator: str, value: Optional[float]) -> str:
        """Format indicator value for display."""
        if value is None:
            return "N/A"
        return f"{value:.2f}"

    def get_signal(self, analysis: TechnicalAnalysis) -> str:
        """Generate trading signal based on indicators."""
        signals = []
        
        if analysis.rsi:
            if analysis.rsi > 70:
                signals.append("RSI: Overbought")
            elif analysis.rsi < 30:
                signals.append("RSI: Oversold")
        
        if analysis.sma_20 and analysis.sma_50:
            if analysis.sma_20 > analysis.sma_50:
                signals.append("SMA: Bullish Crossover")
            else:
                signals.append("SMA: Bearish Crossover")
        
        if analysis.macd and analysis.macd_signal:
            if analysis.macd > analysis.macd_signal:
                signals.append("MACD: Bullish")
            else:
                signals.append("MACD: Bearish")
        
        if analysis.current_price and analysis.bb_upper:
            if analysis.current_price > analysis.bb_upper:
                signals.append("BB: Above Upper Band")
            elif analysis.current_price < analysis.bb_lower:
                signals.append("BB: Below Lower Band")
        
        return "; ".join(signals) if signals else "Neutral"


def create_module() -> TechnicalAnalysisModule:
    """Create technical analysis module."""
    return TechnicalAnalysisModule()
