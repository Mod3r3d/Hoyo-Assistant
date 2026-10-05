"""Repository xử lý dữ liệu bảng Accounts."""

from typing import List, Optional
from app.db.database import db
from app.db.models.account import AccountModel
from app.games.enums import GameType, ServerRegion


class AccountRepository:
    @staticmethod
    async def add_account(
        discord_user_id: int,
        game: GameType,
        uid: int,
        server: ServerRegion,
        nickname: Optional[str] = None,
        is_default: bool = False,
    ) -> AccountModel:
        """Thêm tài khoản mới. Nếu là tài khoản đầu tiên của game, tự động đặt làm default."""
        conn = db.conn

        # Kiểm tra xem user đã có tài khoản nào cho game này chưa
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM accounts WHERE discord_user_id = ? AND game = ?",
            (discord_user_id, game.value),
        )
        count = (await cursor.fetchone())[0]
        if count == 0:
            is_default = True

        if is_default:
            # Bỏ cờ default của các tài khoản game này trước
            await conn.execute(
                "UPDATE accounts SET is_default = 0 WHERE discord_user_id = ? AND game = ?",
                (discord_user_id, game.value),
            )

        cursor = await conn.execute(
            """
            INSERT INTO accounts (discord_user_id, game, uid, server, nickname, is_default)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(discord_user_id, game, uid) DO UPDATE SET
                server = excluded.server,
                nickname = COALESCE(excluded.nickname, accounts.nickname),
                is_default = excluded.is_default,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, discord_user_id, game, uid, server, nickname, is_default, created_at, updated_at
            """,
            (discord_user_id, game.value, uid, server.value, nickname, 1 if is_default else 0),
        )
        row = await cursor.fetchone()
        await conn.commit()

        return AccountModel(
            id=row["id"],
            discord_user_id=row["discord_user_id"],
            game=GameType(row["game"]),
            uid=row["uid"],
            server=ServerRegion(row["server"]),
            nickname=row["nickname"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    async def get_by_id(account_id: int) -> Optional[AccountModel]:
        """Lấy tài khoản theo ID."""
        cursor = await db.conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return AccountModel(
            id=row["id"],
            discord_user_id=row["discord_user_id"],
            game=GameType(row["game"]),
            uid=row["uid"],
            server=ServerRegion(row["server"]),
            nickname=row["nickname"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    async def get_accounts_by_user(
        discord_user_id: int, game: Optional[GameType] = None
    ) -> List[AccountModel]:
        """Lấy danh sách tài khoản của người dùng, có thể lọc theo game."""
        conn = db.conn
        if game:
            cursor = await conn.execute(
                "SELECT * FROM accounts WHERE discord_user_id = ? AND game = ? ORDER BY is_default DESC, id ASC",
                (discord_user_id, game.value),
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM accounts WHERE discord_user_id = ? ORDER BY game ASC, is_default DESC, id ASC",
                (discord_user_id,),
            )
        rows = await cursor.fetchall()
        return [
            AccountModel(
                id=r["id"],
                discord_user_id=r["discord_user_id"],
                game=GameType(r["game"]),
                uid=r["uid"],
                server=ServerRegion(r["server"]),
                nickname=r["nickname"],
                is_default=bool(r["is_default"]),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]

    @staticmethod
    async def get_default_account(
        discord_user_id: int, game: Optional[GameType] = None
    ) -> Optional[AccountModel]:
        """Lấy tài khoản mặc định của người dùng cho game cụ thể."""
        conn = db.conn
        if game:
            cursor = await conn.execute(
                "SELECT * FROM accounts WHERE discord_user_id = ? AND game = ? ORDER BY is_default DESC, id ASC LIMIT 1",
                (discord_user_id, game.value),
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM accounts WHERE discord_user_id = ? ORDER BY is_default DESC, id ASC LIMIT 1",
                (discord_user_id,),
            )
        row = await cursor.fetchone()
        if not row:
            return None
        return AccountModel(
            id=row["id"],
            discord_user_id=row["discord_user_id"],
            game=GameType(row["game"]),
            uid=row["uid"],
            server=ServerRegion(row["server"]),
            nickname=row["nickname"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    async def set_default(discord_user_id: int, account_id: int) -> bool:
        """Đặt một tài khoản làm mặc định cho tựa game tương ứng."""
        conn = db.conn
        acc = await AccountRepository.get_by_id(account_id)
        if not acc or acc.discord_user_id != discord_user_id:
            return False

        # Reset các account cùng game
        await conn.execute(
            "UPDATE accounts SET is_default = 0 WHERE discord_user_id = ? AND game = ?",
            (discord_user_id, acc.game.value),
        )
        # Set account này làm default
        await conn.execute(
            "UPDATE accounts SET is_default = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (account_id,),
        )
        await conn.commit()
        return True

    @staticmethod
    async def delete_account(discord_user_id: int, account_id: int) -> bool:
        """Xóa tài khoản đã liên kết."""
        conn = db.conn
        acc = await AccountRepository.get_by_id(account_id)
        if not acc or acc.discord_user_id != discord_user_id:
            return False

        await conn.execute(
            "DELETE FROM accounts WHERE id = ? AND discord_user_id = ?",
            (account_id, discord_user_id),
        )

        # Nếu xóa account default, hãy chọn account khác cùng game làm default (nếu còn)
        if acc.is_default:
            await conn.execute(
                """
                UPDATE accounts SET is_default = 1
                WHERE id = (SELECT id FROM accounts WHERE discord_user_id = ? AND game = ? LIMIT 1)
                """,
                (discord_user_id, acc.game.value),
            )

        await conn.commit()
        return True
