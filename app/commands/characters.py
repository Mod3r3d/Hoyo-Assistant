"""Nhóm lệnh /characters tra cứu chi tiết nhân vật và vũ khí trong showcase."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.render.character_card import render_character_card
from app.services.account_service import account_service
from app.services.character_service import character_service
from app.services.settings_service import settings_service
from app.ui.common.paginator import PaginatorView


class CharacterCommands(commands.GroupCog, group_name="characters"):
    """Xem danh sách và chi tiết các nhân vật trong tủ trưng bày."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _handle_characters(
        self,
        interaction: discord.Interaction,
        game: GameType,
        target_uid: Optional[int] = None,
        target_user: Optional[discord.User] = None,
    ):
        user_settings = await settings_service.get_settings(interaction.user.id)
        await interaction.response.defer(ephemeral=user_settings.ephemeral_default)

        query_uid = target_uid
        if not query_uid:
            target_id = target_user.id if target_user else interaction.user.id
            acc = await account_service.get_default_or_first_account(target_id, game)
            if not acc:
                target_name = target_user.display_name if target_user else "bạn"
                await interaction.followup.send(
                    f"❌ Không tìm thấy UID {game.display_name} của {target_name}. Hãy liên kết qua `/account add` hoặc nhập UID.",
                    ephemeral=True,
                )
                return
            query_uid = acc.uid

        characters = await character_service.get_showcase_characters(game, query_uid)

        if not characters:
            await interaction.followup.send(
                f"Tủ trưng bày nhân vật của UID `{query_uid}` đang trống hoặc bị ẩn trong game.",
                ephemeral=True,
            )
            return

        embeds = []
        for char in characters:
            badge = "C" if game == GameType.GENSHIN else "E"
            const_val = getattr(char, "constellation", getattr(char, "eidolon", 0))

            embed = discord.Embed(
                title=f"{char.name} (Lv.{char.level})",
                description=f"**Nguyên Tố:** {getattr(char, 'element', 'Khác')}  •  **{badge}{const_val}**  •  **UID:** `{query_uid}`",
                color=0x5BC0BE if game == GameType.GENSHIN else 0x9370DB,
            )

            # Vũ khí / Nón Ánh Sáng
            equip = getattr(char, "weapon", getattr(char, "light_cone", None))
            if equip:
                refine_val = getattr(equip, "refinement", getattr(equip, "superimposition", 1))
                refine_tag = "Tinh Luyện" if game == GameType.GENSHIN else "Tích Lũy"
                embed.add_field(
                    name="⚔️ Trang Bị",
                    value=f"**{equip.name}**\nCấp {equip.level} • {refine_tag} R{refine_val}",
                    inline=True,
                )

            # Chỉ số nổi bật
            stats = getattr(char, "stats", {})
            if stats:
                stat_str = "\n".join([f"• **{k}**: {v}" for k, v in list(stats.items())[:10]])
                embed.add_field(name="📊 Chỉ Số Chiến Đấu", value=stat_str, inline=True)

            embeds.append(embed)

        paginator = PaginatorView(interaction.user.id, embeds=embeds)
        await interaction.followup.send(embed=embeds[0], view=paginator)

    @app_commands.command(name="genshin", description="Xem danh sách nhân vật trưng bày trong Genshin Impact")
    @app_commands.describe(uid="UID Genshin", user="Người dùng Discord đã liên kết tài khoản")
    async def characters_genshin(
        self,
        interaction: discord.Interaction,
        uid: Optional[int] = None,
        user: Optional[discord.User] = None,
    ):
        await self._handle_characters(interaction, GameType.GENSHIN, uid, user)

    @app_commands.command(name="hsr", description="Xem danh sách nhân vật trưng bày trong Honkai: Star Rail")
    @app_commands.describe(uid="UID Star Rail", user="Người dùng Discord đã liên kết tài khoản")
    async def characters_hsr(
        self,
        interaction: discord.Interaction,
        uid: Optional[int] = None,
        user: Optional[discord.User] = None,
    ):
        await self._handle_characters(interaction, GameType.HSR, uid, user)


async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterCommands(bot))
