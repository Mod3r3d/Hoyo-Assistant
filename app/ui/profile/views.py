"""UI View tương tác cho lệnh /profile."""

from typing import Any, List
import discord
from discord.ui import View, Select, button, Button
from app.games.enums import GameType
from app.render.character_card import render_character_card
from app.render.profile_card import render_profile_card
from app.utils.validators import mask_uid


class CharacterSelectDropdown(Select):
    def __init__(self, characters: List[Any], game: GameType):
        self.game = game
        options = []
        for i, char in enumerate(characters[:25]):
            const_val = getattr(char, "constellation", getattr(char, "eidolon", 0))
            badge = "C" if game == GameType.GENSHIN else "E"
            element = getattr(char, "element", "")
            elem_text = f"Hệ {element}" if game == GameType.GENSHIN else f"Thuộc tính {element}"
            options.append(
                discord.SelectOption(
                    label=f"{char.name} (Lv.{char.level})",
                    description=f"{badge}{const_val} • {elem_text}",
                    value=str(i),
                    emoji="⭐",
                )
            )
        super().__init__(placeholder="Chọn nhân vật để xem chi tiết...", min_values=1, max_values=1, options=options)


class ProfileView(View):
    def __init__(
        self,
        author_id: int,
        profile: Any,
        game: GameType,
        show_uid: bool = False,
        timeout: float = 120.0,
    ):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.profile = profile
        self.game = game
        self.show_uid = show_uid

        # Thêm dropdown chọn nhân vật nếu có showcase
        if self.profile.showcase_characters:
            self.char_select = CharacterSelectDropdown(self.profile.showcase_characters, game)
            self.char_select.callback = self._on_character_select
            self.add_item(self.char_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không có quyền thao tác trên menu này.", ephemeral=True)
            return False
        return True

    async def _on_character_select(self, interaction: discord.Interaction):
        idx = int(self.char_select.values[0])
        char = self.profile.showcase_characters[idx]
        await interaction.response.defer()

        # Render thẻ chi tiết nhân vật
        card_buf = await render_character_card(char, self.game)
        file = discord.File(card_buf, filename=f"character_{char.id}.png")

        embed = discord.Embed(
            title=f"Chi Tiết Nhân Vật: {char.name}",
            description=f"Hồ sơ người chơi: **{self.profile.nickname}** (UID: `{mask_uid(self.profile.uid, self.show_uid)}`)",
            color=0x5BC0BE if self.game == GameType.GENSHIN else 0x9370DB,
        )
        embed.set_image(url=f"attachment://character_{char.id}.png")
        await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    @button(label="Tạo lại ảnh Card", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def refresh_card(self, interaction: discord.Interaction, btn: Button):
        await interaction.response.defer()
        card_buf = await render_profile_card(self.profile, self.game, self.show_uid)
        file = discord.File(card_buf, filename=f"profile_{self.profile.uid}.png")

        embed = discord.Embed(
            title=f"Hồ Sơ {self.game.display_name}: {self.profile.nickname}",
            color=0x5BC0BE if self.game == GameType.GENSHIN else 0x9370DB,
        )
        embed.set_image(url=f"attachment://profile_{self.profile.uid}.png")
        await interaction.message.edit(embed=embed, attachments=[file], view=self)
