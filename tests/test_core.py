"""Bộ kiểm thử đơn vị tự động cho HoyoBot."""

import asyncio
import io
import unittest
from app.db.database import db
from app.db.models.account import AccountModel
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.settings import SettingsRepository
from app.db.repositories.users import UserRepository
from app.games.enums import GameType, ServerRegion
from app.games.factory import provider_factory
from app.games.genshin.build_data import get_genshin_build
from app.games.genshin.models import GenshinCharacter, GenshinProfile
from app.games.hsr.build_data import get_hsr_build
from app.render.character_card import render_character_card
from app.render.profile_card import render_profile_card
from app.services.account_service import account_service
from app.services.build_service import build_service
from app.services.search_service import search_service
from app.utils.validators import detect_server, mask_uid, validate_uid


class TestValidators(unittest.TestCase):
    def test_genshin_uid_validation(self):
        # Hợp lệ Asia (8...)
        valid, err, srv = validate_uid("812345678", GameType.GENSHIN)
        self.assertTrue(valid)
        self.assertEqual(srv, ServerRegion.ASIA)

        # Hợp lệ America (6...)
        valid, err, srv = validate_uid("600123456", GameType.GENSHIN)
        self.assertTrue(valid)
        self.assertEqual(srv, ServerRegion.AMERICA)

        # Hợp lệ Europe (7...)
        valid, err, srv = validate_uid("700123456", GameType.GENSHIN)
        self.assertTrue(valid)
        self.assertEqual(srv, ServerRegion.EUROPE)

        # Hợp lệ 10 số (18...)
        valid, err, srv = validate_uid("1800123456", GameType.GENSHIN)
        self.assertTrue(valid)
        self.assertEqual(srv, ServerRegion.ASIA)

        # Sai độ dài
        valid, err, _ = validate_uid("123", GameType.GENSHIN)
        self.assertFalse(valid)

        # Chứa chữ cái
        valid, err, _ = validate_uid("81234abcd", GameType.GENSHIN)
        self.assertFalse(valid)

    def test_hsr_uid_validation(self):
        # Hợp lệ Asia 9 số
        valid, err, srv = validate_uid("800123456", GameType.HSR)
        self.assertTrue(valid)
        self.assertEqual(srv, ServerRegion.ASIA)

        # Sai độ dài (10 số không hợp lệ trong HSR)
        valid, err, _ = validate_uid("8001234567", GameType.HSR)
        self.assertFalse(valid)

    def test_mask_uid(self):
        self.assertEqual(mask_uid(812345678, show=False), "812***678")
        self.assertEqual(mask_uid(812345678, show=True), "812345678")


class TestDatabaseAndAccounts(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await db.connect()
        await db.conn.execute("DELETE FROM accounts WHERE discord_user_id = 999888777")
        await db.conn.execute("DELETE FROM users WHERE discord_user_id = 999888777")
        await db.conn.commit()

    async def asyncTearDown(self):
        await db.conn.execute("DELETE FROM accounts WHERE discord_user_id = 999888777")
        await db.conn.execute("DELETE FROM users WHERE discord_user_id = 999888777")
        await db.conn.commit()
        await db.close()

    async def test_account_lifecycle(self):
        discord_id = 999888777

        # 1. Thêm account Genshin
        acc1, err = await account_service.add_account(
            discord_user_id=discord_id,
            game=GameType.GENSHIN,
            uid=811122233,
            nickname="MainGI",
        )
        self.assertIsNotNone(acc1)
        self.assertIsNone(err)
        self.assertTrue(acc1.is_default)

        # 2. Thêm account thứ 2 cùng game
        acc2, err = await account_service.add_account(
            discord_user_id=discord_id,
            game=GameType.GENSHIN,
            uid=822233344,
            nickname="RerollGI",
        )
        self.assertIsNotNone(acc2)
        self.assertFalse(acc2.is_default)

        # 3. Lấy default account
        default_acc = await account_service.get_default_or_first_account(discord_id, GameType.GENSHIN)
        self.assertIsNotNone(default_acc)
        self.assertEqual(default_acc.uid, 811122233)

        # 4. Đổi default sang acc2
        success = await account_service.set_default_account(discord_id, acc2.id)
        self.assertTrue(success)

        new_default = await account_service.get_default_or_first_account(discord_id, GameType.GENSHIN)
        self.assertEqual(new_default.uid, 822233344)

        # 5. Xóa account
        del_success = await account_service.remove_account(discord_id, acc2.id)
        self.assertTrue(del_success)

        remaining = await account_service.get_user_accounts(discord_id, GameType.GENSHIN)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].uid, 811122233)


class TestBuildAndSearchServices(unittest.IsolatedAsyncioTestCase):
    async def test_build_lookup(self):
        # Genshin build
        furina_build = await build_service.get_build(GameType.GENSHIN, "furina")
        self.assertIsNotNone(furina_build)
        self.assertEqual(furina_build.character_name, "Furina")
        self.assertIn("Huy Hoàng Của Lặng Lẽ", furina_build.weapons[0])

        # HSR build
        acheron_build = await build_service.get_build(GameType.HSR, "acheron")
        self.assertIsNotNone(acheron_build)
        self.assertEqual(acheron_build.character_name, "Acheron")
        self.assertEqual(acheron_build.path, "Hư Vô")

    async def test_search(self):
        genshin_res = await search_service.search(GameType.GENSHIN, "Neuvillette")
        self.assertTrue(len(genshin_res) > 0)
        self.assertEqual(genshin_res[0]["title"], "Neuvillette")

        hsr_res = await search_service.search(GameType.HSR, "Firefly")
        self.assertTrue(len(hsr_res) > 0)
        self.assertIn("Firefly", hsr_res[0]["title"])


class TestCardRenderer(unittest.IsolatedAsyncioTestCase):
    async def test_render_profile_card(self):
        profile = GenshinProfile(
            uid=812345678,
            nickname="Lumine",
            level=60,
            world_level=8,
            signature="Khám phá Teyvat",
            achievement_count=1150,
            showcase_characters=[
                GenshinCharacter(
                    id=10000089,
                    name="Furina",
                    element="Hydro",
                    rarity=5,
                    level=90,
                    constellation=2,
                ),
                GenshinCharacter(
                    id=10000087,
                    name="Neuvillette",
                    element="Hydro",
                    rarity=5,
                    level=90,
                    constellation=1,
                ),
            ],
        )

        buffer = await render_profile_card(profile, GameType.GENSHIN, show_uid=False)
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertTrue(buffer.getbuffer().nbytes > 1000)

    async def test_render_character_card(self):
        char = GenshinCharacter(
            id=10000089,
            name="Furina",
            element="Hydro",
            rarity=5,
            level=90,
            constellation=2,
            stats={
                "HP": "38,500",
                "Tỷ Lệ Bạo Kích": "72.4%",
                "ST Bạo Kích": "164.2%",
                "Hiệu Quả Nạp NT": "182.0%",
            },
        )
        buffer = await render_character_card(char, GameType.GENSHIN)
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertTrue(buffer.getbuffer().nbytes > 1000)


if __name__ == "__main__":
    unittest.main()
