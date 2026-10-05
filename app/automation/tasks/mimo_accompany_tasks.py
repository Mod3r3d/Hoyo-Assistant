"""Tasks tự động hóa nhiệm vụ Mimo và Điểm danh Đồng hành (Accompany)."""

from typing import Any, Dict
from loguru import logger
from app.automation.notifications import notification_service
from app.automation.providers.mimo import AccompanyProvider, MimoProvider
from app.automation.tasks.base import AutomationTask
from app.config import settings
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    SessionRepository,
)


class MimoTask(AutomationTask):
    def __init__(self):
        super().__init__(name="mimo_automation")

    async def execute(self) -> Dict[str, Any]:
        accounts = await AutomationSettingsRepository.get_active_automation_accounts("mimo_enabled")
        completed_count = 0

        for acc, auto_set, sess in accounts:
            cookie = await SessionRepository.get_decrypted_cookie(sess)
            if not cookie:
                continue

            tasks = await MimoProvider.get_and_execute_tasks(cookie, acc.game)
            if tasks:
                completed_count += len(tasks)

        return {
            "status": "SUCCESS",
            "message": f"Đã hoàn thành {completed_count} nhiệm vụ Mimo cho {len(accounts)} tài khoản.",
            "completed": completed_count,
        }


class AccompanyTask(AutomationTask):
    def __init__(self):
        super().__init__(name="accompany_automation")

    async def execute(self) -> Dict[str, Any]:
        accounts = await AutomationSettingsRepository.get_active_automation_accounts("accompany_enabled")
        success_count = 0

        for acc, auto_set, sess in accounts:
            cookie = await SessionRepository.get_decrypted_cookie(sess)
            if not cookie:
                continue

            ok, msg = await AccompanyProvider.perform_accompany(cookie, acc.game)
            if ok:
                success_count += 1

        return {
            "status": "SUCCESS",
            "message": f"Điểm danh Đồng Hành hoàn tất cho {success_count}/{len(accounts)} tài khoản.",
            "success": success_count,
        }
