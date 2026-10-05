"""Task phát hiện Giftcode mới và Tự động Redeem cho các tài khoản."""

from typing import Any, Dict
from loguru import logger
from app.automation.notifications import notification_service
from app.automation.providers.giftcodes import GiftcodeDiscoveryProvider
from app.automation.providers.hoyolab import HoYoLABRedeemProvider
from app.automation.tasks.base import AutomationTask
from app.config import settings
from app.db.repositories.automation import (
    AutomationSettingsRepository,
    GiftCodeRepository,
    SessionRepository,
)
from app.games.enums import GameType


from app.automation.providers.giftcodes import GiftcodeAggregator


class GiftcodeDiscoveryTask(AutomationTask):
    def __init__(self):
        super().__init__(name="giftcode_discovery")
        self.aggregator = GiftcodeAggregator()

    async def execute(self) -> Dict[str, Any]:
        total_discovered = 0
        new_codes_count = 0

        for game in (GameType.GENSHIN, GameType.HSR):
            codes = await self.aggregator.collect(game)
            for c_info in codes:
                code_str = c_info.get("code")
                source = c_info.get("source", "aggregator")
                sources = ", ".join(c_info.get("sources_list", [source]))
                rewards = c_info.get("rewards")
                confidence = c_info.get("confidence", "MEDIUM")
                expires_at = c_info.get("expires_at")

                if not code_str:
                    continue
                total_discovered += 1
                model, is_new = await GiftCodeRepository.add_or_update_code(
                    code=code_str,
                    game=game,
                    source=source,
                    sources=sources,
                    rewards=rewards,
                    confidence=confidence,
                    expires_at=expires_at,
                )
                if is_new:
                    new_codes_count += 1
                    logger.info(
                        f"[{self.name}] Phát hiện mã Giftcode mới ({confidence}): {code_str} "
                        f"({game.display_name}) - Nguồn: {sources}"
                    )

        return {
            "status": "SUCCESS",
            "message": f"Quét {total_discovered} mã từ nhiều nguồn, phát hiện {new_codes_count} mã mới.",
            "total_discovered": total_discovered,
            "new_codes": new_codes_count,
        }


class GiftcodeRedeemTask(AutomationTask):
    def __init__(self, game: GameType | None = None):
        name = f"giftcode_redeem_{game.value}" if game else "giftcode_redeem_all"
        super().__init__(name=name, game=game)

    async def execute(self) -> Dict[str, Any]:
        accounts_to_redeem = await AutomationSettingsRepository.get_active_automation_accounts("redeem_enabled")
        if self.game:
            accounts_to_redeem = [item for item in accounts_to_redeem if item[0].game == self.game]

        total_redeems = 0
        success_count = 0

        for acc, auto_set, sess in accounts_to_redeem:
            active_codes = await GiftCodeRepository.get_active_codes(acc.game)
            cookie = await SessionRepository.get_decrypted_cookie(sess)
            if not cookie:
                continue

            for gift in active_codes:
                # Kiểm tra xem mã này đã từng đổi trên account này chưa
                if await GiftCodeRepository.is_redeemed(acc.id, gift.id):
                    continue

                total_redeems += 1

                if settings.AUTOMATION_MODE == "dry-run":
                    logger.info(f"[DRY RUN] Giả lập đổi mã {gift.code} cho {acc.nickname or acc.uid}")
                    await GiftCodeRepository.record_redemption(
                        account_id=acc.id,
                        gift_code_id=gift.id,
                        game=acc.game,
                        code=gift.code,
                        status="SUCCESS",
                        response_msg="[DRY-RUN] Giả lập thành công",
                    )
                    success_count += 1
                    continue

                status, msg = await HoYoLABRedeemProvider.redeem_code(
                    game=acc.game,
                    uid=acc.uid,
                    server_region=acc.server.value,
                    code=gift.code,
                    cookie=cookie,
                )

                await GiftCodeRepository.record_redemption(
                    account_id=acc.id,
                    gift_code_id=gift.id,
                    game=acc.game,
                    code=gift.code,
                    status=status,
                    response_msg=msg,
                )

                if status == "SUCCESS":
                    success_count += 1
                    if auto_set.notify_mode in ("ALL", "FAILURE_ONLY"):
                        await notification_service.notify_user(
                            discord_user_id=acc.discord_user_id,
                            title=f"🎁 Tự Động Đổi Mã Thành Công — {acc.game.display_name}",
                            description=(
                                f"Đã đổi thành công mã: **`{gift.code}`**\n"
                                f"Tài khoản: **{acc.nickname or acc.uid}** (UID: `{acc.uid}`)\n"
                                f"Vui lòng kiểm tra hòm thư trong game."
                            ),
                            color=settings.SUCCESS_COLOR,
                            channel_id=auto_set.notify_channel_id,
                        )

        return {
            "status": "SUCCESS",
            "message": f"Đã thử đổi {total_redeems} lượt mã giftcode, {success_count} thành công.",
            "total_attempts": total_redeems,
            "success": success_count,
        }
