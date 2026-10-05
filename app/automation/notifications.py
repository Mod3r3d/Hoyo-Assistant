"""Trung tâm điều phối thông báo Discord (Notification Center)."""

from typing import Optional
import discord
from loguru import logger
from app.config import settings


class NotificationService:
    def __init__(self, bot: Optional[discord.Client] = None):
        self.bot = bot

    def set_bot(self, bot: discord.Client):
        self.bot = bot

    async def notify_user(
        self,
        discord_user_id: int,
        title: str,
        description: str,
        color: int = 0x3498DB,
        fields: Optional[list] = None,
        channel_id: Optional[int] = None,
    ) -> bool:
        """Gửi thông báo đến kênh chỉ định hoặc DM của người dùng."""
        if not self.bot:
            logger.warning(f"Bot client chưa được gán cho NotificationService, bỏ qua thông báo tới {discord_user_id}")
            return False

        embed = discord.Embed(title=title, description=description, color=color)
        if fields:
            for name, val, inline in fields:
                embed.add_field(name=name, value=val, inline=inline)
        embed.set_footer(text="HoyoBot Automation • Thông báo tự động")

        # 1. Thử gửi qua Channel nếu có channel_id
        if channel_id:
            try:
                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                if isinstance(channel, discord.TextChannel):
                    await channel.send(content=f"<@{discord_user_id}>", embed=embed)
                    return True
            except Exception as e:
                logger.debug(f"Không thể gửi thông báo qua channel {channel_id}: {e}")

        # 2. Gửi qua DM nếu không gửi được qua Channel
        try:
            user = self.bot.get_user(discord_user_id) or await self.bot.fetch_user(discord_user_id)
            if user:
                await user.send(embed=embed)
                return True
        except discord.Forbidden:
            logger.warning(f"Không thể gửi DM cho user {discord_user_id} (Người dùng đã khóa DM).")
        except Exception as e:
            logger.error(f"Lỗi khi gửi thông báo tới user {discord_user_id}: {e}")

        return False

    async def broadcast_event(self, title: str, description: str, color: int = 0xF39C12, url: str = ""):
        """Thông báo sự kiện web hoặc giftcode mới."""
        logger.info(f"[Broadcast Alert] {title}: {description}")


notification_service = NotificationService()
