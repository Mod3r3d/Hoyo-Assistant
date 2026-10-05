"""Kiểm thử việc nạp các Cogs và Slash Commands của HoyoBot."""

import unittest
from app.bot.client import HoyoBot, EXTENSIONS
from app.db.database import db


class TestBotSetup(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await db.connect()
        self.bot = HoyoBot()

    async def asyncTearDown(self):
        await db.close()

    async def test_extensions_and_commands(self):
        # Nạp tất cả các extensions
        for ext in EXTENSIONS:
            await self.bot.load_extension(ext)

        # Lấy danh sách toàn bộ slash command trong tree
        commands = self.bot.tree.get_commands()
        cmd_names = [cmd.name for cmd in commands]

        # Kiểm tra sự hiện diện của các nhóm lệnh chính
        expected_groups = [
            "account",
            "profile",
            "characters",
            "build",
            "search",
            "events",
            "settings",
            "auto",
            "checkin",
            "giftcode",
            "notify",
            "admin",
            "ping",
            "about",
            "help",
        ]
        for eg in expected_groups:
            self.assertIn(eg, cmd_names, f"Thiếu nhóm lệnh {eg} trong command tree!")

        # Đảm bảo KHÔNG có gacha, challenge, notes, farm
        forbidden_names = ["gacha", "challenge", "notes", "farm", "reminder", "abyss"]
        for fn in forbidden_names:
            self.assertNotIn(fn, cmd_names, f"Lệnh bị cấm '{fn}' xuất hiện trong bot!")


if __name__ == "__main__":
    unittest.main()
