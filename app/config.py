"""Cấu hình ứng dụng HoyoBot (bao gồm lớp Automation v2)."""

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Discord Bot Token
    DISCORD_TOKEN: str = ""

    # Database
    DATABASE_PATH: str = "data/hoyobot.db"

    # Debug & Logging
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Cache & timeouts
    CACHE_TTL_SECONDS: int = 3600
    ENKA_TIMEOUT_SECONDS: int = 12

    # Automation v2 Core Settings
    AUTOMATION_ENABLED: bool = True
    AUTOMATION_MODE: str = "live"  # 'live' hoặc 'dry-run'
    ENCRYPTION_KEY: Optional[str] = None
    TIMEZONE: str = "Asia/Ho_Chi_Minh"

    # Scheduler Intervals
    CHECKIN_CRON_HOUR: int = 0
    CHECKIN_CRON_MINUTE: int = 5
    GIFTCODE_SCAN_INTERVAL_MINUTES: int = 60
    MIMO_SCAN_INTERVAL_MINUTES: int = 60
    WEB_EVENT_SCAN_INTERVAL_MINUTES: int = 120

    # Rate Limiting & Concurrency
    MAX_CONCURRENT_AUTOMATION_TASKS: int = 5
    PROVIDER_REQUEST_DELAY_SECONDS: float = 1.5

    # Admin Discord User IDs (danh sách ID cách nhau bởi dấu phẩy, ví dụ: "12345678,87654321")
    ADMIN_USER_IDS: str = ""

    # Embed Colors
    GENSHIN_COLOR: int = 0x5BC0BE  # Xanh ngọc Genshin
    HSR_COLOR: int = 0x9370DB      # Tím huyền ảo Astral Express
    PRIMARY_COLOR: int = 0x3498DB  # Xanh lam chủ đạo
    SUCCESS_COLOR: int = 0x2ECC71  # Xanh lá thành công
    ERROR_COLOR: int = 0xE74C3C    # Đỏ báo lỗi
    WARNING_COLOR: int = 0xF39C12  # Vàng cảnh báo

    # Assets & Card rendering
    ASSETS_DIR: Path = BASE_DIR / "assets"
    DATA_DIR: Path = BASE_DIR / "data"

    @property
    def db_file_path(self) -> Path:
        path = Path(self.DATABASE_PATH)
        if not path.is_absolute():
            return BASE_DIR / path
        return path

    @property
    def admin_ids(self) -> List[int]:
        if not self.ADMIN_USER_IDS:
            return []
        ids = []
        for x in self.ADMIN_USER_IDS.split(","):
            x = x.strip()
            if x.isdigit():
                ids.append(int(x))
        return ids


settings = Settings()
