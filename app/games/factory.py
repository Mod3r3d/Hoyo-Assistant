"""Factory khởi tạo GameProvider tương ứng với từng trò chơi."""

from typing import Dict
from app.games.base import GameProvider
from app.games.enums import GameType
from app.games.genshin.provider import GenshinProvider
from app.games.hsr.provider import StarRailProvider


class ProviderFactory:
    def __init__(self):
        self._providers: Dict[GameType, GameProvider] = {
            GameType.GENSHIN: GenshinProvider(),
            GameType.HSR: StarRailProvider(),
        }

    def get_provider(self, game: GameType) -> GameProvider:
        """Lấy provider phù hợp với game."""
        provider = self._providers.get(game)
        if not provider:
            raise ValueError(f"Không tìm thấy provider cho tựa game: {game}")
        return provider


# Singleton factory
provider_factory = ProviderFactory()
