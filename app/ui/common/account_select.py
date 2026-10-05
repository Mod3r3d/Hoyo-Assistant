"""Thành phần chọn tài khoản (Account Select) và Xác nhận thao tác (Confirmation)."""

from typing import Callable, Coroutine, List, Optional
import discord
from discord.ui import Select, View, button, Button
from app.db.models.account import AccountModel


class AccountSelectDropdown(Select):
    def __init__(self, accounts: List[AccountModel], placeholder: str = "Chọn tài khoản game..."):
        options = [
            discord.SelectOption(
                label=acc.nickname or f"{acc.game.short_name} - {acc.uid}",
                description=f"UID: {acc.uid} ({acc.server.value}){' • [Mặc định]' if acc.is_default else ''}",
                value=str(acc.id),
                emoji=acc.game.discord_emoji,
            )
            for acc in accounts[:25]
        ]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)


class AccountSelectView(View):
    def __init__(
        self,
        author_id: int,
        accounts: List[AccountModel],
        on_select_callback: Callable[[discord.Interaction, int], Coroutine],
        timeout: float = 60.0,
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.on_select_callback = on_select_callback

        self.dropdown = AccountSelectDropdown(accounts)
        self.dropdown.callback = self._on_select
        self.add_item(self.dropdown)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không có quyền thao tác trên menu này.", ephemeral=True)
            return False
        return True

    async def _on_select(self, interaction: discord.Interaction):
        selected_id = int(self.dropdown.values[0])
        await self.on_select_callback(interaction, selected_id)


class ConfirmationView(View):
    def __init__(self, author_id: int, timeout: float = 45.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value: Optional[bool] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không có quyền thao tác trên menu này.", ephemeral=True)
            return False
        return True

    @button(label="Xác nhận", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, interaction: discord.Interaction, btn: Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @button(label="Hủy bỏ", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, btn: Button):
        self.value = False
        self.stop()
        await interaction.response.defer()
