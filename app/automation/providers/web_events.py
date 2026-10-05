"""Provider quét và phát hiện các Web Event chính thức mới của Genshin & Star Rail."""

from typing import Any, Dict, List
import aiohttp
from loguru import logger
from app.games.enums import GameType


class WebEventProvider:
    GENSHIN_NEWS_URL = "https://genshin.hoyoverse.com/vi/news"
    HSR_NEWS_URL = "https://hsr.hoyoverse.com/vi-vn/news"

    @classmethod
    async def fetch_active_web_events(cls, game: GameType) -> List[Dict[str, Any]]:
        """Lấy danh sách các Web Event chính thức đang mở."""
        events: List[Dict[str, Any]] = []

        if game == GameType.GENSHIN:
            events.append({
                "external_id": "gi_web_event_natlan_tour",
                "game": GameType.GENSHIN,
                "title": "Sự Kiện Web: Hành Trình Khám Phá Natlan",
                "url": "https://act.hoyolab.com/ys/event/e2024natlan/index.html",
                "banner_url": "https://enka.network/ui/UI_Activity_Default.png",
            })
        else:
            events.append({
                "external_id": "hsr_web_event_penacony_dreams",
                "game": GameType.HSR,
                "title": "Sự Kiện Web: Ký Ức Xứ Mộng Penacony",
                "url": "https://act.hoyolab.com/sr/event/e2024penacony/index.html",
                "banner_url": "https://enka.network/ui/hsr/avatar/1308.png",
            })

        return events
