"""Repository xử lý User và Settings."""

from typing import Optional
from app.db.database import db
from app.db.models.user import UserModel, SettingsModel
from app.games.enums import GameType


class UserRepository:
    @staticmethod
    async def get_or_create(discord_user_id: int) -> UserModel:
        """Lấy hoặc tạo mới bản ghi người dùng."""
        conn = db.conn
        cursor = await conn.execute(
            "SELECT * FROM users WHERE discord_user_id = ?",
            (discord_user_id,),
        )
        row = await cursor.fetchone()
        if row:
            return UserModel(
                id=row["id"],
                discord_user_id=row["discord_user_id"],
                default_game=GameType(row["default_game"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        cursor = await conn.execute(
            """
            INSERT INTO users (discord_user_id, default_game)
            VALUES (?, ?)
            RETURNING id, discord_user_id, default_game, created_at, updated_at
            """,
            (discord_user_id, GameType.GENSHIN.value),
        )
        row = await cursor.fetchone()
        await conn.commit()
        return UserModel(
            id=row["id"],
            discord_user_id=row["discord_user_id"],
            default_game=GameType(row["default_game"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    async def set_default_game(discord_user_id: int, game: GameType) -> bool:
        """Thiết lập game mặc định khi tra cứu."""
        conn = db.conn
        await UserRepository.get_or_create(discord_user_id)
        await conn.execute(
            "UPDATE users SET default_game = ?, updated_at = CURRENT_TIMESTAMP WHERE discord_user_id = ?",
            (game.value, discord_user_id),
        )
        await conn.commit()
        return True


class SettingsRepository:
    @staticmethod
    async def get_settings(discord_user_id: int) -> SettingsModel:
        """Lấy cấu hình cá nhân của người dùng hoặc tạo mặc định."""
        conn = db.conn
        cursor = await conn.execute(
            "SELECT * FROM settings WHERE discord_user_id = ?",
            (discord_user_id,),
        )
        row = await cursor.fetchone()
        if row:
            return SettingsModel(
                discord_user_id=row["discord_user_id"],
                theme=row["theme"],
                show_uid=bool(row["show_uid"]),
                use_cards=bool(row["use_cards"]),
                ephemeral_default=bool(row["ephemeral_default"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

        # Tạo mới mặc định
        cursor = await conn.execute(
            """
            INSERT INTO settings (discord_user_id, theme, show_uid, use_cards, ephemeral_default)
            VALUES (?, 'dark', 0, 1, 0)
            RETURNING discord_user_id, theme, show_uid, use_cards, ephemeral_default, created_at, updated_at
            """,
            (discord_user_id,),
        )
        row = await cursor.fetchone()
        await conn.commit()
        return SettingsModel(
            discord_user_id=row["discord_user_id"],
            theme=row["theme"],
            show_uid=bool(row["show_uid"]),
            use_cards=bool(row["use_cards"]),
            ephemeral_default=bool(row["ephemeral_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    async def update_settings(
        discord_user_id: int,
        theme: Optional[str] = None,
        show_uid: Optional[bool] = None,
        use_cards: Optional[bool] = None,
        ephemeral_default: Optional[bool] = None,
    ) -> SettingsModel:
        """Cập nhật cài đặt của user."""
        current = await SettingsRepository.get_settings(discord_user_id)
        new_theme = theme if theme is not None else current.theme
        new_show_uid = show_uid if show_uid is not None else current.show_uid
        new_use_cards = use_cards if use_cards is not None else current.use_cards
        new_ephemeral = ephemeral_default if ephemeral_default is not None else current.ephemeral_default

        conn = db.conn
        cursor = await conn.execute(
            """
            UPDATE settings
            SET theme = ?, show_uid = ?, use_cards = ?, ephemeral_default = ?, updated_at = CURRENT_TIMESTAMP
            WHERE discord_user_id = ?
            RETURNING discord_user_id, theme, show_uid, use_cards, ephemeral_default, created_at, updated_at
            """,
            (new_theme, 1 if new_show_uid else 0, 1 if new_use_cards else 0, 1 if new_ephemeral else 0, discord_user_id),
        )
        row = await cursor.fetchone()
        await conn.commit()
        return SettingsModel(
            discord_user_id=row["discord_user_id"],
            theme=row["theme"],
            show_uid=bool(row["show_uid"]),
            use_cards=bool(row["use_cards"]),
            ephemeral_default=bool(row["ephemeral_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
