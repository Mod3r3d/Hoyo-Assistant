"""Nhóm lệnh /profile tra cứu hồ sơ người chơi Genshin Impact và Honkai: Star Rail."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.render.profile_card import render_profile_card
from app.services.account_service import account_service
from app.services.profile_service import profile_service
from app.services.settings_service import settings_service
from app.ui.profile.views import ProfileView
from app.utils.validators import mask_uid


class ProfileCommands(commands.GroupCog, group_name="profile"):
    """Tra cứu hồ sơ tài khoản và tủ trưng bày nhân vật."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _handle_profile(
        self,
        interaction: discord.Interaction,
        game: GameType,
        target_uid: Optional[int] = None,
        target_user: Optional[discord.User] = None,
    ):
        user_settings = await settings_service.get_settings(interaction.user.id)
        is_ephemeral = user_settings.ephemeral_default
        await interaction.response.defer(ephemeral=is_ephemeral)

        query_uid = target_uid

        # Nếu không truyền UID, tìm theo user được tag hoặc chính người gọi lệnh
        if not query_uid:
            target_discord_id = target_user.id if target_user else interaction.user.id
            acc = await account_service.get_default_or_first_account(target_discord_id, game)
            if not acc:
                target_name = target_user.display_name if target_user else "bạn"
                await interaction.followup.send(
                    f"❌ Không tìm thấy UID {game.display_name} của {target_name}.\n"
                    f"👉 Hãy nhập trực tiếp UID trong lệnh, hoặc dùng `/account add` để liên kết UID.",
                    ephemeral=True,
                )
                return
            query_uid = acc.uid

        # Lấy dữ liệu profile từ service
        profile = await profile_service.get_profile(game, query_uid)

        # Quyết định hiển thị card ảnh hay embed
        show_uid = user_settings.show_uid

        if user_settings.use_cards:
            card_buffer = await render_profile_card(profile, game, show_uid=show_uid)
            file = discord.File(card_buffer, filename=f"profile_{query_uid}.png")

            embed = discord.Embed(
                title=f"Hồ Sơ {game.display_name}: {profile.nickname}",
                color=0x5BC0BE if game == GameType.GENSHIN else 0x9370DB,
            )
            embed.set_image(url=f"attachment://profile_{query_uid}.png")
            view = ProfileView(interaction.user.id, profile, game, show_uid=show_uid)
            await interaction.followup.send(embed=embed, file=file, view=view)
        else:
            # Chế độ embed văn bản thuần
            embed = discord.Embed(
                title=f"🎮 Hồ Sơ {game.display_name}: {profile.nickname}",
                description=f"UID: `{mask_uid(profile.uid, show_uid)}`\nChữ ký: *{profile.signature or 'Chưa đặt'}*",
                color=0x5BC0BE if game == GameType.GENSHIN else 0x9370DB,
            )
            embed.add_field(name="Hạng Cấp", value=f"Cấp: **{profile.level}**", inline=True)
            embed.add_field(name="Cấp Thế Giới / Cân Bằng", value=f"Cấp: **{profile.world_level}**", inline=True)
            embed.add_field(name="Thành Tựu", value=f"🏆 **{profile.achievement_count}**", inline=True)

            if profile.showcase_characters:
                char_lines = []
                for c in profile.showcase_characters:
                    badge = "C" if game == GameType.GENSHIN else "E"
                    const_val = getattr(c, "constellation", getattr(c, "eidolon", 0))
                    char_lines.append(f"• **{c.name}** (Lv.{c.level} • {badge}{const_val})")
                embed.add_field(name="Tủ Trưng Bày Nhân Vật", value="\n".join(char_lines), inline=False)

            view = ProfileView(interaction.user.id, profile, game, show_uid=show_uid)
            await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="genshin", description="Xem hồ sơ Genshin Impact (Hạng mạo hiểm, nhân vật trưng bày)")
    @app_commands.describe(
        uid="UID Genshin muốn tra cứu (bỏ trống để dùng tài khoản đã lưu)",
        user="Người dùng Discord muốn tra cứu hồ sơ (nếu họ đã lưu tài khoản)",
    )
    async def profile_genshin(
        self,
        interaction: discord.Interaction,
        uid: Optional[int] = None,
        user: Optional[discord.User] = None,
    ):
        await self._handle_profile(interaction, GameType.GENSHIN, uid, user)

    @app_commands.command(name="hsr", description="Xem hồ sơ Honkai: Star Rail (Cấp khai phá, nhân vật trưng bày)")
    @app_commands.describe(
        uid="UID Star Rail muốn tra cứu (bỏ trống để dùng tài khoản đã lưu)",
        user="Người dùng Discord muốn tra cứu hồ sơ (nếu họ đã lưu tài khoản)",
    )
    async def profile_hsr(
        self,
        interaction: discord.Interaction,
        uid: Optional[int] = None,
        user: Optional[discord.User] = None,
    ):
        await self._handle_profile(interaction, GameType.HSR, uid, user)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCommands(bot))
