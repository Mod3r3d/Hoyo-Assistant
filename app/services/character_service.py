"""Dịch vụ tra cứu chi tiết nhân vật (CharacterService)."""

from typing import Any, List
from app.db.models.account import AccountModel
from app.games.enums import GameType
from app.games.factory import provider_factory


class CharacterService:
    @staticmethod
    async def get_showcase_characters(game: GameType, uid: int) -> List[Any]:
        """Lấy danh sách nhân vật chi tiết trong showcase."""
        provider = provider_factory.get_provider(game)
        return await provider.get_characters(uid)

    @staticmethod
    async def get_characters_by_account(account: AccountModel) -> List[Any]:
        return await CharacterService.get_showcase_characters(account.game, account.uid)


character_service = CharacterService()
