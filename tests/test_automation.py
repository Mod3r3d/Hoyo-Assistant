"""Bộ kiểm thử đơn vị cho toàn bộ hệ thống Automation v2."""

import unittest
from datetime import datetime
from app.automation.manager import automation_manager
from app.automation.tasks.checkin_task import DailyCheckinTask
from app.automation.tasks.giftcode_tasks import GiftcodeDiscoveryTask, GiftcodeRedeemTask
from app.automation.tasks.web_event_task import WebEventMonitorTask
from app.config import settings
from app.db.database import db
from app.db.repositories.accounts import AccountRepository
from app.db.repositories.automation import (
    AutomationLogRepository,
    AutomationSettingsRepository,
    CheckinRepository,
    GiftCodeRepository,
    SessionRepository,
    WebEventRepository,
)
from app.games.enums import GameType, ServerRegion
from app.security.encryption import cipher, mask_cookie


class TestSecurityAndEncryption(unittest.TestCase):
    def test_encrypt_and_decrypt(self):
        secret_cookie = "ltuid_v2=123456789; ltoken_v2=v2_abcdef1234567890; ltmid_v2=1a2b3c;"
        encrypted = cipher.encrypt(secret_cookie)
        self.assertNotEqual(secret_cookie, encrypted)

        decrypted = cipher.decrypt(encrypted)
        self.assertEqual(secret_cookie, decrypted)

    def test_mask_cookie(self):
        cookie = "ltoken_v2=v2_secret1234567890"
        masked = mask_cookie(cookie)
        self.assertTrue(masked.startswith("ltok"))
        self.assertTrue(masked.endswith("7890"))
        self.assertIn("...", masked)
        self.assertNotIn("secret123", masked)


