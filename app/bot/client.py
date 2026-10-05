"""Lớp Client chính của Discord Bot (HoyoBot)."""

from typing import List
import discord
from discord.ext import commands
from loguru import logger
from app.bot.error_handler import on_app_command_error
from app.bot.lifecycle import on_startup, on_shutdown


EXTENSIONS: List[str] = [
    # Nhóm lệnh cốt lõi
    "app.commands.account",
    "app.commands.profile",
    "app.commands.characters",
    "app.commands.build",
    "app.commands.search",
    "app.commands.events",
    "app.commands.settings",
    # Nhóm lệnh Automation
    "app.commands.auto",
    "app.commands.checkin",
    "app.commands.giftcode",
    "app.commands.notify",
    "app.commands.admin",
]


class HoyoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        """Khởi động DB, Scheduler, load các extension lệnh và đồng bộ Slash Commands."""
        # 1. Khởi động vòng đời & Scheduler
        await on_startup(self)

        # 2. Đăng ký Global Error Handler cho Command Tree
        self.tree.on_error = on_app_command_error

        # 3. Nạp các module lệnh
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                logger.info(f"Đã nạp thành công module lệnh: {ext}")
            except Exception as e:
                logger.exception(f"Lỗi khi nạp module lệnh {ext}: {e}")

        # 4. Đồng bộ danh sách Slash Command lên Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Đã đồng bộ thành công {len(synced)} lệnh Slash lên Discord!")
        except Exception as e:
            logger.error(f"Lỗi đồng bộ Slash Command: {e}")

    async def close(self):
        """Dọn dẹp khi tắt bot."""
        await on_shutdown()
        await super().close()

    async def on_ready(self):
        logger.info(f"Bot đã đăng nhập thành công với tên: {self.user} (ID: {self.user.id if self.user else 'N/A'})")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="/auto & /help • HoyoBot",
        )
        await self.change_presence(status=discord.Status.online, activity=activity)
