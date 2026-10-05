"""Xử lý lỗi toàn cục cho Discord Slash Commands."""

import discord
from discord import app_commands
from loguru import logger
from app.games.base import GameException, GameRateLimitError, PlayerNotFoundError, ProfilePrivateError


async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Bắt và phản hồi tất cả các lỗi xảy ra trong quá trình thực thi Slash Command."""
    # Lấy lỗi gốc nếu bị bọc bởi CommandInvokeError
    original_error = getattr(error, "original", error)

    # 1. Các lỗi game nghiệp vụ đã định nghĩa
    if isinstance(original_error, PlayerNotFoundError):
        msg = f"❌ {original_error.message}"
    elif isinstance(original_error, ProfilePrivateError):
        msg = f"🔒 {original_error.message}"
    elif isinstance(original_error, GameRateLimitError):
        msg = f"⏳ {original_error.message}"
    elif isinstance(original_error, GameException):
        msg = f"⚠️ {original_error.message}"

    # 2. Lỗi Discord Cooldown
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = f"⏳ Bạn đang thao tác quá nhanh! Vui lòng đợi `{error.retry_after:.1f}` giây."

    # 3. Lỗi thiếu quyền
    elif isinstance(error, app_commands.MissingPermissions):
        perms = ", ".join(error.missing_permissions)
        msg = f"❌ Bạn không đủ quyền để thực hiện lệnh này (Thiếu: `{perms}`)."
    elif isinstance(error, app_commands.BotMissingPermissions):
        perms = ", ".join(error.missing_permissions)
        msg = f"❌ Bot không đủ quyền hạn trong kênh/server để chạy lệnh này (Thiếu: `{perms}`)."

    # 4. Lỗi không mong muốn khác
    else:
        logger.exception(f"Lỗi không mong muốn tại command /{interaction.command.name if interaction.command else 'unknown'}: {original_error}")
        msg = "❌ Đã xảy ra lỗi nội bộ khi xử lý lệnh. Vui lòng thử lại sau ít phút."

    # Gửi phản hồi phù hợp với trạng thái interaction
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception as e:
        logger.error(f"Không thể gửi tin nhắn báo lỗi đến người dùng: {e}")