class TestAutomationDatabase(unittest.IsolatedAsyncioTestCase):
    TEST_USER_ID = 888777666

    async def asyncSetUp(self):
        await db.connect()
        # Dọn dẹp dữ liệu test
        await db.conn.execute("DELETE FROM sessions WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM accounts WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM users WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM gift_codes WHERE code = 'TESTCODE2026'")
        await db.conn.execute("DELETE FROM giftcode_redemptions WHERE code = 'TESTCODE2026'")
        await db.conn.execute("DELETE FROM web_events WHERE external_id = 'test_event_1'")
        await db.conn.commit()

    async def asyncTearDown(self):
        await db.conn.execute("DELETE FROM sessions WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM accounts WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM users WHERE discord_user_id = ?", (self.TEST_USER_ID,))
        await db.conn.execute("DELETE FROM gift_codes WHERE code = 'TESTCODE2026'")
        await db.conn.execute("DELETE FROM giftcode_redemptions WHERE code = 'TESTCODE2026'")
        await db.conn.execute("DELETE FROM web_events WHERE external_id = 'test_event_1'")
        await db.conn.commit()
        await db.close()

    async def test_session_lifecycle(self):
        # 1. Lưu session
        raw_cookie = "ltuid=123; ltoken=abc;"
        sess = await SessionRepository.save_session(
            discord_user_id=self.TEST_USER_ID,
            game=GameType.GENSHIN,
            uid=819999999,
            raw_cookie=raw_cookie,
        )
        self.assertIsNotNone(sess)
        self.assertEqual(sess.session_status, "VALID")

        # 2. Đọc lại và giải mã
        loaded = await SessionRepository.get_session(self.TEST_USER_ID, GameType.GENSHIN, 819999999)
        self.assertIsNotNone(loaded)
        cookie_dec = await SessionRepository.get_decrypted_cookie(loaded)
        self.assertEqual(cookie_dec, raw_cookie)

        # 3. Cập nhật status
        await SessionRepository.update_status(sess.id, "EXPIRED")
        loaded_expired = await SessionRepository.get_session(self.TEST_USER_ID, GameType.GENSHIN, 819999999)
        self.assertEqual(loaded_expired.session_status, "EXPIRED")

        # 4. Xóa session
        deleted = await SessionRepository.delete_session(self.TEST_USER_ID, GameType.GENSHIN, 819999999)
        self.assertTrue(deleted)
        self.assertIsNone(await SessionRepository.get_session(self.TEST_USER_ID, GameType.GENSHIN, 819999999))

    async def test_automation_settings_and_accounts(self):
        acc = await AccountRepository.add_account(
            discord_user_id=self.TEST_USER_ID,
            game=GameType.HSR,
            uid=801111222,
            server=ServerRegion.ASIA,
            nickname="TestHSR",
        )
        # Thêm session hợp lệ
        await SessionRepository.save_session(self.TEST_USER_ID, GameType.HSR, 801111222, "dummy_cookie")

        # Tạo và cập nhật settings
        settings_model = await AutomationSettingsRepository.get_or_create(acc.id, self.TEST_USER_ID)
        self.assertTrue(settings_model.checkin_enabled)

        # Lấy danh sách tài khoản hợp lệ
        active = await AutomationSettingsRepository.get_active_automation_accounts("checkin_enabled")
        self.assertTrue(any(item[0].id == acc.id for item in active))

        # Tắt checkin
        await AutomationSettingsRepository.update_feature(acc.id, "checkin", False)
        active_after = await AutomationSettingsRepository.get_active_automation_accounts("checkin_enabled")
        self.assertFalse(any(item[0].id == acc.id for item in active_after))

    async def test_giftcode_repository(self):
        code = "TESTCODE2026"
        model1, is_new1 = await GiftCodeRepository.add_code(code, GameType.GENSHIN, "test")
        self.assertTrue(is_new1)
        self.assertEqual(model1.code, code)

        # Thêm lần 2 -> không trùng (is_new = False)
        model2, is_new2 = await GiftCodeRepository.add_code(code, GameType.GENSHIN, "test")
        self.assertFalse(is_new2)
        self.assertEqual(model2.id, model1.id)

        # Kiểm tra trạng thái đã redeem chưa
        redeemed = await GiftCodeRepository.is_redeemed(99999, model1.id)
        self.assertFalse(redeemed)

        await GiftCodeRepository.record_redemption(99999, model1.id, GameType.GENSHIN, code, "SUCCESS", "OK")
        self.assertTrue(await GiftCodeRepository.is_redeemed(99999, model1.id))

    async def test_web_event_repository(self):
        ev_id = "test_event_1"
        ev, is_new = await WebEventRepository.upsert_event(
            external_id=ev_id,
            game=GameType.GENSHIN,
            title="Sự Kiện Web Test",
            url="https://example.com/event",
        )
        self.assertTrue(is_new)
        self.assertEqual(ev.title, "Sự Kiện Web Test")

        # Lần 2 -> cập nhật, không trùng
        ev2, is_new2 = await WebEventRepository.upsert_event(
            external_id=ev_id,
            game=GameType.GENSHIN,
            title="Sự Kiện Web Test",
            url="https://example.com/event",
        )
        self.assertFalse(is_new2)


class TestAutomationTasksAndScheduler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await db.connect()
        settings.AUTOMATION_MODE = "dry-run"

    async def asyncTearDown(self):
        settings.AUTOMATION_MODE = "live"
        await db.close()

    async def test_checkin_task_dry_run(self):
        task = DailyCheckinTask(GameType.GENSHIN)
        result = await task.run()
        self.assertIn(result.get("status"), ("SUCCESS", "PARTIAL_SUCCESS"))

    async def test_giftcode_tasks_dry_run(self):
        discovery = GiftcodeDiscoveryTask()
        disc_res = await discovery.run()
        self.assertEqual(disc_res.get("status"), "SUCCESS")

        redeem = GiftcodeRedeemTask(GameType.GENSHIN)
        redeem_res = await redeem.run()
        self.assertEqual(redeem_res.get("status"), "SUCCESS")

    async def test_web_event_task(self):
        event_task = WebEventMonitorTask()
        res = await event_task.run()
        self.assertEqual(res.get("status"), "SUCCESS")

    async def test_scheduler_lifecycle(self):
        automation_manager.start()
        self.assertTrue(automation_manager._running)
        self.assertIsNotNone(automation_manager.scheduler)

        # Kiểm tra các jobs đã được đăng ký
        job_ids = [j.id for j in automation_manager.scheduler.get_jobs()]
        self.assertIn("job_daily_checkin", job_ids)
        self.assertIn("job_giftcode_pipeline", job_ids)
        self.assertIn("job_mimo_accompany", job_ids)
        self.assertIn("job_web_events", job_ids)

        automation_manager.stop()
        self.assertFalse(automation_manager._running)


if __name__ == "__main__":
    unittest.main()
