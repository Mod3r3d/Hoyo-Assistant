"""Dịch vụ tra cứu hồ sơ người chơi (ProfileService) và Nhân vật (CharacterService)."""

from typing import Any, List, Optional
from app.db.models.account import AccountModel
from app.games.enums import GameType
from app.games.factory import provider_factory


class ProfileService:
    @staticmethod
    async def get_profile(game: GameType, uid: int) -> Any:
        """Lấy hồ sơ người chơi thông qua GameProvider."""
        provider = provider_factory.get_provider(game)
        return await provider.get_profile(uid)

    @staticmethod
    async def get_profile_by_account(account: AccountModel) -> Any:
        """Lấy hồ sơ dựa trên tài khoản đã lưu."""
        return await ProfileService.get_profile(account.game, account.uid)


class CharacterService:
    @staticmethod
    async def get_showcase_characters(game: GameType, uid: int) -> List[Any]:
        """Lấy danh sách nhân vật chi tiết trong showcase."""
        provider = provider_factory.get_provider(game)
        return await provider.get_characters(uid)

    @staticmethod
    async def get_characters_by_account(account: AccountModel) -> List[Any]:
        return await CharacterService.get_showcase_characters(account.game, account.uid)


profile_service = ProfileService()
character_service = CharacterService()
