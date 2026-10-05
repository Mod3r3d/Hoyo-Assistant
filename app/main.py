"""Điểm khởi chạy ứng dụng HoyoBot (Main Entrypoint)."""

import sys
from loguru import logger
from app.config import settings
from app.bot.client import HoyoBot


def setup_logging():
    """Cấu hình định dạng ghi log trực quan và đẹp mắt."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    logger.add(sys.stdout, format=log_format, level=settings.LOG_LEVEL, colorize=True)
    logger.add("logs/hoyobot.log", rotation="10 MB", retention="7 days", format=log_format, level="DEBUG", encoding="utf-8")


def main():
    setup_logging()
    logger.info("Đang khởi động HoyoBot (Genshin Impact & Honkai: Star Rail)...")

    if not settings.DISCORD_TOKEN:
        logger.warning(
            "⚠️ CHƯA CẤU HÌNH DISCORD_TOKEN trong file .env!\n"
            "👉 Vui lòng mở file .env và điền Token bot của bạn vào dòng:\n"
            "   DISCORD_TOKEN=your_token_here\n"
            "Sau đó chạy lại bot."
        )
        return

    bot = HoyoBot()

    try:
        bot.run(settings.DISCORD_TOKEN, log_handler=None)
    except KeyboardInterrupt:
        logger.info("Nhận tín hiệu dừng từ người dùng (Ctrl+C). Đang tắt bot...")
    except Exception as e:
        logger.exception(f"Lỗi ngoài ý muốn khi chạy bot: {e}")


if __name__ == "__main__":
    main()
