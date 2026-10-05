"""Lệnh /checkin điểm danh tức thì và kiểm tra trạng thái hôm nay."""

from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from app.automation.manager import automation_manager
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import CheckinRepository


class CheckinCommand(commands.GroupCog, group_name="checkin"):
    """Điểm danh HoYoLAB và kiểm tra lịch sử phần thưởng."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="now", description="Kích hoạt điểm danh ngay lập tức cho các tài khoản của bạn")
    async def checkin_now(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        res = await automation_manager.run_manually("checkin")

        embed = discord.Embed(
            title="📅 Kết Quả Điểm Danh Ngay",
            description=res.get("message", "Đã gửi yêu cầu điểm danh"),
            color=0x2ECC71 if res.get("status") == "SUCCESS" else 0xF39C12,
        )
        embed.set_footer(text="Hệ thống tự động đồng bộ phần thưởng vào hòm thư trong game.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="status", description="Kiểm tra trạng thái điểm danh hôm nay của bạn")
    async def checkin_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào. Hãy dùng `/account add` trước.", ephemeral=True)
            return

        today_str = datetime.now().strftime("%Y-%m-%d")
        lines = []

        for acc in accounts:
            checked = await CheckinRepository.has_checked_in_today(acc.id, today_str)
            status_text = "✅ Đã điểm danh thành công" if checked else "⏳ Chưa điểm danh hôm nay"
            lines.append(f"• **{acc.nickname or acc.uid}** ({acc.game.display_name} - `{acc.uid}`): {status_text}")

        embed = discord.Embed(
            title=f"📅 Trạng Thái Điểm Danh Ngày {today_str}",
            description="\n".join(lines),
            color=0x3498DB,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CheckinCommand(bot))
