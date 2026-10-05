"""Client giao tiếp với Enka.Network API cho Genshin Impact và Honkai: Star Rail."""

import asyncio
from typing import Any, Dict, Optional
import aiohttp
from loguru import logger
from app.config import settings
from app.games.base import (
    GameAPIError,
    GameRateLimitError,
    PlayerNotFoundError,
    ProfilePrivateError,
)
from app.games.enums import GameType
from app.integrations.cache import global_cache


class EnkaClient:
    GENSHIN_BASE_URL = "https://enka.network/api/uid"
    HSR_BASE_URL = "https://enka.network/api/hsr/uid"

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "User-Agent": "HoyoBot-Discord/1.0.0 (Public Hoyo Discord Assistant)",
            "Accept": "application/json",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.ENKA_TIMEOUT_SECONDS)
            self._session = aiohttp.ClientSession(
                headers=self._headers, timeout=timeout
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def fetch_genshin(self, uid: int, use_cache: bool = True) -> Dict[str, Any]:
        """Lấy dữ liệu người chơi Genshin Impact qua Enka.Network."""
        cache_key = f"enka:genshin:{uid}"
        if use_cache:
            cached = await global_cache.get(cache_key)
            if cached:
                logger.debug(f"[Cache Hit] Genshin Enka UID {uid}")
                return cached

        url = f"{self.GENSHIN_BASE_URL}/{uid}"
        data = await self._request(url, uid, GameType.GENSHIN)

        # Cache kết quả trong 10 phút (600 giây) để tối ưu và tuân thủ rate limit
        await global_cache.set(cache_key, data, ttl=600)
        return data

    async def fetch_hsr(self, uid: int, use_cache: bool = True) -> Dict[str, Any]:
        """Lấy dữ liệu người chơi Honkai: Star Rail qua Enka.Network."""
        cache_key = f"enka:hsr:{uid}"
        if use_cache:
            cached = await global_cache.get(cache_key)
            if cached:
                logger.debug(f"[Cache Hit] HSR Enka UID {uid}")
                return cached

        url = f"{self.HSR_BASE_URL}/{uid}"
        data = await self._request(url, uid, GameType.HSR)

        await global_cache.set(cache_key, data, ttl=600)
        return data

    async def _request(self, url: str, uid: int, game: GameType) -> Dict[str, Any]:
        session = await self.get_session()
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Kiểm tra dữ liệu rỗng
                    if not data:
                        raise PlayerNotFoundError(uid, game)
                    return data

                elif resp.status == 400:
                    raise GameAPIError(f"Định dạng UID `{uid}` không hợp lệ đối với hệ thống.")

                elif resp.status == 404:
                    raise PlayerNotFoundError(uid, game)

                elif resp.status == 424:
                    raise GameAPIError("Hệ thống game hoặc Enka đang trong quá trình bảo trì. Vui lòng thử lại sau.")

                elif resp.status == 429:
                    raise GameRateLimitError(retry_after=15)

                elif resp.status in (500, 502, 503, 504):
                    raise GameAPIError("Máy chủ dữ liệu Enka Network phản hồi chậm hoặc tạm thời mất kết nối.")

                else:
                    text = await resp.text()
                    logger.warning(f"Enka API returned status {resp.status} for {url}: {text[:200]}")
                    raise GameAPIError(f"Không thể lấy dữ liệu (Mã phản hồi: {resp.status}).")

        except asyncio.TimeoutError:
            raise GameAPIError("Yêu cầu lấy dữ liệu quá thời gian chờ (Timeout). Vui lòng thử lại sau giây lát.")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while requesting {url}: {e}")
            raise GameAPIError("Không thể kết nối đến máy chủ dữ liệu bên ngoài. Vui lòng kiểm tra lại kết nối.")


# Singleton enka client
enka_client = EnkaClient()
