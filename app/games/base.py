"""Giao diện trừu tượng GameProvider và các ngoại lệ chung cho game."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.games.enums import GameType


class GameException(Exception):
    """Lỗi nền tảng game chung."""
    def __init__(self, message: str = "Đã xảy ra lỗi khi tương tác với game."):
        self.message = message
        super().__init__(self.message)


class PlayerNotFoundError(GameException):
    """Không tìm thấy người chơi hoặc UID không tồn tại."""
    def __init__(self, uid: int, game: GameType):
        super().__init__(f"Không tìm thấy người chơi có UID `{uid}` trên máy chủ {game.display_name}.")


class ProfilePrivateError(GameException):
    """Hồ sơ của người chơi đang ẩn hoặc chưa bật hiển thị chi tiết."""
    def __init__(self, uid: int):
        super().__init__(
            f"Hồ sơ người chơi (UID `{uid}`) đang ở chế độ ẩn hoặc chưa mở hiển thị nhân vật trong game.\n"
            "💡 **Hướng dẫn**: Trong game, vào *Menu Paimon/Điện thoại* -> *Chỉnh sửa thông tin hồ sơ* -> *Bật hiển thị chi tiết nhân vật*."
        )


class GameAPIError(GameException):
    """Lỗi từ API dữ liệu bên ngoài."""
    def __init__(self, message: str = "Máy chủ dữ liệu đang bận hoặc quá tải, vui lòng thử lại sau."):
        super().__init__(message)


class GameRateLimitError(GameException):
    """Bị giới hạn tần suất gọi API."""
    def __init__(self, retry_after: int = 10):
        super().__init__(f"Yêu cầu quá nhanh! Vui lòng đợi {retry_after} giây trước khi tra cứu lại.")


class GameProvider(ABC):
    """Lớp cơ sở trừu tượng mà GenshinProvider và StarRailProvider phải triển khai."""

    @property
    @abstractmethod
    def game_type(self) -> GameType:
        """Loại game tương ứng."""
        pass

    @abstractmethod
    async def get_profile(self, uid: int) -> Any:
        """Lấy thông tin hồ sơ người chơi (Player info & showcase list)."""
        pass

    @abstractmethod
    async def get_characters(self, uid: int) -> List[Any]:
        """Lấy danh sách chi tiết các nhân vật trong tủ trưng bày."""
        pass

    @abstractmethod
    async def get_build(self, character_name_or_id: str) -> Optional[Any]:
        """Lấy hướng dẫn build nhân vật (vũ khí, thánh di vật, chỉ số, đội hình)."""
        pass

    @abstractmethod
    async def search(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Tìm kiếm dữ liệu game (nhân vật, vũ khí, thánh di vật, nguyên liệu)."""
        pass

    @abstractmethod
    async def get_events(self) -> List[Dict[str, Any]]:
        """Lấy danh sách sự kiện hiện tại và sắp diễn ra."""
        pass
