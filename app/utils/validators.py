"""Trình xác thực và nhận diện UID cho Genshin Impact và Honkai: Star Rail."""

import re
from typing import Optional, Tuple
from app.games.enums import GameType, ServerRegion


def detect_server(uid: int) -> ServerRegion:
    """Xác định máy chủ dựa trên UID."""
    uid_str = str(uid)
    if not uid_str.isdigit():
        return ServerRegion.UNKNOWN

    first_digit = uid_str[0]
    first_two = uid_str[:2]

    # Genshin 10-digit UID (e.g., 18xxxxxxx)
    if len(uid_str) == 10 and first_two == "18":
        return ServerRegion.ASIA

    if first_digit in ("1", "2"):
        return ServerRegion.CHINA
    elif first_digit == "5":
        return ServerRegion.CHINA
    elif first_digit == "6":
        return ServerRegion.AMERICA
    elif first_digit == "7":
        return ServerRegion.EUROPE
    elif first_digit == "8":
        return ServerRegion.ASIA
    elif first_digit == "9":
        return ServerRegion.TW_HK_MO

    return ServerRegion.UNKNOWN


def validate_uid(uid: int | str, game: GameType) -> Tuple[bool, Optional[str], Optional[ServerRegion]]:
    """
    Kiểm tra UID có hợp lệ với game đã chọn hay không.
    Trả về (is_valid, error_message_vi, server_region).
    """
    uid_str = str(uid).strip()

    if not uid_str.isdigit():
        return False, "UID chỉ được chứa các chữ số.", None

    uid_int = int(uid_str)
    server = detect_server(uid_int)

    if game == GameType.GENSHIN:
        # Genshin UID: 9 hoặc 10 chữ số
        if len(uid_str) not in (9, 10):
            return False, f"UID Genshin Impact phải có 9 hoặc 10 chữ số (bạn đã nhập {len(uid_str)} số).", None
        if server == ServerRegion.UNKNOWN:
            return False, "Đầu số UID không thuộc bất kỳ máy chủ Genshin nào hợp lệ.", None
        return True, None, server

    elif game == GameType.HSR:
        # Honkai: Star Rail UID: 9 chữ số
        if len(uid_str) != 9:
            return False, f"UID Honkai: Star Rail phải có đúng 9 chữ số (bạn đã nhập {len(uid_str)} số).", None
        if server == ServerRegion.UNKNOWN:
            return False, "Đầu số UID không thuộc bất kỳ máy chủ Star Rail nào hợp lệ.", None
        return True, None, server

    return False, "Tựa game không được hỗ trợ.", None


def mask_uid(uid: int | str, show: bool = False) -> str:
    """Ẩn một phần UID để bảo vệ quyền riêng tư nếu show=False."""
    uid_str = str(uid)
    if show or len(uid_str) < 5:
        return uid_str
    # Ví dụ: 812345678 -> 812***678
    prefix_len = 3
    suffix_len = 3
    mask_len = len(uid_str) - prefix_len - suffix_len
    return uid_str[:prefix_len] + ("*" * mask_len) + uid_str[-suffix_len:]
