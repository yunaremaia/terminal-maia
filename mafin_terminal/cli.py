"""MaFin Terminal - CLI Interactive Terminal."""

import asyncio
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from mafin_terminal.core import CommandParser, CommandType, ParsedCommand
from mafin_terminal.core.ui_renderer import TerminalRenderer, Color, TableColumn, TableStyle
from mafin_terminal.modules.market import MarketModule
from mafin_terminal.modules.portfolio import PortfolioManager
from mafin_terminal.modules.technical import TechnicalAnalysisModule
from mafin_terminal.modules.fundamental import FundamentalModule
from mafin_terminal.modules.risk import RiskAnalysisModule
from mafin_terminal.modules.economic import EconomicModule
from mafin_terminal.modules.news import NewsModule
from mafin_terminal.utils import get_config, get_logger


class CLITerminal:
    """Interactive CLI terminal like Bloomberg."""

    def __init__(self):
        self.parser = CommandParser()
        self.renderer = TerminalRenderer()
        self.config = get_config()
        self.logger = get_logger()
        
        self._modules: Dict[str, Any] = {}
        self._current_screen = "home"
        self._symbols: List[str] = []
        self._running = True
        
        self._setup_modules()
        self._setup_commands()

    def _setup_modules(self):
        """Setup data modules."""
        self._modules['market'] = MarketModule()
        self._modules['portfolio'] = PortfolioManager()
        self._modules['technical'] = TechnicalAnalysisModule()
        self._modules['fundamental'] = FundamentalModule()
        self._modules['risk'] = RiskAnalysisModule()
        self._modules['economic'] = EconomicModule()
        self._modules['news'] = NewsModule()
        
        portfolio = self._modules['portfolio'].create_portfolio("Default")
        portfolio.add_cash(100000)

    def _setup_commands(self):
        """Setup command handlers."""
        self._command_handlers = {
            CommandType.QUOTE: self._handle_quote,
            CommandType.CHART: self._handle_chart,
            CommandType.WATCH: self._handle_watch,
            CommandType.PORTFOLIO: self._handle_portfolio,
            CommandType.BUY: self._handle_buy,
            CommandType.SELL: self._handle_sell,
            CommandType.FUNDAMENTAL: self._handle_fundamental,
            CommandType.TECHNICAL: self._handle_technical,
            CommandType.RISK: self._handle_risk,
            CommandType.ECONOMIC: self._handle_economic,
            CommandType.NEWS: self._handle_news,
            CommandType.SEARCH: self._handle_search,
            CommandType.HELP: self._handle_help,
            CommandType.CLEAR: self._handle_clear,
            CommandType.QUIT: self._handle_quit,
            CommandType.SET: self._handle_set,
        }

    def _clear_screen(self):
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _print_banner(self):
        """Print terminal banner."""
        self._clear_screen()
        print(f"{Color.CYAN}{Color.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                                                                   ║")
        print("║     ██████╗ ███████╗ █████╗ ██████╗     ██████╗ ███╗   ██╗███████╗ ║")
        print("║     ██╔══██╗██╔════╝██╔══██╗██╔══██╗    ██╔══██╗████╗  ██║██╔════╝ ║")
        print("║     ██████╔╝█████╗  ███████║██║  ██║    ██████╔╝██╔██╗ ██║█████╗   ║")
        print("║     ██╔══██╗██╔══╝  ██╔══██║██║  ██║    ██╔══██╗██║╚██╗██║██╔══╝   ║")
        print("║     ██║  ██║███████╗██║  ██║██████╔╝    ██████╔╝██║ ╚████║███████╗ ║")
        print("║     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝     ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ║")
        print("║                                                                   ║")
        print("║              Professional Financial Terminal v1.0                 ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Color.RESET}")
        print()
        print(f"{Color.YELLOW}Type 'help' for available commands{Color.RESET}")
        print()

    async def _handle_quote(self, cmd: ParsedCommand):
        """Handle quote command."""
        if not cmd.symbol:
            print(f"{Color.RED}Usage: quote <symbol>{Color.RESET}")
            return

        quote = await self._modules['market'].get_quote(cmd.symbol)
        
        if quote:
            self.renderer.render_quote(
                quote.symbol,
                quote.price,
                quote.change,
                quote.change_percent,
                quote.volume,
                quote.name
            )
        else:
            print(f"{Color.RED}Could not fetch quote for {cmd.symbol}{Color.RESET}")

    async def _handle_chart(self, cmd: ParsedCommand):
        """Handle chart command."""
        if not cmd.symbol:
            print(f"{Color.RED}Usage: chart <symbol> [period]{Color.RESET}")
            return

        period = cmd.args[0] if cmd.args else "1y"
        data = await self._modules['market'].get_historical(cmd.symbol, period)
        
        if data and data.close:
            print(f"\n{Color.CYAN}Chart Data for {cmd.symbol} ({period}){Color.RESET}")
            print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
            print(f"Latest: ${data.close[-1]:.2f}")
            print(f"High: ${max(data.high):.2f}")
            print(f"Low: ${min(data.low):.2f}")
            print(f"Volume: {sum(data.volume):,}")
        else:
            print(f"{Color.RED}No data available for {cmd.symbol}{Color.RESET}")

    async def _handle_watch(self, cmd: ParsedCommand):
        """Handle watch command."""
        if cmd.args:
            for symbol in cmd.args:
                self._modules['market'].add_watch(symbol.upper())
            
            quotes = await self._modules['market'].get_watchlist()
            
            if quotes:
                self._show_quotes_table(quotes)
            else:
                print(f"{Color.YELLOW}Watchlist is empty{Color.RESET}")
        else:
            quotes = await self._modules['market'].get_watchlist()
            if quotes:
                self._show_quotes_table(quotes)
            else:
                print(f"{Color.YELLOW}Watchlist: {', '.join(self._modules['market'].market_data.get_watchlist()) or 'Empty'}{Color.RESET}")

    def _show_quotes_table(self, quotes: List):
        """Show quotes in table format."""
        columns = [
            TableColumn("Symbol", 10),
            TableColumn("Price", 12),
            TableColumn("Change", 12),
            TableColumn("Chg %", 10),
            TableColumn("Volume", 15),
        ]
        
        rows = []
        for q in quotes:
            change_str = f"{q.change:+,.2f}"
            pct_str = f"{q.change_percent:+,.2f}%"
            rows.append([q.symbol, f"${q.price:,.2f}", change_str, pct_str, f"{q.volume:,}"])
        
        print(self.renderer.render_table(columns, rows))

    async def _handle_portfolio(self, cmd: ParsedCommand):
        """Handle portfolio command."""
        portfolio = self._modules['portfolio'].get_default()
        
        await portfolio.update_prices()
        summary = portfolio.get_summary()
        positions = portfolio.get_positions()
        
        print(f"\n{Color.CYAN}Portfolio Summary{Color.RESET}")
        print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
        print(f"Cash:         ${summary.cash:,.2f}")
        print(f"Total Value:  ${summary.total_value:,.2f}")
        print(f"Total Cost:   ${summary.total_cost:,.2f}")
        
        pnl_color = Color.GREEN if summary.total_pnl >= 0 else Color.RED
        print(f"Total P&L:    {pnl_color}${summary.total_pnl:+,.2f} ({summary.total_pnl_percent:+,.2f}%){Color.RESET}")
        
        if positions:
            print(f"\n{Color.CYAN}Positions{Color.RESET}")
            columns = [
                TableColumn("Symbol", 10),
                TableColumn("Qty", 8),
                TableColumn("Avg Cost", 12),
                TableColumn("Current", 12),
                TableColumn("Value", 14),
                TableColumn("P&L", 12),
                TableColumn("P&L %", 8),
            ]
            
            rows = []
            for p in positions:
                pnl_str = f"${p.unrealized_pnl:+,.2f}"
                pnl_pct_str = f"{p.unrealized_pnl_percent:+,.2f}%"
                rows.append([
                    p.symbol,
                    f"{p.quantity:.0f}",
                    f"${p.avg_cost:,.2f}",
                    f"${p.current_price:,.2f}",
                    f"${p.market_value:,.2f}",
                    pnl_str,
                    pnl_pct_str
                ])
            
            print(self.renderer.render_table(columns, rows))

    async def _handle_buy(self, cmd: ParsedCommand):
        """Handle buy command."""
        if len(cmd.args) < 3:
            print(f"{Color.RED}Usage: buy <symbol> <quantity> <price>{Color.RESET}")
            return

        symbol = cmd.args[0].upper()
        quantity = float(cmd.args[1])
        price = float(cmd.args[2])

        portfolio = self._modules['portfolio'].get_default()
        success = portfolio.buy(symbol, quantity, price)

        if success:
            print(f"{Color.GREEN}Bought {quantity} shares of {symbol} at ${price}{Color.RESET}")
        else:
            print(f"{Color.RED}Insufficient funds or invalid position{Color.RESET}")

    async def _handle_sell(self, cmd: ParsedCommand):
        """Handle sell command."""
        if len(cmd.args) < 3:
            print(f"{Color.RED}Usage: sell <symbol> <quantity> <price>{Color.RESET}")
            return

        symbol = cmd.args[0].upper()
        quantity = float(cmd.args[1])
        price = float(cmd.args[2])

        portfolio = self._modules['portfolio'].get_default()
        success = portfolio.sell(symbol, quantity, price)

        if success:
            print(f"{Color.GREEN}Sold {quantity} shares of {symbol} at ${price}{Color.RESET}")
        else:
            print(f"{Color.RED}Insufficient shares{Color.RESET}")

    async def _handle_technical(self, cmd: ParsedCommand):
        """Handle technical analysis command."""
        if not cmd.symbol:
            print(f"{Color.RED}Usage: technical <symbol>{Color.RESET}")
            return

        analysis = await self._modules['technical'].analyze(cmd.symbol)
        
        if analysis:
            print(f"\n{Color.CYAN}Technical Analysis - {cmd.symbol}{Color.RESET}")
            print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
            print(f"Current Price: ${analysis.current_price:.2f}")
            
            print(f"\n{Color.YELLOW}Moving Averages{Color.RESET}")
            print(f"  SMA 20:  ${analysis.sma_20:.2f if analysis.sma_20 else 'N/A'}")
            print(f"  SMA 50:  ${analysis.sma_50:.2f if analysis.sma_50 else 'N/A'}")
            print(f"  SMA 200: ${analysis.sma_200:.2f if analysis.sma_200 else 'N/A'}")
            print(f"  EMA 12:  ${analysis.ema_12:.2f if analysis.ema_12 else 'N/A'}")
            print(f"  EMA 26:  ${analysis.ema_26:.2f if analysis.ema_26 else 'N/A'}")
            
            print(f"\n{Color.YELLOW}Momentum{Color.RESET}")
            print(f"  RSI (14):     {analysis.rsi:.2f if analysis.rsi else 'N/A'}")
            print(f"  MACD:         {analysis.macd:.4f if analysis.macd else 'N/A'}")
            print(f"  MACD Signal:  {analysis.macd_signal:.4f if analysis.macd_signal else 'N/A'}")
            print(f"  MACD Hist:    {analysis.macd_histogram:.4f if analysis.macd_histogram else 'N/A'}")
            
            print(f"\n{Color.YELLOW}Volatility{Color.RESET}")
            print(f"  BB Upper:  ${analysis.bb_upper:.2f if analysis.bb_upper else 'N/A'}")
            print(f"  BB Middle: ${analysis.bb_middle:.2f if analysis.bb_middle else 'N/A'}")
            print(f"  BB Lower:  ${analysis.bb_lower:.2f if analysis.bb_lower else 'N/A'}")
            print(f"  ATR:       {analysis.atr:.2f if analysis.atr else 'N/A'}")
            print(f"  ADX:       {analysis.adx:.2f if analysis.adx else 'N/A'}")
            
            signals = self._modules['technical'].get_signal(analysis)
            print(f"\n{Color.CYAN}Signals: {signals}{Color.RESET}")
        else:
            print(f"{Color.RED}Could not analyze {cmd.symbol}{Color.RESET}")

    async def _handle_fundamental(self, cmd: ParsedCommand):
        """Handle fundamental analysis command."""
        if not cmd.symbol:
            print(f"{Color.RED}Usage: fundamental <symbol>{Color.RESET}")
            return

        data = await self._modules['fundamental'].analyze(cmd.symbol)
        
        if data:
            profile = data.get('profile')
            metrics = data.get('metrics')
            analyst = data.get('analyst')
            
            print(f"\n{Color.CYAN}Fundamental Analysis - {cmd.symbol}{Color.RESET}")
            print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
            
            if profile:
                print(f"\n{Color.YELLOW}Company{Color.RESET}")
                print(f"  Name:     {profile.name}")
                print(f"  Industry: {profile.industry}")
                print(f"  Sector:   {profile.sector}")
            
            if metrics:
                print(f"\n{Color.YELLOW}Key Metrics{Color.RESET}")
                if metrics.market_cap:
                    print(f"  Market Cap:  ${metrics.market_cap:,.0f}")
                if metrics.pe_ratio:
                    print(f"  P/E Ratio:    {metrics.pe_ratio:.2f}")
                if metrics.eps:
                    print(f"  EPS:          ${metrics.eps:.2f}")
                if metrics.dividend_yield:
                    print(f"  Div Yield:    {metrics.dividend_yield * 100:.2f}%")
                if metrics.beta:
                    print(f"  Beta:         {metrics.beta:.2f}")
                if metrics.roe:
                    print(f"  ROE:          {metrics.roe * 100:.2f}%")
                if metrics.profit_margin:
                    print(f"  Profit Margin:{metrics.profit_margin * 100:.2f}%")
            
            if analyst:
                print(f"\n{Color.YELLOW}Analyst{Color.RESET}")
                print(f"  Rating:      {analyst.rating}")
                if analyst.target_price:
                    print(f"  Target Price: ${analyst.target_price:.2f}")
        else:
            print(f"{Color.RED}Could not analyze {cmd.symbol}{Color.RESET}")

    async def _handle_risk(self, cmd: ParsedCommand):
        """Handle risk analysis command."""
        symbol = cmd.symbol or cmd.args[0] if cmd.args else None
        
        if not symbol:
            print(f"{Color.RED}Usage: risk <symbol>{Color.RESET}")
            return

        metrics = await self._modules['risk'].get_risk_metrics(symbol)
        
        if metrics:
            print(f"\n{Color.CYAN}Risk Analysis - {symbol}{Color.RESET}")
            print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
            print(f"  Volatility:    {metrics.volatility * 100:.2f}%" if metrics.volatility else "  Volatility:    N/A")
            print(f"  Beta:          {metrics.beta:.2f}" if metrics.beta else "  Beta:          N/A")
            print(f"  Sharpe Ratio:  {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "  Sharpe Ratio:  N/A")
            print(f"  Sortino Ratio:{metrics.sortino_ratio:.2f}" if metrics.sortino_ratio else "  Sortino Ratio: N/A")
            print(f"  Max Drawdown: {metrics.max_drawdown * 100:.2f}%" if metrics.max_drawdown else "  Max Drawdown:  N/A")
            print(f"  VaR (95%):    {metrics.var_95 * 100:.2f}%" if metrics.var_95 else "  VaR (95%):     N/A")
            print(f"  CVaR (95%):   {metrics.cvar_95 * 100:.2f}%" if metrics.cvar_95 else "  CVaR (95%):    N/A")
        else:
            print(f"{Color.RED}Could not analyze {symbol}{Color.RESET}")

    async def _handle_economic(self, cmd: ParsedCommand):
        """Handle economic data command."""
        data = await self._modules['economic'].get_market_overview()
        
        print(f"\n{Color.CYAN}Economic Data{Color.RESET}")
        print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
        
        if data.get('indices'):
            print(f"\n{Color.YELLOW}Indices{Color.RESET}")
            columns = [TableColumn("Name", 20), TableColumn("Price", 12), TableColumn("Change", 12)]
            rows = [[i.name, f"{i.price:.2f}", f"{i.change_percent:+.2f}%"] for i in data['indices'][:5]]
            print(self.renderer.render_table(columns, rows))
        
        if data.get('currencies'):
            print(f"\n{Color.YELLOW}Currencies{Color.RESET}")
            columns = [TableColumn("Pair", 15), TableColumn("Price", 12), TableColumn("Change", 12)]
            rows = [[c.name, f"{c.price:.4f}", f"{c.change_percent:+.2f}%"] for c in data['currencies'][:5]]
            print(self.renderer.render_table(columns, rows))
        
        if data.get('commodities'):
            print(f"\n{Color.YELLOW}Commodities{Color.RESET}")
            columns = [TableColumn("Name", 20), TableColumn("Price", 12), TableColumn("Change", 12)]
            rows = [[c.name, f"{c.price:.2f}", f"{c.change_percent:+.2f}%"] for c in data['commodities'][:5]]
            print(self.renderer.render_table(columns, rows))

    async def _handle_news(self, cmd: ParsedCommand):
        """Handle news command."""
        if cmd.symbol:
            news_data = await self._modules['news'].get_symbol_news(cmd.symbol, 10)
            items = news_data.news
        else:
            items = await self._modules['news'].get_market_news(15)
        
        print(f"\n{Color.CYAN}Market News{Color.RESET}")
        print(f"{Color.DIM}{'=' * 60}{Color.RESET}")
        
        for i, item in enumerate(items, 1):
            print(f"\n{i}. {item.title}")
            print(f"   {item.publisher} - {item.published[:10] if item.published else 'N/A'}")

    async def _handle_search(self, cmd: ParsedCommand):
        """Handle search command."""
        if not cmd.raw_args:
            print(f"{Color.RED}Usage: search <query>{Color.RESET}")
            return

        results = await self._modules['market'].search_symbol(cmd.raw_args)
        
        if results:
            print(f"\n{Color.CYAN}Search Results{Color.RESET}")
            columns = [TableColumn("Symbol", 10), TableColumn("Name", 30), TableColumn("Exchange", 12), TableColumn("Type", 10)]
            rows = [[r.get('symbol', ''), r.get('name', '')[:28], r.get('exchange', ''), r.get('type', '')] for r in results[:10]]
            print(self.renderer.render_table(columns, rows))
        else:
            print(f"{Color.YELLOW}No results found{Color.RESET}")

    def _handle_help(self, cmd: ParsedCommand):
        """Handle help command."""
        print(self.parser.format_help())

    def _handle_clear(self, cmd: ParsedCommand):
        """Handle clear command."""
        self._clear_screen()

    def _handle_quit(self, cmd: ParsedCommand):
        """Handle quit command."""
        print(f"\n{Color.YELLOW}Thank you for using MaFin Terminal!{Color.RESET}\n")
        self._running = False

    def _handle_set(self, cmd: ParsedCommand):
        """Handle set command."""
        if cmd.options.get('key') and cmd.options.get('value'):
            self.config.set(cmd.options['key'], cmd.options['value'])
            print(f"{Color.GREEN}Set {cmd.options['key']} = {cmd.options['value']}{Color.RESET}")
        else:
            print(f"{Color.RED}Usage: set <key> <value>{Color.RESET}")

    async def process_command(self, input_str: str):
        """Process a command."""
        cmd = self.parser.parse(input_str)
        
        if cmd.type == CommandType.UNKNOWN:
            print(f"{Color.RED}Unknown command: {input_str}{Color.RESET}")
            print(f"{Color.YELLOW}Type 'help' for available commands{Color.RESET}")
            return
        
        handler = self._command_handlers.get(cmd.type)
        if handler:
            await handler(cmd)

    def run(self):
        """Run the terminal."""
        self._print_banner()
        
        while self._running:
            try:
                prompt = f"{Color.CYAN}MAFIN{Color.RESET} > "
                input_str = input(prompt).strip()
                
                if input_str:
                    asyncio.run(self.process_command(input_str))
            
            except KeyboardInterrupt:
                print(f"\n{Color.YELLOW}Use 'quit' to exit{Color.RESET}")
            except Exception as e:
                print(f"{Color.RED}Error: {e}{Color.RESET}")


def launch_cli():
    """Launch CLI terminal."""
    terminal = CLITerminal()
    terminal.run()


if __name__ == "__main__":
    launch_cli()
