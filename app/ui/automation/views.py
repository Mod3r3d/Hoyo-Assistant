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
        placeholder="ltuid_v2=...; ltoken_v2=...; cookie_token_v2=...;",
        required=True,
        min_length=20,
        max_length=2000,
    )

    def __init__(
        self,
        discord_user_id: int,
        target_scope: str = "all",
        account_id: int | None = None,
        game: GameType | None = None,
        uid: int | None = None,
    ):
        super().__init__()
        self.discord_user_id = discord_user_id
        self.target_scope = target_scope
        self.account_id = account_id
        self.game = game
        self.uid = uid

    async def on_submit(self, interaction: discord.Interaction):
        raw_cookie = self.cookie_input.value.strip()

        user_accounts = await AccountRepository.get_accounts_by_user(self.discord_user_id)
        if not user_accounts:
            await interaction.response.send_message("❌ Bạn chưa có tài khoản nào được liên kết.", ephemeral=True)
            return

        targets = []
        for acc in user_accounts:
            if self.target_scope == "all":
                targets.append(acc)
            elif self.target_scope == acc.game.value:
                targets.append(acc)
            elif self.uid and acc.uid == self.uid:
                targets.append(acc)

        if not targets:
            targets = user_accounts

        saved_names = []
        for acc in targets:
            await SessionRepository.save_session(
                discord_user_id=self.discord_user_id,
                game=acc.game,
                uid=acc.uid,
                raw_cookie=raw_cookie,
            )
            await AutomationSettingsRepository.get_or_create(acc.id, self.discord_user_id)
            saved_names.append(f"{acc.game.emoji} **{acc.game.display_name}** (`{acc.uid}`)")

        has_cookie_token = "cookie_token" in raw_cookie
        redeem_note = (
            "🎁 **Đổi Giftcode:** Đã phát hiện token đổi mã, sẵn sàng tự động nhận giftcode!"
            if has_cookie_token
            else "⚠️ **Lưu ý Giftcode:** Thiếu `cookie_token_v2`. Điểm danh hoạt động tốt, nhưng để tự động đổi Giftcode bạn cần thêm `cookie_token_v2` từ tab Cookies trong F12."
        )

        acc_list_str = "\n• " + "\n• ".join(saved_names)

        embed = discord.Embed(
            title="🔒 Đã Lưu Phiên Đăng Nhập Thành Công!",
            description=(
                f"Đã lưu và đồng bộ Cookie an toàn cho các tài khoản:{acc_list_str}\n\n"
                f"📅 **Điểm danh hàng ngày:** Đã kích hoạt.\n"
                f"{redeem_note}\n\n"
                f"💡 *Gợi ý:* Bạn có thể gõ `/auto run tac_vu: Điểm danh ngay` để kiểm tra kết quả ngay lập tức."
            ),
            color=0x2ECC71,
        )
        embed.set_footer(text="Hệ thống luôn mã hóa bảo mật toàn bộ dữ liệu Cookie.")
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

        modal = CookieInputModal(
            discord_user_id=interaction.user.id,
            target_scope="all",
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
