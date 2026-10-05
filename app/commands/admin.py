"""Lệnh /admin quản trị hệ thống tự động hóa dành riêng cho Administrator."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.automation.manager import automation_manager
from app.config import settings
from app.db.repositories.automation import AutomationLogRepository


class AdminCommands(commands.GroupCog, group_name="admin"):
    """Công cụ quản trị hệ thống tự động hóa (Chỉ dành cho Admin bot)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _is_admin(self, user_id: int) -> bool:
        if not settings.admin_ids:
            # Nếu chưa cấu hình admin_ids trong .env, cho phép người dùng chạy lệnh để test
            return True
        return user_id in settings.admin_ids

    @app_commands.command(name="auto_status", description="Xem trạng thái hoạt động chi tiết của Scheduler và Task Logs")
    async def admin_auto_status(self, interaction: discord.Interaction):
        if not self._is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền quản trị viên bot.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        scheduler = automation_manager.scheduler

        is_running = automation_manager._running and scheduler is not None
        jobs_info = []

        if is_running and scheduler:
            for j in scheduler.get_jobs():
                next_run = j.next_run_time.strftime("%H:%M:%S %d/%m/%Y") if j.next_run_time else "Chưa xếp lịch"
                jobs_info.append(f"• **{j.name}** (`{j.id}`)\n  └─ Lần chạy tiếp: `{next_run}`")

        # Lấy 5 log thực thi gần nhất
        recent_logs = await AutomationLogRepository.get_recent_logs(limit=5)
        log_lines = []
        for l in recent_logs:
            time_str = l.created_at.strftime("%H:%M:%S") if l.created_at else ""
            log_lines.append(f"[{time_str}] **{l.task_name}** ({l.status} - {l.duration_ms}ms): {l.message}")

        embed = discord.Embed(
            title="🛠️ Quản Trị Hệ Thống Tự Động Hóa (Admin Dashboard)",
            description=(
                f"• **Trạng thái Scheduler:** {'🟢 Đang hoạt động' if is_running else '🔴 Tạm dừng'}\n"
                f"• **Chế độ:** `{settings.AUTOMATION_MODE.upper()}`\n"
                f"• **Múi giờ:** `{settings.TIMEZONE}`"
            ),
            color=0x2ECC71 if is_running else 0xE74C3C,
        )

        if jobs_info:
            embed.add_field(name="⏰ Danh Sách Job Đang Lập Lịch", value="\n".join(jobs_info), inline=False)

        if log_lines:
            embed.add_field(name="📜 5 Nhật Ký Thực Thi Gần Nhất", value="\n".join(log_lines), inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="auto_run", description="Kích hoạt thủ công một tác vụ bất kỳ")
    @app_commands.describe(tac_vu="Tác vụ muốn chạy cưỡng bức")
    @app_commands.choices(
        tac_vu=[
            app_commands.Choice(name="Điểm danh HoYoLAB", value="checkin"),
            app_commands.Choice(name="Quét tìm Giftcode", value="giftcode_discovery"),
            app_commands.Choice(name="Đổi Giftcode tự động", value="giftcode_redeem"),
            app_commands.Choice(name="Nhiệm vụ Mimo", value="mimo"),
            app_commands.Choice(name="Điểm danh Đồng Hành", value="accompany"),
            app_commands.Choice(name="Quét Sự Kiện Web", value="events"),
        ]
    )
    async def admin_auto_run(self, interaction: discord.Interaction, tac_vu: app_commands.Choice[str]):
        if not self._is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền quản trị viên bot.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        res = await automation_manager.run_manually(tac_vu.value)

        embed = discord.Embed(
            title=f"⚡ Quản Trị: Kích Hoạt Tác Vụ {tac_vu.name}",
            description=f"Kết quả:\n```json\n{res}\n```",
            color=0x3498DB,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
