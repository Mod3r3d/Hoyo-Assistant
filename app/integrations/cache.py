"""Bộ nhớ đệm In-Memory TTL Cache cho dữ liệu API và static data."""

import asyncio
import time
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        # key -> (value, expire_timestamp)
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Lấy giá trị từ cache nếu chưa hết hạn."""
        async with self._lock:
            item = self._cache.get(key)
            if not item:
                return None
            val, expire_time = item
            if time.time() > expire_time:
                del self._cache[key]
                return None
            return val

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Lưu giá trị vào cache với TTL tương ứng."""
        duration = ttl if ttl is not None else self.default_ttl
        expire_time = time.time() + duration
        async with self._lock:
            self._cache[key] = (value, expire_time)

    async def delete(self, key: str):
        """Xóa một key khỏi cache."""
        async with self._lock:
            self._cache.pop(key, None)

    async def clear(self):
        """Xóa toàn bộ cache."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self):
        """Dọn dẹp các mục đã hết hạn."""
        now = time.time()
        async with self._lock:
            expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
            for k in expired_keys:
                del self._cache[k]


# Global cache instance
global_cache = TTLCache(default_ttl=3600)
