"""Trình quản lý lịch trình và điều phối tác vụ tự động hóa (AutomationManager)."""

import asyncio
from typing import Any, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from app.automation.tasks.checkin_task import DailyCheckinTask
from app.automation.tasks.giftcode_tasks import GiftcodeDiscoveryTask, GiftcodeRedeemTask
from app.automation.tasks.mimo_accompany_tasks import AccompanyTask, MimoTask
from app.automation.tasks.web_event_task import WebEventMonitorTask
from app.config import settings


class AutomationManager:
    def __init__(self):
        self.scheduler: AsyncIOScheduler | None = None
        self._running = False
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_lock(self, task_name: str) -> asyncio.Lock:
        if task_name not in self._locks:
            self._locks[task_name] = asyncio.Lock()
        return self._locks[task_name]

    async def _safe_run_task(self, task):
        lock = self._get_lock(task.name)
        if lock.locked():
            logger.warning(f"[Scheduler] Tác vụ {task.name} đang chạy, bỏ qua lần kích hoạt này để tránh chồng lấn.")
            return

        async with lock:
            await task.run()

    def start(self):
        """Khởi động bộ lập lịch APScheduler."""
        if not settings.AUTOMATION_ENABLED:
            logger.info("Automation đã bị vô hiệu hóa trong cấu hình (AUTOMATION_ENABLED=False).")
            return

        if self._running:
            return

        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)

        # 1. Điểm danh hàng ngày (00:05 sáng mỗi ngày)
        checkin_task = DailyCheckinTask()
        self.scheduler.add_job(
            self._safe_run_task,
            CronTrigger(hour=settings.CHECKIN_CRON_HOUR, minute=settings.CHECKIN_CRON_MINUTE, timezone=settings.TIMEZONE),
            args=[checkin_task],
            id="job_daily_checkin",
            name="Điểm Danh Hàng Ngày HoYoLAB",
            jitter=60,
            replace_existing=True,
        )

        # 2. Quét & Redeem Giftcode theo chu kỳ (mặc định mỗi 60 phút)
        discovery_task = GiftcodeDiscoveryTask()
        redeem_task = GiftcodeRedeemTask()

        async def _run_giftcode_pipeline():
            await self._safe_run_task(discovery_task)
            await self._safe_run_task(redeem_task)

        self.scheduler.add_job(
            _run_giftcode_pipeline,
            IntervalTrigger(minutes=settings.GIFTCODE_SCAN_INTERVAL_MINUTES),
            id="job_giftcode_pipeline",
            name="Quét & Tự Động Đổi Giftcode",
            jitter=30,
            replace_existing=True,
        )

        # 3. Nhiệm vụ Mimo & Accompany theo chu kỳ
        mimo_task = MimoTask()
        accompany_task = AccompanyTask()

        async def _run_mimo_accompany_pipeline():
            await self._safe_run_task(mimo_task)
            await self._safe_run_task(accompany_task)

        self.scheduler.add_job(
            _run_mimo_accompany_pipeline,
            IntervalTrigger(minutes=settings.MIMO_SCAN_INTERVAL_MINUTES),
            id="job_mimo_accompany",
            name="Nhiệm Vụ Mimo & Đồng Hành",
            jitter=30,
            replace_existing=True,
        )

        # 4. Quét Sự Kiện Web mới (mặc định mỗi 120 phút)
        web_event_task = WebEventMonitorTask()
        self.scheduler.add_job(
            self._safe_run_task,
            IntervalTrigger(minutes=settings.WEB_EVENT_SCAN_INTERVAL_MINUTES),
            args=[web_event_task],
            id="job_web_events",
            name="Theo Dõi Sự Kiện Web Mới",
            jitter=45,
            replace_existing=True,
        )

        self.scheduler.start()
        self._running = True
        logger.info(f"Đã kích hoạt Background Scheduler (Chế độ: {settings.AUTOMATION_MODE}, Múi giờ: {settings.TIMEZONE})")

    def stop(self):
        """Dừng bộ lập lịch an toàn."""
        if self.scheduler and self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("Đã dừng Background Scheduler thành công.")

    async def run_manually(self, task_name: str, game_filter: Optional[str] = None) -> Dict[str, Any]:
        """Kích hoạt chạy ngay lập tức một tác vụ cụ thể."""
        task_map = {
            "checkin": DailyCheckinTask(),
            "giftcode_discovery": GiftcodeDiscoveryTask(),
            "giftcode_redeem": GiftcodeRedeemTask(),
            "mimo": MimoTask(),
            "accompany": AccompanyTask(),
            "events": WebEventMonitorTask(),
        }

        task = task_map.get(task_name)
        if not task:
            return {"status": "FAILED", "message": f"Không tìm thấy tác vụ mang tên: {task_name}"}

        lock = self._get_lock(task.name)
        async with lock:
            return await task.run()


automation_manager = AutomationManager()
