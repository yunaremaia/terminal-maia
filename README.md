# MaFin Terminal

**Professional Financial Terminal for Investors**

---

## Overview

MaFin Terminal is an open-source, fullscreen graphical financial terminal designed to provide professional-grade market data, portfolio analytics, and financial analysis tools—modeled after the legendary Bloomberg Terminal—at a fraction of the cost.

The terminal features **multi-monitor support**: when launched, it automatically detects all connected monitors and their resolutions, then opens in fullscreen mode occupying all available screen space across all displays.

Built with Python and PyQt6, MaFin Terminal delivers real-time market data, charting capabilities, portfolio management, risk analysis, and economic indicators through an intuitive interface optimized for speed and efficiency.

---

## Key Features

### Multi-Monitor Display
- **Automatic Monitor Detection**: Detects the number of connected monitors and their resolutions on startup
- **Fullscreen Mode**: Opens in fullscreen occupying all available space across all displays
- **Flexible Layout**: Optimized layout that utilizes the entire screen real estate

### Market Data & Quotes
- **Real-time Quotes**: Get instant access to stock, ETF, forex, cryptocurrency, and commodity prices
- **Level 2 Market Data**: View bid/ask depths, order book visualization, and market depth
- **Market Movers**: Track top gainers, losers, and most active securities
- **Pre/Post Market Data**: Access extended trading hours data

### Technical Analysis
- **Advanced Charting**: Interactive candlestick, line, and OHLC charts
- **100+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic, ADX, and more
- **Drawing Tools**: Trendlines, Fibonacci retracements, support/resistance levels
- **Multiple Timeframes**: Intraday, daily, weekly, monthly views

### Fundamental Analysis
- **Company Profiles**: Executive leadership, business description, competitors
- **Financial Statements**: Income statement, balance sheet, cash flow (quarterly/annual)
- **Key Metrics**: P/E ratio, EPS, market cap, dividend yield, beta, ROE, ROA
- **Analyst Ratings**: Consensus ratings, price targets, earnings estimates

### Portfolio Management
- **Holdings Tracker**: Monitor multiple portfolios with real-time P&L
- **Transaction Logging**: Record buys, sells, dividends, and splits
- **Performance Analytics**: Returns, Sharpe ratio, volatility, max drawdown
- **Asset Allocation**: Visual breakdown by sector, geography, currency

### Risk Analysis
- **Value at Risk (VaR)**: Calculate portfolio risk exposure
- **Beta & Correlation**: Measure systematic risk and asset relationships
- **Stress Testing**: Simulate market scenarios (crash, rally, volatility spike)
- **Credit Analysis**: Corporate bond yields, credit ratings, spreads

### Economic Data
- **Macro Indicators**: GDP, CPI, unemployment, interest rates
- **Central Bank Policies**: Fed, ECB, BOJ, and other major central banks
- **Global Markets**: International indices, currencies, commodities
- **Economic Calendar**: Upcoming events, earnings, dividends, IPOs

### News & Research
- **Real-time News**: Breaking financial news from multiple sources
- **Sentiment Analysis**: AI-powered market sentiment indicators
- **SEC Filings**: 10-K, 10-Q, 8-K, insider trading alerts
- **Analyst Reports**: Summary of analyst recommendations

---

## Architecture

```
mafin-terminal/
├── mafin_terminal/           # Main application package
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Application entry point
│   ├── gui/                  # GUI components
│   │   ├── main_window.py   # Main window with multi-monitor support
│   │   ├── monitor_detector.py # Monitor detection and resolution
│   │   └── widgets/         # Reusable UI widgets
│   ├── core/                # Core terminal engine
│   │   ├── command_parser.py # Command parsing and execution
│   │   ├── keyboard_handler.py # Keyboard input management
│   │   ├── screen_manager.py   # Multi-window screen management
│   │   └── ui_renderer.py      # Terminal UI rendering
│   ├── modules/              # Feature modules
│   │   ├── market/           # Market data (quotes, depth, movers)
│   │   ├── portfolio/        # Portfolio management
│   │   ├── technical/        # Charting and technical analysis
│   │   ├── fundamental/      # Company fundamentals
│   │   ├── risk/            # Risk analytics
│   │   ├── economic/         # Economic data
│   │   └── news/             # News and research
│   ├── data/                 # Data providers and caching
│   │   ├── providers/        # API integrations
│   │   └── cache/            # Local data caching
│   └── utils/                # Utilities
│       ├── config.py         # Configuration management
│       ├── logger.py         # Logging system
│       └── database.py       # SQLite database operations
├── tests/                    # Unit and integration tests
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI Framework | PyQt6 |
| Multi-Monitor | QDesktopWidget (Qt) |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Plotly |
| Database | SQLite |
| Async I/O | asyncio, aiohttp |
| Testing | pytest, pytest-asyncio |

---

## Monitor Detection

The application automatically detects all connected monitors on startup:

```python
from mafin_terminal.gui.monitor_detector import MonitorDetector

