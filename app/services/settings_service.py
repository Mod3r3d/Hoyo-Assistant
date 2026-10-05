"""Dịch vụ quản lý cài đặt cá nhân."""

from typing import Optional
from app.db.models.user import SettingsModel
from app.db.repositories.settings import SettingsRepository


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


settings_service = SettingsService()
