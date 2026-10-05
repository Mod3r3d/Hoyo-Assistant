"""Cơ chế Rate Limit đơn giản cho người dùng gọi command bot."""

import time
from typing import Dict, Tuple


class UserRateLimiter:
    """Giới hạn tần suất gọi API bên ngoài để tránh bị block IP hoặc Discord rate limit."""

    def __init__(self, default_cooldown_seconds: float = 3.0):
        self.default_cooldown = default_cooldown_seconds
        # user_id -> (last_timestamp, count)
        self._user_timestamps: Dict[int, float] = {}

    def is_rate_limited(self, user_id: int, custom_cooldown: float = 0.0) -> Tuple[bool, float]:
        """
        Kiểm tra user có đang bị rate limit không.
        Trả về (bị_chặn, số_giây_còn_lại).
        """
        cooldown = custom_cooldown if custom_cooldown > 0 else self.default_cooldown
        now = time.time()
        last_time = self._user_timestamps.get(user_id, 0.0)

        elapsed = now - last_time
        if elapsed < cooldown:
            return True, cooldown - elapsed

        self._user_timestamps[user_id] = now
        return False, 0.0

    def reset(self, user_id: int):
        self._user_timestamps.pop(user_id, None)


# Singleton instance
global_rate_limiter = UserRateLimiter(default_cooldown_seconds=3.0)
