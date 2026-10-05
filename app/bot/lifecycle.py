"""Quản lý vòng đời khởi động (startup) và tắt (shutdown) của ứng dụng bot."""

import discord
from loguru import logger
from app.automation.manager import automation_manager
from app.automation.notifications import notification_service
from app.config import settings
from app.db.database import db
from app.integrations.enka_client import enka_client


async def on_startup(bot: discord.Client | None = None):
    """Khởi tạo tài nguyên khi bot khởi động."""
    logger.info("Đang khởi tạo tài nguyên hệ thống...")
    # Tạo thư mục dữ liệu nếu chưa có
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Kết nối cơ sở dữ liệu
    await db.connect()
    logger.info("Hệ thống cơ sở dữ liệu đã sẵn sàng.")

    # Cung cấp bot client cho notification service
    if bot:
        notification_service.set_bot(bot)

    # Khởi động Background Scheduler cho Automation v2
    automation_manager.start()


async def on_shutdown():
    """Giải phóng tài nguyên khi bot dừng."""
    logger.info("Đang đóng các kết nối và dừng bot...")
    automation_manager.stop()
    await enka_client.close()
    await db.close()
    logger.info("Đã dọn dẹp tài nguyên an toàn.")
