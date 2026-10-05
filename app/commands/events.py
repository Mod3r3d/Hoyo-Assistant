"""Nhóm lệnh /events theo dõi các sự kiện và banner trong Genshin Impact và Honkai: Star Rail."""

import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.services.event_service import event_service


class EventCommands(commands.GroupCog, group_name="events"):
    """Xem danh sách các sự kiện và banner đang diễn ra."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="genshin", description="Xem các sự kiện và banner đang diễn ra trong Genshin Impact")
    async def events_genshin(self, interaction: discord.Interaction):
        await interaction.response.defer()
        events = await event_service.get_events(GameType.GENSHIN)

        embed = discord.Embed(
            title="📅 Sự Kiện Genshin Impact Đang Diễn Ra",
            description="Tổng hợp các sự kiện trong trò chơi và banner cầu nguyện:",
            color=0x5BC0BE,
        )

        for ev in events:
            val_text = f"**Thời gian:** {ev.get('duration', 'N/A')}\n{ev.get('description', '')}\n[Xem chi tiết trang chủ]({ev.get('link', 'https://genshin.hoyoverse.com')})"
            embed.add_field(name=f"🎉 {ev.get('title')}", value=val_text, inline=False)

        embed.set_footer(text="Hệ thống tự động đồng bộ theo các cập nhật mới nhất.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hsr", description="Xem các sự kiện và banner đang diễn ra trong Honkai: Star Rail")
    async def events_hsr(self, interaction: discord.Interaction):
        await interaction.response.defer()
        events = await event_service.get_events(GameType.HSR)

        embed = discord.Embed(
            title="📅 Sự Kiện Honkai: Star Rail Đang Diễn Ra",
            description="Tổng hợp các sự kiện Khai Phá và banner bước nhảy:",
            color=0x9370DB,
        )

        for ev in events:
            val_text = f"**Thời gian:** {ev.get('duration', 'N/A')}\n{ev.get('description', '')}\n[Xem chi tiết trang chủ]({ev.get('link', 'https://hsr.hoyoverse.com')})"
            embed.add_field(name=f"🎉 {ev.get('title')}", value=val_text, inline=False)

        embed.set_footer(text="Hệ thống tự động đồng bộ theo các cập nhật mới nhất.")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EventCommands(bot))
