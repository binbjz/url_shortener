import time
from functools import wraps
from collections.abc import Callable
from typing import TypeVar, ParamSpec
from pymongo.errors import ServerSelectionTimeoutError

P = ParamSpec("P")
R = TypeVar("R")


def retry(retry_count: int = 3, wait_seconds: int = 2):
    def decorator(func: Callable[P, R]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal retry_count
            attempts = 0
            while attempts < retry_count:
                try:
                    return func(*args, **kwargs)
                except ServerSelectionTimeoutError as e:
                    print(f"Attempt {attempts + 1} failed with error: {e}")
                    time.sleep(wait_seconds)
                    attempts += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator
