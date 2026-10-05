"""Pydantic model cho User & Settings trong DB."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.games.enums import GameType


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    discord_user_id: int
    default_game: GameType = GameType.GENSHIN
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SettingsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    discord_user_id: int
    theme: str = "dark"
    show_uid: bool = False
    use_cards: bool = True
    ephemeral_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
