"""Caching utilities for improved performance in BI Documentation Tool."""

import functools
import hashlib
import json
import logging
import pickle
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union

F = TypeVar('F', bound=Callable[..., Any])


class MemoryCache:
    """In-memory cache with TTL (Time To Live) support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """Initialize memory cache.
        
        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry['expires_at']
    
    def _evict_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.cache.items() 
            if current_time > v['expires_at']
        ]
        for key in expired_keys:
            del self.cache[key]
            self.logger.debug(f"Evicted expired cache entry: {key}")
    
    def _evict_lru(self) -> None:
        """Evict least recently used items if cache is full."""
        if len(self.cache) >= self.max_size:
            # Sort by access time and remove oldest
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]['accessed_at']
            )
            del self.cache[lru_key]
            self.logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        self._evict_expired()
        
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry):
                entry['accessed_at'] = time.time()
                self.logger.debug(f"Cache hit: {key}")
                return entry['value']
            else:
                del self.cache[key]
                self.logger.debug(f"Cache miss (expired): {key}")
        else:
            self.logger.debug(f"Cache miss: {key}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        self._evict_expired()
        self._evict_lru()
        
        ttl = ttl or self.default_ttl
        current_time = time.time()
        
        self.cache[key] = {
            'value': value,
            'created_at': current_time,
            'accessed_at': current_time,
            'expires_at': current_time + ttl
        }
        
        self.logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.logger.debug("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size,
        }


class FileCache:
    """File-based cache for persistent storage."""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_age: int = 86400):
        """Initialize file cache.
        
        Args:
            cache_dir: Directory for cache files (defaults to temp dir)
            max_age: Maximum age of cache files in seconds (24 hours)
        """
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "bidoc_cache"
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age = max_age
        self.logger = logging.getLogger(__name__)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _is_expired(self, cache_path: Path) -> bool:
        """Check if cache file is expired."""
        if not cache_path.exists():
            return True
        
        age = time.time() - cache_path.stat().st_mtime
        return age > self.max_age
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        cache_path = self._get_cache_path(key)
        
        if self._is_expired(cache_path):
            if cache_path.exists():
                cache_path.unlink()
                self.logger.debug(f"Removed expired cache file: {key}")
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            self.logger.debug(f"File cache hit: {key}")
            return value
        except (FileNotFoundError, pickle.UnpicklingError, EOFError) as e:
            self.logger.debug(f"File cache miss: {key} ({e})")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in file cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            self.logger.debug(f"File cache set: {key}")
        except Exception as e:
            self.logger.error(f"Failed to cache {key}: {e}")
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        self.logger.debug("File cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired cache files and return count."""
        removed = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            if self._is_expired(cache_file):
                cache_file.unlink()
                removed += 1
        
        if removed > 0:
            self.logger.debug(f"Cleaned up {removed} expired cache files")
        
        return removed


# Global cache instances
_memory_cache: Optional[MemoryCache] = None
_file_cache: Optional[FileCache] = None


def get_memory_cache() -> MemoryCache:
    """Get or create global memory cache."""
    global _memory_cache
    if _memory_cache is None:
        _memory_cache = MemoryCache()
    return _memory_cache


def get_file_cache() -> FileCache:
    """Get or create global file cache."""
    global _file_cache
    if _file_cache is None:
        _file_cache = FileCache()
    return _file_cache


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    # Create deterministic key from arguments
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def memory_cached(ttl: int = 3600) -> Callable[[F], F]:
    """Decorator for in-memory caching with TTL.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_memory_cache()
            
            # Generate cache key
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


def file_cached(max_age: int = 86400) -> Callable[[F], F]:
    """Decorator for file-based caching.
    
    Args:
        max_age: Maximum age in seconds
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_file_cache()
            cache.max_age = max_age
            
            # Generate cache key
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


def hybrid_cached(memory_ttl: int = 3600, file_max_age: int = 86400) -> Callable[[F], F]:
    """Decorator for hybrid memory + file caching.
    
    Args:
        memory_ttl: Memory cache TTL in seconds
        file_max_age: File cache max age in seconds
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            memory_cache = get_memory_cache()
            file_cache = get_file_cache()
            file_cache.max_age = file_max_age
            
            # Generate cache key
            key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try memory cache first
            result = memory_cache.get(key)
            if result is not None:
                return result
            
            # Try file cache
            result = file_cache.get(key)
            if result is not None:
                # Promote to memory cache
                memory_cache.set(key, result, memory_ttl)
                return result
            
            # Execute function and cache in both
            result = func(*args, **kwargs)
            memory_cache.set(key, result, memory_ttl)
            file_cache.set(key, result)
            return result
        
        return wrapper
    return decorator


def clear_all_caches() -> None:
    """Clear all caches (memory and file)."""
    get_memory_cache().clear()
    get_file_cache().clear()


def cleanup_caches() -> Dict[str, int]:
    """Clean up expired cache entries and return statistics."""
    memory_cache = get_memory_cache()
    file_cache = get_file_cache()
    
    # Memory cache cleanup happens automatically
    memory_cache._evict_expired()
    
    # File cache cleanup
    expired_files = file_cache.cleanup_expired()
    
    return {
        'memory_size': len(memory_cache.cache),
        'expired_files_removed': expired_files,
    }