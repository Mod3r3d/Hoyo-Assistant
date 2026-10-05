"""Task chạy nền tự động điểm danh hàng ngày (Daily Check-in Task)."""

from datetime import datetime
from typing import Any, Dict
from loguru import logger
from app.automation.notifications import notification_service
from app.automation.providers.hoyolab import HoYoLABCheckinProvider
from app.automation.tasks.base import AutomationTask
from app.config import settings
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    CheckinRepository,
    SessionRepository,
)
from app.games.enums import GameType


class DailyCheckinTask(AutomationTask):
    def __init__(self, game: GameType | None = None):
        name = f"daily_checkin_{game.value}" if game else "daily_checkin_all"
        super().__init__(name=name, game=game)

    async def execute(self) -> Dict[str, Any]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        accounts_to_check = await AutomationSettingsRepository.get_active_automation_accounts("checkin_enabled")

        if self.game:
            accounts_to_check = [item for item in accounts_to_check if item[0].game == self.game]

        total = len(accounts_to_check)
        success_count = 0
        already_count = 0
        failed_count = 0

        logger.info(f"[{self.name}] Tìm thấy {total} tài khoản cần điểm danh ngày {today_str}")

        for acc, auto_set, sess in accounts_to_check:
            # 1. Kiểm tra xem hôm nay đã điểm danh chưa
            if await CheckinRepository.has_checked_in_today(acc.id, today_str):
                already_count += 1
                continue

            # 2. Xử lý chế độ Dry Run
            if settings.AUTOMATION_MODE == "dry-run":
                logger.info(f"[DRY RUN] Giả lập điểm danh cho {acc.nickname or acc.uid} ({acc.game.display_name})")
                await CheckinRepository.record_execution(
                    account_id=acc.id,
                    game=acc.game,
                    run_date=today_str,
                    status="SUCCESS",
                    reward_summary="[DRY-RUN] Giả lập nhận thưởng",
                )
                success_count += 1
                continue

            # 3. Giải mã cookie
            cookie = await SessionRepository.get_decrypted_cookie(sess)
            if not cookie:
                await SessionRepository.update_status(sess.id, "INVALID")
                failed_count += 1
                continue

            # 4. Thực hiện gọi HoYoLAB API
            status, reward_summary, error_code = await HoYoLABCheckinProvider.perform_checkin(acc.game, cookie)

            # 5. Lưu kết quả thực thi
            await CheckinRepository.record_execution(
                account_id=acc.id,
                game=acc.game,
                run_date=today_str,
                status=status,
                reward_summary=reward_summary,
                error_code=error_code,
            )

            # 6. Xử lý thông báo và cập nhật phiên đăng nhập
            if status in ("SUCCESS", "ALREADY_CHECKED"):
                success_count += 1
                if auto_set.notify_mode == "ALL":
                    await notification_service.notify_user(
                        discord_user_id=acc.discord_user_id,
                        title=f"✅ Điểm Danh Thành Công — {acc.game.display_name}",
                        description=f"Tài khoản **{acc.nickname or acc.uid}** (UID: `{acc.uid}`)\nPhần thưởng: {reward_summary or 'Đã nhận quà'}",
                        color=settings.SUCCESS_COLOR,
                        channel_id=auto_set.notify_channel_id,
                    )
            elif status == "AUTH_REQUIRED":
                failed_count += 1
                await SessionRepository.update_status(sess.id, "EXPIRED")
                # Thông báo khẩn cấp vì cần cookie mới
                await notification_service.notify_user(
                    discord_user_id=acc.discord_user_id,
                    title=f"⚠️ Phiên Đăng Nhập Hết Hạn — {acc.game.display_name}",
                    description=(
                        f"Phiên điểm danh tự động của tài khoản **{acc.nickname or acc.uid}** (UID: `{acc.uid}`) đã hết hạn.\n"
                        f"👉 Vui lòng dùng lệnh `/auto session add` để cập nhật lại Cookie HoYoLAB mới."
                    ),
                    color=settings.ERROR_COLOR,
                    channel_id=auto_set.notify_channel_id,
                )
            else:
                failed_count += 1
                if auto_set.notify_mode in ("ALL", "FAILURE_ONLY"):
                    await notification_service.notify_user(
                        discord_user_id=acc.discord_user_id,
                        title=f"❌ Điểm Danh Thất Bại — {acc.game.display_name}",
                        description=f"Tài khoản **{acc.nickname or acc.uid}** (UID: `{acc.uid}`)\nNguyên nhân: {error_code or 'Lỗi không xác định'}",
                        color=settings.ERROR_COLOR,
                        channel_id=auto_set.notify_channel_id,
                    )

        msg = f"Hoàn thành điểm danh: {success_count} thành công, {already_count} đã điểm danh trước đó, {failed_count} lỗi."
        return {
            "status": "SUCCESS" if failed_count == 0 else "PARTIAL_SUCCESS",
            "message": msg,
            "total": total,
            "success": success_count,
            "already": already_count,
            "failed": failed_count,
        }
