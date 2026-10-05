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
            if not codes:
                embed.add_field(name=f"{g.display_name}", value="*Hiện chưa có mã mới*", inline=False)
                continue

            code_lines = []
            for c in codes:
                badge = "✅" if getattr(c, "confidence", "MEDIUM") == "HIGH" else "🟢"
                rewards = c.rewards
                if rewards and len(rewards) > 42:
                    rewards = rewards[:39] + "..."
                reward_info = f" • *{rewards}*" if rewards else ""
                src_display = c.sources if c.sources else c.source
                code_lines.append(f"{badge} **`{c.code}`**{reward_info}\n   └─ Xác nhận: `{src_display}`")

            # Chia nhỏ code_lines thành từng field không vượt quá 900 ký tự
            chunks = []
            curr_chunk = []
            curr_len = 0
            for line in code_lines:
                line_len = len(line) + 1
                if curr_len + line_len > 900:
                    if curr_chunk:
                        chunks.append(curr_chunk)
                    curr_chunk = [line]
                    curr_len = line_len
                else:
                    curr_chunk.append(line)
                    curr_len += line_len
            if curr_chunk:
                chunks.append(curr_chunk)

            game_icon = "🎮" if g == GameType.GENSHIN else "🚂"
            for p_idx, chunk in enumerate(chunks):
                part_label = f" (Phần {p_idx + 1})" if len(chunks) > 1 else ""
                field_title = f"{game_icon} {g.display_name}{part_label} — {len(codes)} mã hoạt động"
                embed.add_field(
                    name=field_title,
                    value="\n".join(chunk),
                    inline=False,
                )

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

    @app_commands.command(name="history", description="Xem lịch sử đổi giftcode của tài khoản bạn")
    async def giftcode_history(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.followup.send(
                "❌ Bạn chưa có tài khoản nào được liên kết. Hãy dùng `/account add` trước.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🎁 Lịch Sử Đổi Mã Giftcode",
            description="Các mã giftcode đã được đổi cho tài khoản của bạn:",
            color=0xF39C12,
        )

        for acc in accounts:
            redeems = await GiftCodeRepository.get_redemption_history(acc.id, limit=8)
            header = f"{'🎮' if acc.game == GameType.GENSHIN else '🚂'} {acc.nickname or acc.uid} ({acc.game.display_name} - `{acc.uid}`)"
            if redeems:
                lines = []
                for r in redeems:
                    status_icon = "✅" if r.status in ("SUCCESS", "ALREADY_REDEEMED") else "⚠️"
                    date_str = r.redeemed_at.strftime("%d/%m %H:%M") if r.redeemed_at else ""
                    lines.append(f"{status_icon} **`{r.code}`** — {r.status} {f'({date_str})' if date_str else ''}")
                embed.add_field(name=header, value="\n".join(lines), inline=False)
            else:
                embed.add_field(name=header, value="*Chưa có lượt đổi mã nào ghi nhận*", inline=False)

        embed.set_footer(text="Hệ thống lưu vết để đảm bảo không bị đổi trùng lặp mã.")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(GiftcodeCommands(bot))
