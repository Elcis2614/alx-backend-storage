#!/usr/bin/env python3
"""
    Simple class with redis data
"""

import uuid
import redis


class Cache():
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: any) -> str:
        """
            sets data to the redis instance
            with a unique key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
