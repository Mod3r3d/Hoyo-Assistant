"""Nhóm lệnh /notify tùy chỉnh kênh và phương thức nhận thông báo tự động."""

from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from app.db.database import db
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import AutomationSettingsRepository


class NotifyCommands(commands.GroupCog, group_name="notify"):
    """Cài đặt kênh nhận thông báo tự động hóa (DM hoặc Kênh máy chủ)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="status", description="Xem cấu hình nhận thông báo hiện tại của bạn")
    async def notify_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        accounts = await AccountRepository.get_accounts_by_user(interaction.user.id)
        if not accounts:
            await interaction.followup.send("Bạn chưa có tài khoản nào.", ephemeral=True)
            return

        acc = accounts[0]
        auto_set = await AutomationSettingsRepository.get_or_create(acc.id, interaction.user.id)

        channel_text = f"<#{auto_set.notify_channel_id}>" if auto_set.notify_channel_id else "Tin nhắn riêng (DM)"
        mode_text = {
            "ALL": "Tất cả (Cả thành công & thất bại)",
            "FAILURE_ONLY": "Chỉ khi có lỗi hoặc hết hạn cookie",
            "NONE": "Tắt hoàn toàn thông báo",
        }.get(auto_set.notify_mode, auto_set.notify_mode)

        embed = discord.Embed(
            title="🔔 Cài Đặt Thông Báo Tự Động Hóa",
            description=(
                f"• **Chế độ thông báo:** {mode_text}\n"
                f"• **Địa chỉ nhận:** {channel_text}\n\n"
                f"Dùng `/notify set` để đổi chế độ hoặc `/notify channel` để chọn kênh nhận tin."
            ),
            color=0x3498DB,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="set", description="Thiết lập chế độ gửi thông báo tự động")
    @app_commands.describe(che_do="Mức độ thông báo mong muốn")
    @app_commands.choices(
        che_do=[
            app_commands.Choice(name="Chỉ báo khi có lỗi hoặc hết hạn cookie (Khuyên dùng)", value="FAILURE_ONLY"),
            app_commands.Choice(name="Báo tất cả (Bao gồm cả khi điểm danh/nhận quà thành công)", value="ALL"),
            app_commands.Choice(name="Không gửi thông báo (Tắt)", value="NONE"),
        ]
    )
    async def notify_set(self, interaction: discord.Interaction, che_do: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=True)
        await db.conn.execute(
            "UPDATE automation_settings SET notify_mode = ?, updated_at = CURRENT_TIMESTAMP WHERE discord_user_id = ?",
            (che_do.value, interaction.user.id),
        )
        await db.conn.commit()

        await interaction.followup.send(
            f"✅ Đã cập nhật chế độ nhận thông báo: **{che_do.name}**!",
            ephemeral=True,
        )

    @app_commands.command(name="channel", description="Chọn kênh Discord nhận thông báo (để trống để gửi qua DM)")
    @app_commands.describe(kenh="Kênh văn bản bạn muốn bot gửi thông báo vào")
    async def notify_channel(self, interaction: discord.Interaction, kenh: Optional[discord.TextChannel] = None):
        await interaction.response.defer(ephemeral=True)
        chan_id = kenh.id if kenh else None

        await db.conn.execute(
            "UPDATE automation_settings SET notify_channel_id = ?, updated_at = CURRENT_TIMESTAMP WHERE discord_user_id = ?",
            (chan_id, interaction.user.id),
        )
        await db.conn.commit()

        dest_text = f"kênh {kenh.mention}" if kenh else "Tin nhắn riêng (DM)"
        await interaction.followup.send(
            f"✅ Đã thiết lập thông báo tự động chuyển tiếp tới **{dest_text}**.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(NotifyCommands(bot))
