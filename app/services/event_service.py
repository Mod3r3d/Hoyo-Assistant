"""Dịch vụ theo dõi sự kiện game."""

from typing import Any, Dict, List
from app.games.enums import GameType
from app.games.factory import provider_factory


class EventService:
    @staticmethod
    async def get_events(game: GameType) -> List[Dict[str, Any]]:
        provider = provider_factory.get_provider(game)
        return await provider.get_events()


event_service = EventService()
