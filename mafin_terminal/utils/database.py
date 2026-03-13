"""Database utilities for MaFin Terminal."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'mafin_terminal.db')
        
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_schema()

    def _ensure_db_dir(self):
        """Ensure database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_schema(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    added_at TEXT NOT NULL,
                    notes TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    portfolio_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    fees REAL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_cache (
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    change REAL NOT NULL,
                    change_percent REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    PRIMARY KEY (symbol, timestamp)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def add_to_watchlist(self, symbol: str, notes: str = "") -> bool:
        """Add symbol to watchlist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO watchlist (symbol, added_at, notes) VALUES (?, ?, ?)",
                    (symbol.upper(), datetime.now().isoformat(), notes)
                )
                return True
        except sqlite3.IntegrityError:
            return False

    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove symbol from watchlist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
            return cursor.rowcount > 0

    def get_watchlist(self) -> List[Dict[str, Any]]:
        """Get watchlist symbols."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM watchlist ORDER BY added_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def save_transaction(self, portfolio_name: str, transaction: Dict):
        """Save transaction to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions 
                (id, portfolio_name, symbol, type, quantity, price, date, fees, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.get('id'),
                portfolio_name,
                transaction.get('symbol'),
                transaction.get('type'),
                transaction.get('quantity'),
                transaction.get('price'),
                transaction.get('date'),
                transaction.get('fees', 0),
                transaction.get('notes', ''),
                datetime.now().isoformat()
            ))

    def get_transactions(self, portfolio_name: str, symbol: Optional[str] = None) -> List[Dict]:
        """Get transactions for a portfolio."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if symbol:
                cursor.execute(
                    "SELECT * FROM transactions WHERE portfolio_name = ? AND symbol = ? ORDER BY date DESC",
                    (portfolio_name, symbol.upper())
                )
            else:
                cursor.execute(
                    "SELECT * FROM transactions WHERE portfolio_name = ? ORDER BY date DESC",
                    (portfolio_name,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def cache_price(self, symbol: str, price: float, change: float, change_percent: float):
        """Cache price data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_cache (symbol, price, change, change_percent, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol.upper(), price, change, change_percent, datetime.now().isoformat()))

    def get_cached_price(self, symbol: str) -> Optional[Dict]:
        """Get cached price for symbol."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM price_cache 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (symbol.upper(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def set_setting(self, key: str, value: Any):
        """Save setting to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now().isoformat()))

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting from database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row['value'])
            return default


import os

_db_instance: Optional[Database] = None


def get_database(db_path: Optional[str] = None) -> Database:
    """Get global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
