"""Nhóm lệnh /build hướng dẫn xây dựng trang bị và đội hình nhân vật (Build Guides)."""

from typing import List
import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.games.genshin.build_data import GENSHIN_BUILDS
from app.games.hsr.build_data import HSR_BUILDS
from app.services.build_service import build_service


class BuildCommands(commands.GroupCog, group_name="build"):
    """Xem hướng dẫn xây dựng vũ khí, di vật và đội hình cho nhân vật."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Autocomplete cho nhân vật Genshin
    async def genshin_char_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        q = current.lower()
        for key, build in GENSHIN_BUILDS.items():
            if q in build.character_name.lower():
                choices.append(app_commands.Choice(name=f"{build.character_name} ({build.element})", value=build.character_name))
            if len(choices) >= 25:
                break
        return choices

    # Autocomplete cho nhân vật HSR
    async def hsr_char_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        q = current.lower()
        for key, build in HSR_BUILDS.items():
            if q in build.character_name.lower():
                choices.append(app_commands.Choice(name=f"{build.character_name} ({build.element} - {build.path})", value=build.character_name))
            if len(choices) >= 25:
                break
        return choices

    @app_commands.command(name="genshin", description="Xem hướng dẫn build nhân vật Genshin Impact")
    @app_commands.describe(nhan_vat="Tên nhân vật bạn muốn xem hướng dẫn")
    @app_commands.autocomplete(nhan_vat=genshin_char_autocomplete)
    async def build_genshin(self, interaction: discord.Interaction, nhan_vat: str):
        await interaction.response.defer()
        build = await build_service.get_build(GameType.GENSHIN, nhan_vat)

        if not build:
            await interaction.followup.send(
                f"❌ Chưa có dữ liệu hướng dẫn cho nhân vật **{nhan_vat}** trong Genshin Impact.\n"
                f"💡 Bạn có thể thử gõ tên như: *Furina, Neuvillette, Arlecchino, Raiden Shogun, Zhongli, Nahida, Kazuha...*",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📖 Hướng Dẫn Build: {build.character_name}",
            description=f"**Hệ:** {build.element}  •  **Độ hiếm:** {build.rarity}⭐  •  **Vai trò:** {build.role}",
            color=0x5BC0BE,
        )

        # Vũ khí
        embed.add_field(
            name="⚔️ Vũ Khí Khuyên Dùng",
            value="\n".join([f"{i+1}. {w}" for i, w in enumerate(build.weapons)]),
            inline=False,
        )

        # Thánh di vật
        embed.add_field(
            name="🛡️ Thánh Di Vật",
            value="\n".join([f"• {s}" for s in build.artifact_sets]),
            inline=False,
        )

        # Chỉ số chính
        stats_text = "\n".join([f"• **{k}**: {v}" for k, v in build.main_stats.items()])
        embed.add_field(name="🎯 Chỉ Số Chính Từng Mảnh", value=stats_text, inline=True)

        # Chỉ số phụ
        substats_text = "\n".join([f"• {s}" for s in build.substats])
        embed.add_field(name="⚡ Ưu Tiên Dòng Phụ", value=substats_text, inline=True)

        # Ưu tiên nâng thiên phú
        embed.add_field(name="📚 Thứ Tự Nâng Thiên Phú", value=build.talent_priority, inline=False)

        # Đội hình tiêu biểu
        if build.team_synergy:
            teams_text = "\n".join([f"• {t}" for t in build.team_synergy])
            embed.add_field(name="👥 Đội Hình Tiêu Biểu", value=teams_text, inline=False)

        if build.notes:
            embed.add_field(name="💡 Lưu Ý Khi Chơi", value=build.notes, inline=False)

        embed.set_footer(text="Dữ liệu tổng hợp từ các chuyên gia chiến thuật và meta hiện tại.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hsr", description="Xem hướng dẫn build nhân vật Honkai: Star Rail")
    @app_commands.describe(nhan_vat="Tên nhân vật bạn muốn xem hướng dẫn")
    @app_commands.autocomplete(nhan_vat=hsr_char_autocomplete)
    async def build_hsr(self, interaction: discord.Interaction, nhan_vat: str):
        await interaction.response.defer()
        build = await build_service.get_build(GameType.HSR, nhan_vat)

        if not build:
            await interaction.followup.send(
                f"❌ Chưa có dữ liệu hướng dẫn cho nhân vật **{nhan_vat}** trong Star Rail.\n"
                f"💡 Bạn có thể thử gõ tên như: *Acheron, Firefly, Feixiao, Robin, Sunday, Ruan Mei, Aventurine...*",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📖 Hướng Dẫn Build: {build.character_name}",
            description=f"**Thuộc Tính:** {build.element}  •  **Vận Mệnh:** {build.path}  •  **Vai trò:** {build.role}",
            color=0x9370DB,
        )

        embed.add_field(
            name="🔮 Nón Ánh Sáng Khuyên Dùng",
            value="\n".join([f"{i+1}. {w}" for i, w in enumerate(build.light_cones)]),
            inline=False,
        )

        embed.add_field(
            name="🛡️ Di Vật & Phụ Kiện Vị Diện",
            value=(
                "**Bộ Di Vật:**\n" + "\n".join([f"• {s}" for s in build.relic_sets]) +
                "\n\n**Phụ Kiện Vị Diện:**\n" + "\n".join([f"• {p}" for p in build.planar_sets])
            ),
            inline=False,
        )

        stats_text = "\n".join([f"• **{k}**: {v}" for k, v in build.main_stats.items()])
        embed.add_field(name="🎯 Chỉ Số Chính Từng Mảnh", value=stats_text, inline=True)

        substats_text = "\n".join([f"• {s}" for s in build.substats])
        embed.add_field(name="⚡ Ưu Tiên Dòng Phụ", value=substats_text, inline=True)

        embed.add_field(name="📚 Thứ Tự Nâng Vết Tích", value=build.trace_priority, inline=False)

        if build.team_synergy:
            teams_text = "\n".join([f"• {t}" for t in build.team_synergy])
            embed.add_field(name="👥 Đội Hình Tiêu Biểu", value=teams_text, inline=False)

        if build.notes:
            embed.add_field(name="💡 Lưu Ý Khi Chơi", value=build.notes, inline=False)

        embed.set_footer(text="Dữ liệu tổng hợp từ các chuyên gia chiến thuật và meta hiện tại.")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BuildCommands(bot))