detector = MonitorDetector()
monitors = detector.get_all_monitors()

for i, monitor in enumerate(monitors):
    print(f"Monitor {i+1}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
```

This information is used to:
- Set the optimal window size
- Position windows across multiple monitors
- Enable fullscreen mode spanning all displays

---

## Data Providers

MaFin Terminal integrates with multiple free and paid data sources:

- **Yahoo Finance** (free tier)
- **Alpha Vantage** (free tier available)
- **Financial Modeling Prep** (free tier available)
- **Finnhub** (free tier available)
- **Polygon.io** (free tier available)

*Note: Some features require API keys. Free tiers have rate limits.*

---

## Installation

### Prerequisites

```bash
# Python 3.10 or higher required
python --version  # Verify Python version
```

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mafin-terminal.git
cd mafin-terminal

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp config.example.yaml config.yaml

# Add your API keys to config.yaml
```

### First Launch

```bash
python -m mafin_terminal
```

The application will:
1. Detect all connected monitors
2. Display the detected monitor configuration
3. Open in fullscreen mode across all monitors

---

## Configuration

Edit `config.yaml` to customize your terminal:

```yaml
display:
  fullscreen: true
  theme: "dark"
  color_scheme: "bloomberg_orange"
  font_size: 14

multi_monitor:
  use_all_monitors: true
  primary_monitor_only: false

data_providers:
  yahoo_finance:
    enabled: true
  alpha_vantage:
    enabled: false
    api_key: "YOUR_API_KEY"

portfolio:
  default_currency: "USD"
  display_currency: "USD"

logging:
  level: "INFO"
  file: "logs/mafin.log"
```

---

## Supported Assets

| Asset Class | Examples |
|-------------|----------|
| Equities | AAPL, MSFT, GOOGL, TSLA |
| ETFs | SPY, QQQ, IWM, VTI |
| Forex | EUR/USD, GBP/USD, USD/JPY |
| Crypto | BTC/USD, ETH/USD, SOL/USD |
| Commodities | GOLD, SILVER, OIL, NATGAS |
| Indices | ^GSPC (S&P 500), ^DJI, ^IXIC |
| Bonds | ^TNX (10Y Treasury) |

---

## Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

- Report bugs and suggest features
- Improve documentation
- Add new data providers
- Create new analysis modules
- Submit pull requests

---

## Roadmap

### Phase 1 - Foundation (v0.1)
- [x] Multi-monitor detection and fullscreen support
- [x] Core GUI framework with PyQt6
- [x] Basic quote functionality

### Phase 2 - Market Data (v0.2)
- [ ] Level 2 market data
- [ ] Advanced charting
- [ ] Technical indicators

### Phase 3 - Analytics (v0.3)
- [ ] Portfolio management
- [ ] Risk analytics
- [ ] Backtesting engine

### Phase 4 - Professional (v0.4)
- [ ] Options chains
- [ ] Options analytics
- [ ] Algorithmic trading interface

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice, investment recommendations, or trading signals. Past performance does not guarantee future results. Use at your own risk.

---

## Acknowledgments

- Inspired by the Bloomberg Terminal
- Built with the open-source community
- Data providers for making financial data accessible

---

## Contact

- GitHub Issues: https://github.com/yourusername/mafin-terminal/issues
- Discussions: https://github.com/yourusername/mafin-terminal/discussions

---

*MaFin Terminal - Professional-grade financial analysis for everyone.*
