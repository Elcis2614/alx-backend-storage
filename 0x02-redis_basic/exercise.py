#!/usr/bin/env python3
"""
    Simple class with redis data
"""

import uuid
import redis
from typing import Union
from typing import Any
from typing import Callable
from typing import Optional
from functools import wraps


def replay(method: Callable) -> type(None):
    """
       display the history of calls of a particular function
    """
    cache = method.__self__
    calls = cache.get(method.__qualname__, int)
    fn = method.__qualname__
    print("{} was called {} times:".format(fn, calls))
    inputs = cache._redis.lrange("{}:inputs".format(fn), 0, -1)
    outputs = cache._redis.lrange("{}:outputs".format(fn), 0, -1)
    data = tuple(zip(inputs, outputs))
    for item in data:
        print("{}(*{}) -> {}".format(fn, item[0].decode('utf-8'),
                                     item[1].decode('utf-8')))


def call_history(method: Callable) -> Callable:
    """
        Decorator for stre method
        store the history of inputs and outputs for method
    """
    @wraps(method)
    def wrappeur(self, *args):
        self._redis.rpush("{}:inputs".format(method.__qualname__), str(args))
        output = method(self, *args)
        self._redis.rpush("{}:outputs".format(method.__qualname__), output)
        return output
    return wrappeur


def count_calls(method: Callable) -> Callable:
    """
        Decorator for store method
        Counts the number of times store method is called
    """
    @wraps(method)
    def wrappeur(self, data):
        """
           wrapper function
        """
        self._redis.incr(method.__qualname__)
        return method(self, data)
    return wrappeur


class Cache():
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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
        return int(data, 10)
