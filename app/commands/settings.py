"""Lệnh /settings tùy chỉnh cá nhân và /ping, /about, /help thông tin bot."""

import time
import discord
from discord import app_commands
from discord.ext import commands
from app.services.settings_service import settings_service
from app.ui.settings.views import SettingsView


class SettingsCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Tùy chỉnh cài đặt cá nhân (Hiển thị UID, Card đồ họa, Riêng tư)")
    async def settings_cmd(self, interaction: discord.Interaction):
        user_settings = await settings_service.get_settings(interaction.user.id)
        view = SettingsView(interaction.user.id, user_settings)
        await interaction.response.send_message(embed=view.build_embed(), view=view, ephemeral=True)


class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Kiểm tra độ trễ mạng và phản hồi của bot")
    async def ping_cmd(self, interaction: discord.Interaction):
        start_time = time.time()
        await interaction.response.defer(ephemeral=True)
        api_latency = round(self.bot.latency * 1000)
        roundtrip_latency = round((time.time() - start_time) * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            description=(
                f"• **Độ trễ Discord Gateway:** `{api_latency}ms`\n"
                f"• **Thời gian phản hồi lệnh:** `{roundtrip_latency}ms`"
            ),
            color=0x2ECC71,
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="about", description="Thông tin giới thiệu về HoyoBot")
    async def about_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✨ Giới Thiệu HoyoBot",
            description=(
                "**HoyoBot** là trợ thủ Discord chuyên biệt dành cho cộng đồng người chơi **Genshin Impact** và **Honkai: Star Rail**.\n\n"
                "Được thiết kế tinh gọn, hiện đại và tập trung tối đa vào tốc độ và trải nghiệm người dùng tiếng Việt."
            ),
            color=0x3498DB,
        )
        embed.add_field(
            name="🎮 Hỗ Trợ 2 Tựa Game",
            value="• **Genshin Impact**\n• **Honkai: Star Rail**",
            inline=True,
        )
        embed.add_field(
            name="🌟 Tính Năng Nổi Bật",
            value="• Quản lý nhiều tài khoản UID\n• Tra cứu hồ sơ & tủ nhân vật\n• Đồ họa thẻ Profile/Character Card\n• Hướng dẫn build vũ khí/di vật\n• Tra cứu sự kiện & bách khoa",
            inline=True,
        )
        embed.set_footer(text="Phát triển bằng Python, discord.py & Pillow.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="help", description="Xem hướng dẫn sử dụng các lệnh của HoyoBot")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 Danh Sách Lệnh HoyoBot",
            description="Tất cả các lệnh đều sử dụng hệ thống Slash Command (`/`):",
            color=0x3498DB,
        )
        embed.add_field(
            name="👤 Quản Lý Tài Khoản (`/account`)",
            value=(
                "`/account add` — Liên kết UID Genshin hoặc Star Rail\n"
                "`/account list` — Xem danh sách tài khoản đã liên kết\n"
                "`/account default` — Đặt tài khoản mặc định\n"
                "`/account remove` — Xóa tài khoản đã lưu"
            ),
            inline=False,
        )
        embed.add_field(
            name="📊 Tra Cứu Hồ Sơ (`/profile`)",
            value=(
                "`/profile genshin [uid] [user]` — Xem hồ sơ & card Genshin\n"
                "`/profile hsr [uid] [user]` — Xem hồ sơ & card Star Rail"
            ),
            inline=False,
        )
        embed.add_field(
            name="⚔️ Tủ Trưng Bày Nhân Vật (`/characters`)",
            value=(
                "`/characters genshin [uid] [user]` — Chi tiết nhân vật Genshin\n"
                "`/characters hsr [uid] [user]` — Chi tiết nhân vật Star Rail"
            ),
            inline=False,
        )
        embed.add_field(
            name="📚 Hướng Dẫn Build (`/build`)",
            value=(
                "`/build genshin <nhân vật>` — Gợi ý vũ khí, TDV, chỉ số Genshin\n"
                "`/build hsr <nhân vật>` — Gợi ý nón ánh sáng, di vật Star Rail"
            ),
            inline=False,
        )
        embed.add_field(
            name="🤖 Tự Động Hóa",
            value=(
                "`/auto status` — Bảng điều khiển trung tâm tự động hóa\n"
                "`/auto toggle` — Bật/tắt điểm danh, đổi code, mimo, sự kiện\n"
                "`/auto session_add` — Nhập Cookie HoYoLAB an toàn (mã hóa)\n"
                "`/auto run <tác vụ>` — Kích hoạt thủ công chạy tác vụ ngay\n"
                "`/checkin now` & `/checkin status` — Điểm danh tức thì\n"
                "`/giftcode list` & `/giftcode redeem` — Tra cứu & đổi Giftcode\n"
                "`/notify set` & `/notify channel` — Cấu hình kênh nhận thông báo"
            ),
            inline=False,
        )
        embed.add_field(
            name="🔍 Bách Khoa & Tiện Ích",
            value=(
                "`/search genshin <từ khóa>` — Tìm kiếm dữ liệu Genshin\n"
                "`/search hsr <từ khóa>` — Tìm kiếm dữ liệu Star Rail\n"
                "`/events genshin` & `/events hsr` — Xem sự kiện đang mở\n"
                "`/settings` — Cài đặt hiển thị & riêng tư\n"
                "`/ping` & `/about` — Kiểm tra kết nối & thông tin bot"
            ),
            inline=False,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCommand(bot))
    await bot.add_cog(GeneralCommands(bot))
