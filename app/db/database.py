"""Khởi tạo và quản lý kết nối SQLite bất đồng bộ (aiosqlite) với hỗ trợ Automation v2."""

import os
from pathlib import Path
import aiosqlite
from loguru import logger
from app.config import settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER UNIQUE NOT NULL,
    default_game TEXT NOT NULL DEFAULT 'genshin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    uid INTEGER NOT NULL,
    server TEXT NOT NULL,
    nickname TEXT,
    is_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discord_user_id, game, uid)
);

CREATE TABLE IF NOT EXISTS settings (
    discord_user_id INTEGER PRIMARY KEY,
    theme TEXT NOT NULL DEFAULT 'dark',
    show_uid BOOLEAN NOT NULL DEFAULT 0,
    use_cards BOOLEAN NOT NULL DEFAULT 1,
    ephemeral_default BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lưu trữ Session & Cookie đã mã hóa cho Automation
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    uid INTEGER NOT NULL,
    cookie_encrypted TEXT NOT NULL,
    session_status TEXT NOT NULL DEFAULT 'VALID',
    last_auth_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discord_user_id, game, uid)
);

-- Cài đặt bật/tắt từng tính năng Automation cho từng Account
CREATE TABLE IF NOT EXISTS automation_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER UNIQUE NOT NULL,
    discord_user_id INTEGER NOT NULL,
    automation_enabled BOOLEAN NOT NULL DEFAULT 1,
    checkin_enabled BOOLEAN NOT NULL DEFAULT 1,
    redeem_enabled BOOLEAN NOT NULL DEFAULT 1,
    mimo_enabled BOOLEAN NOT NULL DEFAULT 1,
    accompany_enabled BOOLEAN NOT NULL DEFAULT 0,
    event_notify_enabled BOOLEAN NOT NULL DEFAULT 1,
    notify_mode TEXT NOT NULL DEFAULT 'FAILURE_ONLY',
    notify_channel_id INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lịch sử điểm danh hàng ngày
CREATE TABLE IF NOT EXISTS checkin_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    run_date TEXT NOT NULL,
    status TEXT NOT NULL,
    reward_summary TEXT DEFAULT NULL,
    error_code TEXT DEFAULT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, run_date)
);

-- Bảng mã Giftcode phát hiện được
CREATE TABLE IF NOT EXISTS gift_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    game TEXT NOT NULL,
    source TEXT NOT NULL,
    sources TEXT DEFAULT NULL,
    rewards TEXT DEFAULT NULL,
    confidence TEXT DEFAULT 'MEDIUM',
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NULL,
    last_checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    UNIQUE(game, code)
);

-- Lịch sử đổi Giftcode của từng account
CREATE TABLE IF NOT EXISTS giftcode_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    gift_code_id INTEGER NOT NULL,
    game TEXT NOT NULL,
    code TEXT NOT NULL,
    status TEXT NOT NULL,
    response_msg TEXT DEFAULT NULL,
    redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, gift_code_id)
);

-- Nhiệm vụ Mimo / Accompany
CREATE TABLE IF NOT EXISTS automation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    external_task_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL,
    reward TEXT DEFAULT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP DEFAULT NULL,
    last_error TEXT DEFAULT NULL,
    UNIQUE(account_id, provider, external_task_id)
);

-- Sự kiện Web mới phát hiện
CREATE TABLE IF NOT EXISTS web_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    game TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    banner_url TEXT DEFAULT NULL,
    start_at TIMESTAMP DEFAULT NULL,
    end_at TIMESTAMP DEFAULT NULL,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game, external_id)
);

-- Nhật ký thực thi nhiệm vụ chạy nền
CREATE TABLE IF NOT EXISTS automation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    game TEXT DEFAULT NULL,
    account_id INTEGER DEFAULT NULL,
    status TEXT NOT NULL,
    duration_ms INTEGER DEFAULT 0,
    message TEXT DEFAULT NULL,
    error_detail TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_accounts_user_game ON accounts(discord_user_id, game);
CREATE INDEX IF NOT EXISTS idx_sessions_user_game ON sessions(discord_user_id, game);
CREATE INDEX IF NOT EXISTS idx_checkin_account_date ON checkin_executions(account_id, run_date);
CREATE INDEX IF NOT EXISTS idx_giftcodes_active ON gift_codes(game, status);
CREATE INDEX IF NOT EXISTS idx_auto_logs_task ON automation_logs(task_name, status);
"""


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self):
        """Khởi tạo kết nối và bảng dữ liệu."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(str(self.db_path))
        self._connection.row_factory = aiosqlite.Row
        await self._connection.executescript(SCHEMA_SQL)

        # Migration an toàn cho các cột mới của bảng gift_codes
        for col_def in [
            "ALTER TABLE gift_codes ADD COLUMN sources TEXT DEFAULT NULL",
            "ALTER TABLE gift_codes ADD COLUMN rewards TEXT DEFAULT NULL",
            "ALTER TABLE gift_codes ADD COLUMN confidence TEXT DEFAULT 'MEDIUM'",
        ]:
            try:
                await self._connection.execute(col_def)
            except Exception:
                pass

        await self._connection.commit()
        logger.info(f"Đã kết nối cơ sở dữ liệu SQLite tại {self.db_path}")

    async def close(self):
        """Đóng kết nối cơ sở dữ liệu."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Đã đóng kết nối cơ sở dữ liệu.")

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Database chưa được kết nối! Hãy gọi await db.connect() trước.")
        return self._connection


db = Database(settings.db_file_path)
