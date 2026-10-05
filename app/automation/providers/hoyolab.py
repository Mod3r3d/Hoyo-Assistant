"""Provider kết nối API HoYoLAB cho Daily Check-in và Đổi Giftcode."""

from typing import Any, Dict, Optional, Tuple
import aiohttp
from loguru import logger
from app.games.enums import GameType


class HoYoLABCheckinProvider:
    # URL điểm danh chính thức của HoYoLAB
    GENSHIN_SIGN_URL = "https://sg-hk4e-api.hoyolab.com/event/sol/sign"
    HSR_SIGN_URL = "https://sg-public-api.hoyolab.com/event/luna/os/sign"

    GENSHIN_ACT_ID = "e202102251931481"
    HSR_ACT_ID = "e202303301540311"

    @classmethod
    def _get_headers(cls, cookie: str) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.40.1",
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "x-rpc-app_version": "2.40.1",
            "x-rpc-client_type": "5",
            "Referer": "https://act.hoyolab.com/",
            "Origin": "https://act.hoyolab.com",
        }

    @classmethod
    async def perform_checkin(cls, game: GameType, cookie: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Thực hiện điểm danh hàng ngày.
        Trả về (status, reward_summary, error_code).
        status: SUCCESS, ALREADY_CHECKED, AUTH_REQUIRED, FAILED
        """
        if game == GameType.GENSHIN:
            url = cls.GENSHIN_SIGN_URL
            act_id = cls.GENSHIN_ACT_ID
        else:
            url = cls.HSR_SIGN_URL
            act_id = cls.HSR_ACT_ID

        headers = cls._get_headers(cookie)
        payload = {"act_id": act_id}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        retcode = data.get("retcode", -1)
                        message = data.get("message", "OK")

                        if retcode == 0:
                            # Thành công
                            return "SUCCESS", "Đã nhận phần thưởng điểm danh hôm nay", None
                        elif retcode == -5003:
                            # Đã điểm danh rồi
                            return "ALREADY_CHECKED", "Hôm nay bạn đã điểm danh rồi", None
                        elif retcode in (-100, 10001, -107):
                            # Hết hạn cookie / cần đăng nhập lại
                            return "AUTH_REQUIRED", None, f"Cookie hết hạn hoặc không hợp lệ ({message})"
                        else:
                            return "FAILED", None, f"Mã lỗi {retcode}: {message}"
                    else:
                        return "FAILED", None, f"HTTP {resp.status}"

        except Exception as e:
            logger.error(f"Lỗi kết nối khi checkin {game.display_name}: {e}")
            return "FAILED", None, str(e)


class HoYoLABRedeemProvider:
    # Endpoint đổi mã giftcode chính thức
    GENSHIN_REDEEM_URL = "https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey"
    HSR_REDEEM_URL = "https://sg-hkrpg-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey"

    @classmethod
    async def redeem_code(
        cls, game: GameType, uid: int, server_region: str, code: str, cookie: str
    ) -> Tuple[str, str]:
        """
        Đổi mã Giftcode cho tài khoản.
        Trả về (status, response_message).
        status: SUCCESS, ALREADY_REDEEMED, INVALID_CODE, EXPIRED, AUTH_REQUIRED, FAILED
        """
        if game == GameType.GENSHIN:
            url = cls.GENSHIN_REDEEM_URL
            game_biz = "hk4e_global"
        else:
            url = cls.HSR_REDEEM_URL
            game_biz = "hkrpg_global"

        # Chuẩn hóa server code của Hoyoverse (os_asia, os_usa, os_euro, os_cht)
        server_map = {
            "Asia": "os_asia",
            "America": "os_usa",
            "Europe": "os_euro",
            "TW/HK/MO": "os_cht",
        }
        region_code = server_map.get(server_region, "os_asia")

        params = {
            "uid": str(uid),
            "region": region_code,
            "cdkey": code.strip().upper(),
            "game_biz": game_biz,
            "lang": "vi",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Referer": "https://genshin.hoyoverse.com/",
            "Origin": "https://genshin.hoyoverse.com",
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        retcode = data.get("retcode", -1)
                        msg = data.get("message", "OK")

                        if retcode == 0:
                            return "SUCCESS", "Đổi mã thành công! Phần thưởng đã được gửi vào hòm thư trong game."
                        elif retcode == -2017:
                            return "ALREADY_REDEEMED", "Mã này đã được đổi trên tài khoản này từ trước."
                        elif retcode == -2003:
                            return "INVALID_CODE", "Mã giftcode không tồn tại hoặc không hợp lệ."
                        elif retcode == -2016:
                            return "EXPIRED", "Mã giftcode đã hết hạn sử dụng."
                        elif retcode in (-1071, -1073, -100):
                            return "AUTH_REQUIRED", f"Lỗi xác thực tài khoản: {msg}"
                        else:
                            return "FAILED", f"Lỗi ({retcode}): {msg}"
                    else:
                        return "FAILED", f"Lỗi kết nối máy chủ HTTP {resp.status}"

        except Exception as e:
            logger.error(f"Lỗi khi redeem code {code} cho UID {uid}: {e}")
            return "FAILED", str(e)
