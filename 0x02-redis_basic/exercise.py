#!/usr/bin/env python3
"""
    Simple class with redis data
"""

import uuid
import redis
from typing import Union
from typing import Callable
from typing import Optional
from functools import wraps


def count_calls(method: Callable[[Union[str, bytes, int, float]], str]) -> Callable[[Union[str, bytes, int, float]], str]:
    """
        Decorator for store method
    """
    @wraps(method)
    def wrappeur(self, data):
        """
           wrapper
        """
        self._redis.incr(method.__qualname__)
        return method(self, data)
    return wrappeur


class Cache():
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
            sets data to the redis instance
            with a unique key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable[[any], any]] = None) -> any:
        """
            key : string argument
            Callable argument named fn.
            This callable will be used to convert the data back to the desired
            format.
        """
        data = self._redis.get(key)
        if (fn == int):
            return self.get_int(data)
        elif (fn == str):
            return self.get_str(data)
        elif (fn is None):
            return data
        return fn(data)

    def get_str(self, data: bytes) -> str:
        """
            convert binary to string
        """
        return data.decode('utf-8')

    def get_int(self, data: bytes) -> int:
        """
           converts binary to integer
        """
        return int(data, 2)
