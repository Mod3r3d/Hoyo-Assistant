"""Task theo dõi và phát hiện Sự Kiện Web mới."""

from typing import Any, Dict
from loguru import logger
from app.automation.notifications import notification_service
from app.automation.providers.web_events import WebEventProvider
from app.automation.tasks.base import AutomationTask
from app.config import settings
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    WebEventRepository,
)
from app.games.enums import GameType


class WebEventMonitorTask(AutomationTask):
    def __init__(self):
        super().__init__(name="web_event_monitor")

    async def execute(self) -> Dict[str, Any]:
        total_scanned = 0
        new_events_count = 0

        for game in (GameType.GENSHIN, GameType.HSR):
            events = await WebEventProvider.fetch_active_web_events(game)
            for ev in events:
                total_scanned += 1
                model, is_new = await WebEventRepository.upsert_event(
                    external_id=ev["external_id"],
                    game=game,
                    title=ev["title"],
                    url=ev["url"],
                    banner_url=ev.get("banner_url"),
                )

                if is_new:
                    new_events_count += 1
                    logger.info(f"[{self.name}] Phát hiện sự kiện Web mới: {model.title} ({game.display_name})")

                    # Gửi thông báo đến những người dùng đăng ký nhận tin tức sự kiện
                    accounts = await AutomationSettingsRepository.get_active_automation_accounts("event_notify_enabled")
                    notified_users = set()

                    for acc, auto_set, _ in accounts:
                        if acc.game == game and acc.discord_user_id not in notified_users:
                            notified_users.add(acc.discord_user_id)
                            await notification_service.notify_user(
                                discord_user_id=acc.discord_user_id,
                                title=f"🎉 Sự Kiện Web Mới: {model.title}",
                                description=(
                                    f"Tựa game: **{game.display_name}**\n"
                                    f"Tham gia sự kiện ngay để nhận Nguyên Thạch/Ngọc Ánh Sao và vật phẩm độc quyền!\n\n"
                                    f"🔗 [Nhấn vào đây để mở Sự Kiện Web]({model.url})"
                                ),
                                color=settings.PRIMARY_COLOR,
                                channel_id=auto_set.notify_channel_id,
                            )

        return {
            "status": "SUCCESS",
            "message": f"Quét {total_scanned} sự kiện web, phát hiện {new_events_count} sự kiện mới.",
            "total_scanned": total_scanned,
            "new_events": new_events_count,
        }
