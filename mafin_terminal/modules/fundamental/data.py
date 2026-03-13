"""Fundamental analysis module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict
import yfinance as yf


@dataclass
class CompanyProfile:
    """Company profile information."""
    symbol: str
    name: str
    industry: str
    sector: str
    employees: Optional[int]
    website: str
    description: str
    ceo: Optional[str]
    headquarters: Optional[str]
    founded: Optional[int]


@dataclass
class FinancialStatement:
    """Financial statement data."""
    period: str
    date: str
    revenue: Optional[float]
    net_income: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    equity: Optional[float]
    operating_cash_flow: Optional[float]
    free_cash_flow: Optional[float]


@dataclass
class KeyMetrics:
    """Key financial metrics."""
    symbol: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    eps: Optional[float]
    beta: Optional[float]
    dividend_yield: Optional[float]
    payout_ratio: Optional[float]
    profit_margin: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    debt_to_equity: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]


@dataclass
class AnalystData:
    """Analyst recommendations."""
    symbol: str
    rating: str
    target_price: Optional[float]
    low_target: Optional[float]
    high_target: Optional[float]
    mean_target: Optional[float]
    number_of_analysts: int
    recommendations: Dict[str, int]


class FundamentalModule:
    """Fundamental analysis module."""

    def __init__(self):
        self._provider = None

    async def get_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            if not info:
                return None

            return CompanyProfile(
                symbol=symbol.upper(),
                name=info.get('shortName', info.get('longName', '')),
                industry=info.get('industry', 'N/A'),
                sector=info.get('sector', 'N/A'),
                employees=info.get('fullTimeEmployees'),
                website=info.get('website', ''),
                description=info.get('longBusinessSummary', ''),
                ceo=info.get('ceo'),
                headquarters=info.get('city', '') + ', ' + info.get('country', '') if info.get('city') else None,
                founded=info.get('foundedDate', None)
            )
        except Exception as e:
            print(f"Error fetching profile for {symbol}: {e}")
            return None

    async def get_key_metrics(self, symbol: str) -> Optional[KeyMetrics]:
        """Get key financial metrics."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            if not info:
                return None

            return KeyMetrics(
                symbol=symbol.upper(),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                eps=info.get('trailingEps'),
                beta=info.get('beta'),
                dividend_yield=info.get('dividendYield'),
                payout_ratio=info.get('payoutRatio'),
                profit_margin=info.get('profitMargins'),
                roe=info.get('returnOnEquity'),
                roa=info.get('returnOnAssets'),
                debt_to_equity=info.get('debtToEquity'),
                current_ratio=info.get('currentRatio'),
                quick_ratio=info.get('quickRatio')
            )
        except Exception as e:
            print(f"Error fetching metrics for {symbol}: {e}")
            return None

    async def get_income_statement(self, symbol: str, period: str = "annual") -> List[FinancialStatement]:
        """Get income statement."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            income = await loop.run_in_executor(
                None, 
                lambda: ticker.income_statement if period == "annual" else ticker.quarterly_income_statement
            )
            
            if income is None or income.empty:
                return []
            
            statements = []
            for idx, row in income.iterrows():
                statements.append(FinancialStatement(
                    period=period,
                    date=str(idx),
                    revenue=row.get('TotalRevenue'),
                    net_income=row.get('NetIncome'),
                    total_assets=row.get('TotalAssets'),
                    total_liabilities=row.get('TotalLiabilities'),
                    equity=row.get('TotalStockholderEquity'),
                    operating_cash_flow=row.get('OperatingCashflow'),
                    free_cash_flow=row.get('FreeCashFlow')
                ))
            
            return statements[:5]
        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {e}")
            return []

    async def get_analyst_data(self, symbol: str) -> Optional[AnalystData]:
        """Get analyst recommendations."""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            recommendations = await loop.run_in_executor(None, lambda: ticker.recommendations)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            if not info:
                return None
            
            recommendations_dict = {}
            if recommendations is not None and not recommendations.empty:
                for _, row in recommendations.head(5).iterrows():
                    rating = row.get('ToGrade', 'N/A')
                    recommendations_dict[rating] = recommendations_dict.get(rating, 0) + 1

            return AnalystData(
                symbol=symbol.upper(),
                rating=info.get('recommendationKey', 'N/A'),
                target_price=info.get('targetMeanPrice'),
                low_target=info.get('targetLowPrice'),
                high_target=info.get('targetHighPrice'),
                mean_target=info.get('targetMeanPrice'),
                number_of_analysts=info.get('numberOfAnalystOpinions', 0),
                recommendations=recommendations_dict
            )
        except Exception as e:
            print(f"Error fetching analyst data for {symbol}: {e}")
            return None

    async def analyze(self, symbol: str) -> Dict:
        """Get complete fundamental analysis."""
        profile = await self.get_profile(symbol)
        metrics = await self.get_key_metrics(symbol)
        analyst = await self.get_analyst_data(symbol)
        income = await self.get_income_statement(symbol)
        
        return {
            'profile': profile,
            'metrics': metrics,
            'analyst': analyst,
            'income_statement': income
        }


def create_module() -> FundamentalModule:
    """Create fundamental module."""
    return FundamentalModule()
