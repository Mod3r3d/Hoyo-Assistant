"""Nhóm lệnh /giftcode tra cứu mã quà tặng và đổi thưởng thủ công."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.automation.providers.hoyolab import HoYoLABRedeemProvider
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import (
    GiftCodeRepository,
    SessionRepository,
)
from app.games.enums import GameType


class GiftcodeCommands(commands.GroupCog, group_name="giftcode"):
    """Tra cứu các mã quà tặng Giftcode hoạt động và đổi quà."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="list", description="Xem danh sách các mã Giftcode đang hoạt động")
    @app_commands.describe(game="Chọn tựa game muốn xem mã")
    @app_commands.choices(
        game=[
            app_commands.Choice(name="Genshin Impact", value=GameType.GENSHIN.value),
            app_commands.Choice(name="Honkai: Star Rail", value=GameType.HSR.value),
        ]
    )
    async def giftcode_list(self, interaction: discord.Interaction, game: Optional[app_commands.Choice[str]] = None):
        await interaction.response.defer()
        target_game = GameType(game.value) if game else None

        games_to_query = [target_game] if target_game else [GameType.GENSHIN, GameType.HSR]

        embed = discord.Embed(
            title="🎁 Danh Sách Giftcode Đang Hoạt Động",
            description="Các mã quà tặng phát hiện được bởi hệ thống tự động:",
            color=0xF39C12,
        )

        for g in games_to_query:
            codes = await GiftCodeRepository.get_active_codes(g)
            if codes:
                code_lines = []
                for c in codes[:12]:
                    badge = "✅" if getattr(c, "confidence", "MEDIUM") == "HIGH" else "🟢"
                    reward_info = f" • *{c.rewards}*" if c.rewards else ""
                    src_display = c.sources if c.sources else c.source
                    code_lines.append(f"{badge} **`{c.code}`**{reward_info}\n   └─ Xác nhận: `{src_display}`")
                embed.add_field(
                    name=f"{'🎮' if g == GameType.GENSHIN else '🚂'} {g.display_name} ({len(codes)} mã hoạt động)",
                    value="\n".join(code_lines),
                    inline=False,
                )
            else:
                embed.add_field(name=f"{g.display_name}", value="*Hiện chưa có mã mới*", inline=False)

        embed.set_footer(text="✅: Đã xác thực qua nhiều nguồn | Bot tự động đổi mã cho tài khoản bật Auto Redeem")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="redeem", description="Đổi thủ công một mã Giftcode cho tài khoản của bạn")
    @app_commands.describe(code="Mã giftcode cần đổi", game="Chọn tựa game")
    @app_commands.choices(
        game=[
            app_commands.Choice(name="Genshin Impact", value=GameType.GENSHIN.value),
            app_commands.Choice(name="Honkai: Star Rail", value=GameType.HSR.value),
        ]
    )
    async def giftcode_redeem(
        self, interaction: discord.Interaction, code: str, game: app_commands.Choice[str]
    ):
        await interaction.response.defer(ephemeral=True)
        game_enum = GameType(game.value)

        acc = await AccountRepository.get_default_account(interaction.user.id, game_enum)
        if not acc:
            await interaction.followup.send(
                f"❌ Bạn chưa có tài khoản {game_enum.display_name} mặc định nào. Hãy dùng `/account add` trước.",
                ephemeral=True,
            )
            return

        sess = await SessionRepository.get_session(interaction.user.id, acc.game, acc.uid)
        if not sess:
            await interaction.followup.send(
                "❌ Bạn chưa liên kết Cookie HoYoLAB cho tài khoản này! Dùng lệnh `/auto session_add` để thêm cookie.",
                ephemeral=True,
            )
            return

        cookie = await SessionRepository.get_decrypted_cookie(sess)
        status, msg = await HoYoLABRedeemProvider.redeem_code(
            game=acc.game,
            uid=acc.uid,
            server_region=acc.server.value,
            code=code,
            cookie=cookie,
        )

        embed = discord.Embed(
            title=f"🎁 Đổi Mã Giftcode: {code.upper()}",
            description=(
                f"Tài khoản: **{acc.nickname or acc.uid}** (UID: `{acc.uid}` - {acc.server.value})\n"
                f"Trạng thái: **{status}**\n"
                f"Kết quả: {msg}"
            ),
            color=0x2ECC71 if status == "SUCCESS" else 0xE74C3C,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(GiftcodeCommands(bot))
