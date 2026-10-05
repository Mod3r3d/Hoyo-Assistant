"""UI Views và Modals tương tác cho tính năng Automation v2."""

import discord
from discord.ui import Button, Modal, Select, TextInput, View, button
from app.automation.manager import automation_manager
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    SessionRepository,
)
from app.games.enums import GameType
from app.security.encryption import mask_cookie


class CookieInputModal(Modal, title="Thêm / Cập Nhật Cookie HoYoLAB"):
    cookie_input = TextInput(
        label="Dán Cookie HoYoLAB của bạn vào đây",
        style=discord.TextStyle.paragraph,
        placeholder="ltuid_v2=...; ltoken_v2=...; ltmid_v2=...;",
        required=True,
        min_length=20,
        max_length=2000,
    )

    def __init__(self, account_id: int, discord_user_id: int, game: GameType, uid: int):
        super().__init__()
        self.account_id = account_id
        self.discord_user_id = discord_user_id
        self.game = game
        self.uid = uid

    async def on_submit(self, interaction: discord.Interaction):
        raw_cookie = self.cookie_input.value.strip()

        # Lưu cookie đã mã hóa
        await SessionRepository.save_session(
            discord_user_id=self.discord_user_id,
            game=self.game,
            uid=self.uid,
            raw_cookie=raw_cookie,
        )

        # Đảm bảo có bản ghi automation_settings
        await AutomationSettingsRepository.get_or_create(self.account_id, self.discord_user_id)

        embed = discord.Embed(
            title="🔒 Đã Lưu Phiên Đăng Nhập Thành Công!",
            description=(
                f"Tài khoản: **{self.game.display_name}** (UID: `{self.uid}`)\n"
                f"Trạng thái: Cookie đã được **mã hóa bảo mật** trong cơ sở dữ liệu.\n\n"
                f"Các tính năng Tự động Điểm danh và Đổi Giftcode cho tài khoản này đã sẵn sàng!"
            ),
            color=0x2ECC71,
        )
        embed.set_footer(text="Hệ thống sẽ không bao giờ hiển thị Cookie thô ra bên ngoài.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AutomationDashboardView(View):
    def __init__(self, author_id: int, accounts_data: list, timeout: float = 120.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.accounts_data = accounts_data  # list of (AccountModel, AutomationSettingsModel, SessionModel | None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không có quyền thao tác trên menu này.", ephemeral=True)
            return False
        return True

    @button(label="⚡ Chạy Điểm Danh Ngay", style=discord.ButtonStyle.primary, emoji="📅", row=0)
    async def run_checkin_now(self, interaction: discord.Interaction, btn: Button):
        await interaction.response.defer(ephemeral=True)
        res = await automation_manager.run_manually("checkin")
        await interaction.followup.send(f"📋 **Kết quả Điểm danh:** {res.get('message', 'Đã thực thi')}", ephemeral=True)

    @button(label="🎁 Chạy Đổi Giftcode Ngay", style=discord.ButtonStyle.primary, emoji="🎁", row=0)
    async def run_redeem_now(self, interaction: discord.Interaction, btn: Button):
        await interaction.response.defer(ephemeral=True)
        res = await automation_manager.run_manually("giftcode_redeem")
        await interaction.followup.send(f"🎁 **Kết quả Đổi Mã:** {res.get('message', 'Đã thực thi')}", ephemeral=True)

    @button(label="🔑 Thêm/Đổi Cookie", style=discord.ButtonStyle.secondary, emoji="🔐", row=1)
    async def add_cookie_btn(self, interaction: discord.Interaction, btn: Button):
        if not self.accounts_data:
            await interaction.response.send_message("Bạn chưa có tài khoản nào. Hãy dùng `/account add` trước.", ephemeral=True)
            return

        # Nếu có 1 account, mở modal trực tiếp; nếu nhiều account, chọn account đầu tiên
        acc, _, _ = self.accounts_data[0]
        modal = CookieInputModal(
            account_id=acc.id,
            discord_user_id=interaction.user.id,
            game=acc.game,
            uid=acc.uid,
        )
        await interaction.response.send_modal(modal)

    @button(label="🗑️ Xóa Cookie Phiên", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def delete_cookie_btn(self, interaction: discord.Interaction, btn: Button):
        if not self.accounts_data:
            await interaction.response.send_message("Bạn chưa có tài khoản nào.", ephemeral=True)
            return

        acc, _, _ = self.accounts_data[0]
        deleted = await SessionRepository.delete_session(interaction.user.id, acc.game, acc.uid)
        if deleted:
            await interaction.response.send_message(f"🗑️ Đã xóa phiên đăng nhập của tài khoản UID `{acc.uid}`.", ephemeral=True)
        else:
            await interaction.response.send_message("Tài khoản này chưa lưu Cookie nào.", ephemeral=True)
