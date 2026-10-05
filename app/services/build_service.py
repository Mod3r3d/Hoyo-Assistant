"""Dịch vụ hướng dẫn build (BuildService), tìm kiếm (SearchService), sự kiện (EventService), và cài đặt (SettingsService)."""

from typing import Any, Dict, List, Optional
from app.db.models.user import SettingsModel
from app.db.repositories.settings import SettingsRepository
from app.games.enums import GameType
from app.games.factory import provider_factory


class BuildService:
    @staticmethod
    async def get_build(game: GameType, character_name: str) -> Optional[Any]:
        """Lấy hướng dẫn build nhân vật theo game."""
        provider = provider_factory.get_provider(game)
        return await provider.get_build(character_name)


class SearchService:
    @staticmethod
    async def search(game: GameType, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Tìm kiếm dữ liệu game."""
        provider = provider_factory.get_provider(game)
        return await provider.search(query, category)


class EventService:
    @staticmethod
    async def get_events(game: GameType) -> List[Dict[str, Any]]:
        """Lấy danh sách sự kiện hiện tại."""
        provider = provider_factory.get_provider(game)
        return await provider.get_events()


class SettingsService:
    @staticmethod
    async def get_settings(discord_user_id: int) -> SettingsModel:
        return await SettingsRepository.get_settings(discord_user_id)

    @staticmethod
    async def update_settings(
        discord_user_id: int,
        theme: Optional[str] = None,
        show_uid: Optional[bool] = None,
        use_cards: Optional[bool] = None,
        ephemeral_default: Optional[bool] = None,
    ) -> SettingsModel:
        return await SettingsRepository.update_settings(
            discord_user_id=discord_user_id,
            theme=theme,
            show_uid=show_uid,
            use_cards=use_cards,
            ephemeral_default=ephemeral_default,
        )


build_service = BuildService()
search_service = SearchService()
event_service = EventService()
settings_service = SettingsService()
