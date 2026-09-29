"""Utility module for advanced routing in the CMTIP bus.

This module provides a minimal yet extensible framework for
- tracking routing metrics (latency, hop count, relay fee)
- caching frequently used target addresses to reduce lookup time
- a decorator that logs routing calls for audit purposes.

All functions are intentionally lightweight to keep the
context window small – the broker can import this file without
excessive token cost.
"""

from __future__ import annotations

import time
from typing import Callable, Any

# Simple in‑memory cache for target embeddings; in a real deployment this
# would be backed by a persistent store.
_target_cache: dict[str, Any] = {}


def _log(message: str) -> None:
    """Internal log helper – replace with real logger when available."""
    print(f"[route_utils] {time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def route_decorator(func: Callable) -> Callable:
    """Decorator that logs entry/exit and measures latency.

    Usage:
        @route_decorator
        def route_tensor(...):
            ...
    """
    def wrapper(*args, **kwargs):  # type: ignore
        start = time.time()
        _log(f"Starting route call: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start
            _log(f"Finished {func.__name__} in {elapsed:.6f}s")
    return wrapper


@route_decorator
def cache_target(target_id: str, embedding: Any) -> None:
    """Cache a target embedding for quick lookup.

    Parameters
    ----------
    target_id: str
        Unique identifier for the target (e.g. cluster id or agent id).
    embedding: Any
        The embedding signature to store.
    """
    _target_cache[target_id] = embedding
    _log(f"Cached target {target_id}")


@route_decorator
def get_cached_target(target_id: str) -> Any | None:
    """Retrieve a cached target embedding.

    Returns ``None`` if the target is not cached.
    """
    embedding = _target_cache.get(target_id)
    _log(f"Lookup for {target_id}: {'HIT' if embedding else 'MISS'}")
    return embedding


__all__ = [
    "route_decorator",
    "cache_target",
    "get_cached_target",
]
