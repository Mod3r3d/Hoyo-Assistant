"""UI View tương tác cho lệnh /settings."""

import discord
from discord.ui import View, button, Button
from app.db.models.user import SettingsModel
from app.services.settings_service import settings_service


class SettingsView(View):
    def __init__(self, author_id: int, user_settings: SettingsModel, timeout: float = 90.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.settings = user_settings
        self._sync_buttons()

    def _sync_buttons(self):
        # Nút ẩn/hiện UID
        self.toggle_uid_btn.label = "Hiện UID công khai: BẬT" if self.settings.show_uid else "Hiện UID công khai: TẮT"
        self.toggle_uid_btn.style = discord.ButtonStyle.success if self.settings.show_uid else discord.ButtonStyle.secondary

        # Nút dùng ảnh card
        self.toggle_cards_btn.label = "Đồ họa Card ảnh: BẬT" if self.settings.use_cards else "Đồ họa Card ảnh: TẮT"
        self.toggle_cards_btn.style = discord.ButtonStyle.success if self.settings.use_cards else discord.ButtonStyle.secondary

        # Nút phản hồi ẩn danh (Ephemeral)
        self.toggle_ephemeral_btn.label = "Tin nhắn riêng tư: BẬT" if self.settings.ephemeral_default else "Tin nhắn riêng tư: TẮT"
        self.toggle_ephemeral_btn.style = discord.ButtonStyle.success if self.settings.ephemeral_default else discord.ButtonStyle.secondary

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không có quyền thao tác trên cài đặt của người khác.", ephemeral=True)
            return False
        return True

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="⚙️ Cài Đặt Cá Nhân",
            description="Tùy chỉnh trải nghiệm hiển thị và quyền riêng tư của bạn với HoyoBot.",
            color=0x3498DB,
        )
        embed.add_field(
            name="👁️ Hiển Thị UID",
            value="Hiển thị đầy đủ UID khi tạo card/embed" if self.settings.show_uid else "Ẩn một phần UID (`812***678`) để bảo mật",
            inline=False,
        )
        embed.add_field(
            name="🖼️ Chế Độ Đồ Họa Card",
            value="Tạo ảnh đồ họa màu sắc sang trọng" if self.settings.use_cards else "Chỉ gửi bảng chữ Discord Embed nhanh gọn",
            inline=False,
        )
        embed.add_field(
            name="🔒 Phản Hồi Riêng Tư (Ephemeral)",
            value="Chỉ bạn nhìn thấy tin nhắn trả lời" if self.settings.ephemeral_default else "Mọi người trong kênh đều thấy kết quả",
            inline=False,
        )
        embed.set_footer(text="Nhấn các nút bên dưới để bật/tắt thiết lập tương ứng.")
        return embed

    @button(label="Hiện UID công khai", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def toggle_uid_btn(self, interaction: discord.Interaction, btn: Button):
        self.settings = await settings_service.update_settings(
            self.author_id, show_uid=not self.settings.show_uid
        )
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @button(label="Đồ họa Card ảnh", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def toggle_cards_btn(self, interaction: discord.Interaction, btn: Button):
        self.settings = await settings_service.update_settings(
            self.author_id, use_cards=not self.settings.use_cards
        )
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @button(label="Tin nhắn riêng tư", style=discord.ButtonStyle.secondary, emoji="🔒")
    async def toggle_ephemeral_btn(self, interaction: discord.Interaction, btn: Button):
        self.settings = await settings_service.update_settings(
            self.author_id, ephemeral_default=not self.settings.ephemeral_default
        )
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)
