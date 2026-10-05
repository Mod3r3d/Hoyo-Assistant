"""Thành phần phân trang (Paginator View) dùng chung cho Discord UI."""

from typing import List, Optional
import discord
from discord.ui import View, button, Button


class PaginatorView(View):
    def __init__(
        self,
        author_id: int,
        embeds: Optional[List[discord.Embed]] = None,
        files: Optional[List[discord.File]] = None,
        timeout: float = 120.0,
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.embeds = embeds or []
        self.files = files or []
        self.current_page = 0
        self.max_pages = max(len(self.embeds), len(self.files), 1)
        self._update_buttons()

    def _update_buttons(self):
        self.first_button.disabled = self.current_page == 0
        self.prev_button.disabled = self.current_page == 0
        self.page_indicator.label = f"Trang {self.current_page + 1}/{self.max_pages}"
        self.next_button.disabled = self.current_page >= self.max_pages - 1
        self.last_button.disabled = self.current_page >= self.max_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Bạn không thể thao tác trên menu điều hướng của người khác.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        # Vô hiệu hóa nút bấm khi hết thời gian chờ
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

    @button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="paginator_first")
    async def first_button(self, interaction: discord.Interaction, btn: Button):
        self.current_page = 0
        self._update_buttons()
        await self._respond(interaction)

    @button(label="◀️", style=discord.ButtonStyle.primary, custom_id="paginator_prev")
    async def prev_button(self, interaction: discord.Interaction, btn: Button):
        if self.current_page > 0:
            self.current_page -= 1
        self._update_buttons()
        await self._respond(interaction)

    @button(label="Trang 1/1", style=discord.ButtonStyle.secondary, disabled=True, custom_id="paginator_indicator")
    async def page_indicator(self, interaction: discord.Interaction, btn: Button):
        pass

    @button(label="▶️", style=discord.ButtonStyle.primary, custom_id="paginator_next")
    async def next_button(self, interaction: discord.Interaction, btn: Button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
        self._update_buttons()
        await self._respond(interaction)

    @button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="paginator_last")
    async def last_button(self, interaction: discord.Interaction, btn: Button):
        self.current_page = self.max_pages - 1
        self._update_buttons()
        await self._respond(interaction)

    @button(label="Đóng", style=discord.ButtonStyle.danger, custom_id="paginator_close")
    async def close_button(self, interaction: discord.Interaction, btn: Button):
        self.stop()
        await interaction.message.delete()

    async def _respond(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page] if self.embeds else None
        await interaction.response.edit_message(embed=embed, view=self)
