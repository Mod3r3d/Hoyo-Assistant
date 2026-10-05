"""Nhóm lệnh /auto quản lý trung tâm điều khiển Tự Động Hóa."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.automation.manager import automation_manager
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    SessionRepository,
)
from app.games.enums import GameType
from app.ui.automation.views import AutomationDashboardView, CookieInputModal


class AutoCommands(commands.GroupCog, group_name="auto"):
    """Trung tâm quản lý các tính năng tự động hóa (Điểm danh, Đổi giftcode, Mimo, Sự kiện)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="status", description="Xem trạng thái hoạt động của các tính năng tự động hóa")
    async def auto_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)

        if not accounts:
            await interaction.followup.send(
                "Bạn chưa có tài khoản nào được liên kết! Dùng lệnh `/account add` trước để bắt đầu.",
                ephemeral=True,
            )
            return

        accounts_data = []
        embed = discord.Embed(
            title="🤖 Bảng Điều Khiển Tự Động Hóa",
            description="Trạng thái cấu hình chạy nền cho các tài khoản game của bạn:",
            color=0x3498DB,
        )

        for acc in accounts:
            auto_set = await AutomationSettingsRepository.get_or_create(acc.id, interaction.user.id)
            sess = await SessionRepository.get_session(interaction.user.id, acc.game, acc.uid)
            accounts_data.append((acc, auto_set, sess))

            # Biểu tượng trạng thái session
            if not sess:
                session_text = "❌ Chưa liên kết Cookie (Bấm nút bên dưới để thêm)"
            elif sess.session_status == "VALID":
                session_text = "✅ Phiên đăng nhập hợp lệ (Đã mã hóa an toàn)"
            elif sess.session_status == "EXPIRED":
                session_text = "⚠️ Cookie đã hết hạn, cần cập nhật lại"
            else:
                session_text = f"❓ Trạng thái: {sess.session_status}"

            def mark(b: bool) -> str:
                return "✅ Bật" if b else "❌ Tắt"

            field_val = (
                f"**UID:** `{acc.uid}` ({acc.server.value})\n"
                f"**Phiên HoYoLAB:** {session_text}\n"
                f"├─ Tự động chạy nền: {mark(auto_set.automation_enabled)}\n"
                f"├─ Điểm danh hàng ngày: {mark(auto_set.checkin_enabled)}\n"
                f"├─ Tự động nhận Giftcode: {mark(auto_set.redeem_enabled)}\n"
                f"├─ Nhiệm vụ Mimo: {mark(auto_set.mimo_enabled)}\n"
                f"├─ Đồng hành (Accompany): {mark(auto_set.accompany_enabled)}\n"
                f"└─ Báo sự kiện Web: {mark(auto_set.event_notify_enabled)}\n"
            )
            embed.add_field(
                name=f"{'🎮' if acc.game == GameType.GENSHIN else '🚂'} {acc.nickname or acc.uid} ({acc.game.display_name})",
                value=field_val,
                inline=False,
            )

        embed.set_footer(text="Dùng /auto toggle để bật/tắt từng tính năng, hoặc bấm các nút bên dưới để thao tác nhanh.")
        view = AutomationDashboardView(interaction.user.id, accounts_data)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="toggle", description="Bật hoặc tắt tính năng tự động cụ thể")
    @app_commands.describe(
        tinh_nang="Chọn tính năng bạn muốn bật hoặc tắt",
        trang_thai="Chọn BẬT hoặc TẮT",
    )
    @app_commands.choices(
        tinh_nang=[
            app_commands.Choice(name="Toàn bộ Tự Động Hóa (Tất cả)", value="automation"),
            app_commands.Choice(name="Điểm Danh Hàng Ngày (Check-in)", value="checkin"),
            app_commands.Choice(name="Tự Động Đổi Giftcode (Auto Redeem)", value="redeem"),
            app_commands.Choice(name="Nhiệm Vụ Mimo", value="mimo"),
            app_commands.Choice(name="Điểm Danh Đồng Hành (Accompany)", value="accompany"),
            app_commands.Choice(name="Thông Báo Sự Kiện Web", value="events"),
        ],
        trang_thai=[
            app_commands.Choice(name="Bật (Hoạt động)", value="1"),
            app_commands.Choice(name="Tắt (Tạm ngưng)", value="0"),
        ],
    )
    async def auto_toggle(
        self,
        interaction: discord.Interaction,
        tinh_nang: app_commands.Choice[str],
        trang_thai: app_commands.Choice[str],
    ):
        await interaction.response.defer(ephemeral=True)
        enabled = trang_thai.value == "1"

        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào. Hãy dùng `/account add` trước.", ephemeral=True)
            return

        for acc in accounts:
            await AutomationSettingsRepository.get_or_create(acc.id, interaction.user.id)
            await AutomationSettingsRepository.update_feature(acc.id, tinh_nang.value, enabled)

        trang_thai_str = "BẬT" if enabled else "TẮT"
        await interaction.followup.send(
            f"✅ Đã **{trang_thai_str}** tính năng **{tinh_nang.name}** cho toàn bộ tài khoản của bạn!",
            ephemeral=True,
        )

    @app_commands.command(name="session_add", description="Mở cửa sổ thêm/cập nhật Cookie HoYoLAB an toàn")
    async def auto_session_add(self, interaction: discord.Interaction):
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.response.send_message(
                "Bạn chưa có tài khoản nào. Hãy dùng `/account add` trước.", ephemeral=True
            )
            return

        acc = accounts[0]
        modal = CookieInputModal(
            account_id=acc.id,
            discord_user_id=interaction.user.id,
            game=acc.game,
            uid=acc.uid,
        )
        await interaction.response.send_modal(modal)

    @app_commands.command(name="session_remove", description="Xóa phiên đăng nhập Cookie HoYoLAB đã lưu")
    async def auto_session_remove(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào.", ephemeral=True)
            return

        count = 0
        for acc in accounts:
            if await SessionRepository.delete_session(interaction.user.id, acc.game, acc.uid):
                count += 1

        await interaction.followup.send(
            f"🗑️ Đã xóa thành công {count} phiên đăng nhập Cookie khỏi hệ thống an toàn.",
            ephemeral=True,
        )

    @app_commands.command(name="run", description="Kích hoạt chạy ngay lập tức một tác vụ tự động")
    @app_commands.describe(tac_vu="Tác vụ muốn kích hoạt ngay")
    @app_commands.choices(
        tac_vu=[
            app_commands.Choice(name="Điểm danh ngay (Check-in)", value="checkin"),
            app_commands.Choice(name="Quét tìm Giftcode mới", value="giftcode_discovery"),
            app_commands.Choice(name="Đổi Giftcode ngay (Redeem)", value="giftcode_redeem"),
            app_commands.Choice(name="Nhiệm vụ Mimo", value="mimo"),
            app_commands.Choice(name="Điểm danh Đồng Hành", value="accompany"),
            app_commands.Choice(name="Quét Sự Kiện Web mới", value="events"),
        ]
    )
    async def auto_run_cmd(self, interaction: discord.Interaction, tac_vu: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        result = await automation_manager.run_manually(tac_vu.value)
        await interaction.followup.send(
            f"⚡ **Kết quả thực thi {tac_vu.name}:**\n{result.get('message', 'Đã xử lý xong')}",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoCommands(bot))
