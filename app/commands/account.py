"""Nhóm lệnh /account quản lý tài khoản game của người dùng."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.games.enums import GameType
from app.services.account_service import account_service
from app.ui.common.account_select import AccountSelectView, ConfirmationView


class AccountCommands(commands.GroupCog, group_name="account"):
    """Quản lý danh sách tài khoản Genshin Impact và Honkai: Star Rail đã liên kết."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Liên kết tài khoản game mới (Genshin hoặc Star Rail)")
    @app_commands.describe(
        game="Chọn tựa game bạn muốn liên kết",
        uid="UID trong game của bạn (9 hoặc 10 chữ số)",
        nickname="Biệt danh gợi nhớ cho tài khoản này (không bắt buộc)",
    )
    @app_commands.choices(
        game=[
            app_commands.Choice(name="Genshin Impact", value=GameType.GENSHIN.value),
            app_commands.Choice(name="Honkai: Star Rail", value=GameType.HSR.value),
        ]
    )
    async def add_account(
        self,
        interaction: discord.Interaction,
        game: app_commands.Choice[str],
        uid: int,
        nickname: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)
        game_enum = GameType(game.value)

        account, err_msg = await account_service.add_account(
            discord_user_id=interaction.user.id,
            game=game_enum,
            uid=uid,
            nickname=nickname,
        )

        if err_msg or not account:
            await interaction.followup.send(f"❌ **Không thể thêm tài khoản:** {err_msg}")
            return

        embed = discord.Embed(
            title="✅ Liên Kết Tài Khoản Thành Công!",
            description=(
                f"**Game:** {account.game.display_name}\n"
                f"**UID:** `{account.uid}`\n"
                f"**Máy chủ:** `{account.server.value}`\n"
                f"**Biệt danh:** {account.nickname or '*Chưa đặt*'}\n"
                f"**Mặc định:** {'Có (Tự động)' if account.is_default else 'Không'}"
            ),
            color=0x2ECC71,
        )
        embed.set_footer(text="Bây giờ bạn có thể dùng lệnh /profile hoặc /characters mà không cần gõ lại UID!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="list", description="Xem danh sách toàn bộ tài khoản game bạn đã lưu")
    async def list_accounts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await account_service.get_user_accounts(interaction.user.id)

        if not accounts:
            await interaction.followup.send(
                "Bạn chưa lưu tài khoản nào! Dùng lệnh `/account add` để liên kết UID đầu tiên của bạn."
            )
            return

        embed = discord.Embed(
            title=f"📋 Danh Sách Tài Khoản Của {interaction.user.display_name}",
            description="Các tài khoản đã liên kết trong hệ thống HoyoBot:",
            color=0x3498DB,
        )

        genshin_accs = [a for a in accounts if a.game == GameType.GENSHIN]
        hsr_accs = [a for a in accounts if a.game == GameType.HSR]

        if genshin_accs:
            lines = []
            for a in genshin_accs:
                tag = " 🌟 *(Mặc định)*" if a.is_default else ""
                lines.append(f"• **{a.nickname or 'Không tên'}** — UID: `{a.uid}` ({a.server.value}){tag} `[ID: {a.id}]`")
            embed.add_field(name=f"{GameType.GENSHIN.emoji} Genshin Impact", value="\n".join(lines), inline=False)

        if hsr_accs:
            lines = []
            for a in hsr_accs:
                tag = " 🌟 *(Mặc định)*" if a.is_default else ""
                lines.append(f"• **{a.nickname or 'Không tên'}** — UID: `{a.uid}` ({a.server.value}){tag} `[ID: {a.id}]`")
            embed.add_field(name=f"{GameType.HSR.emoji} Honkai: Star Rail", value="\n".join(lines), inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="default", description="Chọn tài khoản mặc định khi tra cứu")
    async def set_default_account(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await account_service.get_user_accounts(interaction.user.id)

        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào. Hãy dùng `/account add` trước.")
            return

        async def on_select(inter: discord.Interaction, selected_id: int):
            success = await account_service.set_default_account(interaction.user.id, selected_id)
            if success:
                acc = await account_service.get_account_by_id(selected_id)
                acc_name = acc.nickname or str(acc.uid) if acc else ""
                await inter.response.edit_message(
                    content=f"✅ Đã đặt **{acc_name}** làm tài khoản mặc định cho {acc.game.display_name if acc else ''}!",
                    view=None,
                )
            else:
                await inter.response.edit_message(content="❌ Có lỗi xảy ra khi cập nhật.", view=None)

        view = AccountSelectView(interaction.user.id, accounts, on_select)
        await interaction.followup.send("Chọn tài khoản bạn muốn đặt làm mặc định:", view=view)

    @app_commands.command(name="remove", description="Xóa một tài khoản game đã lưu")
    async def remove_account(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await account_service.get_user_accounts(interaction.user.id)

        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào để xóa.")
            return

        async def on_select_to_remove(inter: discord.Interaction, selected_id: int):
            acc = await account_service.get_account_by_id(selected_id)
            if not acc:
                await inter.response.edit_message(content="❌ Không tìm thấy tài khoản.", view=None)
                return

            confirm_view = ConfirmationView(interaction.user.id)
            await inter.response.edit_message(
                content=f"⚠️ Bạn có chắc chắn muốn xóa tài khoản **{acc.nickname or acc.uid}** ({acc.game.display_name} - `{acc.uid}`)?",
                view=confirm_view,
            )
            await confirm_view.wait()

            if confirm_view.value is True:
                await account_service.remove_account(interaction.user.id, selected_id)
                await inter.edit_original_response(content=f"🗑️ Đã xóa thành công tài khoản `{acc.uid}`.", view=None)
            elif confirm_view.value is False:
                await inter.edit_original_response(content="Đã hủy thao tác xóa.", view=None)

        view = AccountSelectView(interaction.user.id, accounts, on_select_to_remove)
        await interaction.followup.send("Chọn tài khoản bạn muốn xóa khỏi hệ thống:", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AccountCommands(bot))
