"""Nhóm lệnh /search tra cứu bách khoa dữ liệu Genshin và Star Rail."""

from typing import List
import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.games.genshin.constants import GENSHIN_CHARACTERS
from app.games.hsr.constants import HSR_CHARACTERS
from app.services.search_service import search_service


class SearchCommands(commands.GroupCog, group_name="search"):
    """Tra cứu bách khoa dữ liệu nhân vật, vũ khí trong game."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def genshin_search_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        q = current.lower()
        for char_id, meta in GENSHIN_CHARACTERS.items():
            if q in meta["name"].lower() or q in meta["element"].lower():
                choices.append(app_commands.Choice(name=f"{meta['name']} ({meta['element']})", value=meta["name"]))
            if len(choices) >= 25:
                break
        return choices

    async def hsr_search_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        q = current.lower()
        for char_id, meta in HSR_CHARACTERS.items():
            if q in meta["name"].lower() or q in meta["element"].lower() or q in meta["path"].lower():
                choices.append(app_commands.Choice(name=f"{meta['name']} ({meta['element']} - {meta['path']})", value=meta["name"]))
            if len(choices) >= 25:
                break
        return choices

    @app_commands.command(name="genshin", description="Tìm kiếm nhân vật trong cơ sở dữ liệu Genshin Impact")
    @app_commands.describe(tu_khoa="Từ khóa hoặc tên nhân vật cần tìm")
    @app_commands.autocomplete(tu_khoa=genshin_search_autocomplete)
    async def search_genshin(self, interaction: discord.Interaction, tu_khoa: str):
        await interaction.response.defer()
        results = await search_service.search(GameType.GENSHIN, tu_khoa)

        if not results:
            await interaction.followup.send(f"❌ Không tìm thấy kết quả nào phù hợp với từ khóa `{tu_khoa}` trong Genshin Impact.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Kết Quả Tìm Kiếm Genshin: '{tu_khoa}'",
            description=f"Tìm thấy **{len(results)}** kết quả liên quan:",
            color=0x5BC0BE,
        )

        for item in results[:10]:
            embed.add_field(
                name=f"⭐ {item['title']}",
                value=f"Phân loại: {item.get('category', 'Chung')} • {item.get('description', '')}",
                inline=False,
            )

        if len(results) > 10:
            embed.set_footer(text=f"Và còn {len(results) - 10} kết quả khác...")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hsr", description="Tìm kiếm nhân vật trong cơ sở dữ liệu Honkai: Star Rail")
    @app_commands.describe(tu_khoa="Từ khóa hoặc tên nhân vật cần tìm")
    @app_commands.autocomplete(tu_khoa=hsr_search_autocomplete)
    async def search_hsr(self, interaction: discord.Interaction, tu_khoa: str):
        await interaction.response.defer()
        results = await search_service.search(GameType.HSR, tu_khoa)

        if not results:
            await interaction.followup.send(f"❌ Không tìm thấy kết quả nào phù hợp với từ khóa `{tu_khoa}` trong Star Rail.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🔍 Kết Quả Tìm Kiếm Star Rail: '{tu_khoa}'",
            description=f"Tìm thấy **{len(results)}** kết quả liên quan:",
            color=0x9370DB,
        )

        for item in results[:10]:
            embed.add_field(
                name=f"⭐ {item['title']}",
                value=f"Phân loại: {item.get('category', 'Chung')} • {item.get('description', '')}",
                inline=False,
            )

        if len(results) > 10:
            embed.set_footer(text=f"Và còn {len(results) - 10} kết quả khác...")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCommands(bot))
