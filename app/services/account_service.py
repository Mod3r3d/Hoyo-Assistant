"""Dịch vụ quản lý tài khoản game (Genshin & HSR)."""

from typing import List, Optional, Tuple
from app.db.models.account import AccountModel
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.users import UserRepository
from app.games.enums import GameType, ServerRegion
from app.utils.validators import validate_uid


class AccountService:
    @staticmethod
    async def add_account(
        discord_user_id: int,
        game: GameType,
        uid: int,
        nickname: Optional[str] = None,
        is_default: bool = False,
    ) -> Tuple[Optional[AccountModel], Optional[str]]:
        """
        Thêm tài khoản game mới cho người dùng Discord.
        Kiểm tra tính hợp lệ của UID và xác định server.
        """
        # Xác thực người dùng trong DB
        await UserRepository.get_or_create(discord_user_id)

        # Kiểm tra UID hợp lệ
        is_valid, err_msg, server = validate_uid(uid, game)
        if not is_valid or not server:
            return None, err_msg or "UID không hợp lệ."

        account = await AccountRepository.add_account(
            discord_user_id=discord_user_id,
            game=game,
            uid=uid,
            server=server,
            nickname=nickname,
            is_default=is_default,
        )
        return account, None

    @staticmethod
    async def get_user_accounts(
        discord_user_id: int, game: Optional[GameType] = None
    ) -> List[AccountModel]:
        """Lấy tất cả tài khoản của người dùng."""
        return await AccountRepository.get_accounts_by_user(discord_user_id, game)

    @staticmethod
    async def get_default_or_first_account(
        discord_user_id: int, game: GameType
    ) -> Optional[AccountModel]:
        """Lấy tài khoản mặc định của game hoặc tài khoản đầu tiên."""
        return await AccountRepository.get_default_account(discord_user_id, game)

    @staticmethod
    async def set_default_account(discord_user_id: int, account_id: int) -> bool:
        """Đặt tài khoản làm mặc định."""
        return await AccountRepository.set_default(discord_user_id, account_id)

    @staticmethod
    async def remove_account(discord_user_id: int, account_id: int) -> bool:
        """Xóa tài khoản đã lưu."""
        return await AccountRepository.delete_account(discord_user_id, account_id)

    @staticmethod
    async def get_account_by_id(account_id: int) -> Optional[AccountModel]:
        """Lấy thông tin tài khoản theo ID."""
        return await AccountRepository.get_by_id(account_id)


account_service = AccountService()
