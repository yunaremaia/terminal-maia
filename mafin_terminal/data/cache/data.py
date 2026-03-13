"""Data cache module."""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Cache entry with value and expiration."""
    value: Any
    timestamp: float
    ttl: float
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl <= 0:
            return False
        return time.time() - self.timestamp > self.ttl


class DataCache:
    """In-memory data cache with TTL support."""

    def __init__(self, default_ttl: float = 60.0):
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self._hits += 1
                return entry.value
            else:
                del self._cache[key]
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        ttl = ttl if ttl is not None else self._default_ttl
        self._cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl
        )
    
    def delete(self, key: str):
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def cleanup(self):
        """Remove expired entries."""
        expired = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired:
            del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate
        }


class QuoteCache:
    """Specialized cache for quotes."""

    def __init__(self, ttl: float = 15.0):
        self._cache = DataCache(ttl)
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get cached quote."""
        return self._cache.get(f"quote:{symbol}")
    
    def set_quote(self, symbol: str, data: Dict):
        """Cache quote data."""
        self._cache.set(f"quote:{symbol}", data)
    
    def invalidate_quote(self, symbol: str):
        """Invalidate quote cache."""
        self._cache.delete(f"quote:{symbol}")
    
    def invalidate_all_quotes(self):
        """Clear all quotes."""
        self._cache.clear()


_cache_instance: Optional[DataCache] = None
_quote_cache_instance: Optional[QuoteCache] = None


def get_cache() -> DataCache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
    return _cache_instance


def get_quote_cache() -> QuoteCache:
    """Get global quote cache instance."""
    global _quote_cache_instance
    if _quote_cache_instance is None:
        _quote_cache_instance = QuoteCache()
    return _quote_cache_instance
