"""Pydantic model cho Account trong DB."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.games.enums import GameType, ServerRegion


class AccountModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    discord_user_id: int
    game: GameType
    uid: int
    server: ServerRegion
    nickname: Optional[str] = None
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def display_label(self) -> str:
        """Nhãn hiển thị trực quan trong Select Menu."""
        name = self.nickname or f"UID {self.uid}"
        default_tag = " [Mặc định]" if self.is_default else ""
        return f"{self.game.short_name} - {name} ({self.uid} - {self.server.value}){default_tag}"
