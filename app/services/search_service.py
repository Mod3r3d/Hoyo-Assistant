"""Dịch vụ tìm kiếm bách khoa game."""

from typing import Any, Dict, List
from app.games.enums import GameType
from app.games.factory import provider_factory


class SearchService:
    @staticmethod
    async def search(game: GameType, query: str, category: str = "all") -> List[Dict[str, Any]]:
        provider = provider_factory.get_provider(game)
        return await provider.search(query, category)


search_service = SearchService()
