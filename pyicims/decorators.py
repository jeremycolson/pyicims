# mypy: ignore-errors
"""Custom decorators."""
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Callable


def timed_lru_cache(seconds: int, maxsize: int = 128):
    """Decorator that adds a time limit to the LRU cache.

    Args:
        - seconds (int): number of seconds before triggering refresh, defaults to 128.
        - maxsize (int): max number of records the cache will store.

    Notes:
        - If maxsize is set to None, the LRU will be diisabled.

    Returns:
        Callable: wrapped function
    """

    def wrapper_cache(func) -> Callable:
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
