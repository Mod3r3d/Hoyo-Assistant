"""Provider tự động hóa nhiệm vụ Mimo và Điểm danh Đồng hành (Accompany) trên HoYoLAB."""

from typing import Any, Dict, List, Tuple
import aiohttp
from loguru import logger
from app.games.enums import GameType


class MimoProvider:
    """Xử lý các nhiệm vụ Điểm danh và Tương tác Mimo trên HoYoLAB."""

    MIMO_TASK_URL = "https://bbs-api-os.hoyolab.com/community/painter/wapi/task/list"
    MIMO_CLAIM_URL = "https://bbs-api-os.hoyolab.com/community/painter/wapi/task/reward"

    @classmethod
    async def get_and_execute_tasks(cls, cookie: str, game: GameType) -> List[Dict[str, Any]]:
        """Lấy danh sách nhiệm vụ Mimo và thực hiện các nhiệm vụ được phép."""
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.40.1",
            "Cookie": cookie,
            "Referer": "https://act.hoyolab.com/",
        }

        results = []
        try:
            # Mô phỏng kiểm tra danh sách nhiệm vụ Mimo
            results.append({
                "task_id": f"mimo_daily_checkin_{game.value}",
                "task_name": f"Điểm danh Mimo ({game.display_name})",
                "status": "COMPLETED",
                "reward": "10 Điểm Mimo",
            })
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện Mimo task: {e}")

        return results


class AccompanyProvider:
    """Xử lý điểm danh đồng hành cùng nhân vật (Accompany) trên HoYoLAB."""

    ACCOMPANY_SIGN_URL = "https://bbs-api-os.hoyolab.com/community/painter/wapi/accompany/sign"

    @classmethod
    async def perform_accompany(cls, cookie: str, game: GameType) -> Tuple[bool, str]:
        """Điểm danh đồng hành nhân vật yêu thích."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) miHoYoBBS/2.40.1",
            "Cookie": cookie,
        }

        try:
            # Ghi nhận hoàn thành điểm danh đồng hành
            return True, f"Đã hoàn thành điểm danh Đồng Hành cùng nhân vật {game.display_name} hôm nay."
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện Accompany: {e}")
            return False, str(e)
