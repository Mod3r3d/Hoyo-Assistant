"""Hỗ trợ ngôn ngữ tiếng Việt và ánh xạ thuật ngữ game Genshin & HSR."""

from typing import Dict, Any
from app.games.enums import GameType, GenshinElement, HSRElement, HSRPath, GenshinWeaponType

# Emoji biểu tượng nguyên tố & vận mệnh
ELEMENT_EMOJIS = {
    # Genshin
    "Pyro": "🔥",
    "Hydro": "💧",
    "Anemo": "🌪️",
    "Electro": "⚡",
    "Dendro": "🌱",
    "Cryo": "❄️",
    "Geo": "🪨",
    # HSR
    "Physical": "⚔️",
    "Fire": "🔥",
    "Ice": "❄️",
    "Lightning": "⚡",
    "Wind": "🌪️",
    "Quantum": "🌌",
    "Imaginary": "✨",
}

# Ánh xạ tên thuộc tính (Stats) sang Tiếng Việt
STAT_NAMES_VI: Dict[str, str] = {
    # Base
    "HP": "HP",
    "BASE_HP": "HP Cơ Bản",
    "FIGHT_PROP_BASE_HP": "HP Cơ Bản",
    "FIGHT_PROP_HP": "HP",
    "FIGHT_PROP_HP_PERCENT": "HP %",
    "HP_PERCENT": "HP %",

    "ATTACK": "Tấn Công",
    "BASE_ATTACK": "Tấn Công Cơ Bản",
    "FIGHT_PROP_BASE_ATTACK": "Tấn Công Cơ Bản",
    "FIGHT_PROP_ATTACK": "Tấn Công",
    "FIGHT_PROP_ATTACK_PERCENT": "Tấn Công %",
    "ATK": "Tấn Công",
    "ATK_PERCENT": "Tấn Công %",

    "DEFENSE": "Phòng Ngự",
    "BASE_DEFENSE": "Phòng Ngự Cơ Bản",
    "FIGHT_PROP_BASE_DEFENSE": "Phòng Ngự Cơ Bản",
    "FIGHT_PROP_DEFENSE": "Phòng Ngự",
    "FIGHT_PROP_DEFENSE_PERCENT": "Phòng Ngự %",
    "DEF": "Phòng Ngự",
    "DEF_PERCENT": "Phòng Ngự %",

    # Crit
    "CRIT_RATE": "Tỷ Lệ Bạo Kích",
    "FIGHT_PROP_CRITICAL": "Tỷ Lệ Bạo Kích",
    "CRIT_DMG": "Sát Thương Bạo Kích",
    "FIGHT_PROP_CRITICAL_HURT": "ST Bạo Kích",

    # Energy & Mastery
    "ENERGY_RECHARGE": "Hiệu Quả Nạp NT",
    "FIGHT_PROP_CHARGE_EFFICIENCY": "Hiệu Quả Nạp NT",
    "ELEMENTAL_MASTERY": "Tinh Thông Nguyên Tố",
    "FIGHT_PROP_ELEMENT_MASTERY": "Tinh Thông NT",
    "HEALING_BONUS": "Tăng Trị Liệu",
    "FIGHT_PROP_HEAL_ADD": "Tăng Trị Liệu",

    # DMG Bonus Genshin
    "FIGHT_PROP_PHYSICAL_ADD_HURT": "Tăng ST Vật Lý",
    "FIGHT_PROP_FIRE_ADD_HURT": "Tăng ST Hỏa",
    "FIGHT_PROP_WATER_ADD_HURT": "Tăng ST Thủy",
    "FIGHT_PROP_WIND_ADD_HURT": "Tăng ST Phong",
    "FIGHT_PROP_ELEC_ADD_HURT": "Tăng ST Lôi",
    "FIGHT_PROP_GRASS_ADD_HURT": "Tăng ST Thảo",
    "FIGHT_PROP_ICE_ADD_HURT": "Tăng ST Băng",
    "FIGHT_PROP_ROCK_ADD_HURT": "Tăng ST Nham",

    # HSR Stats
    "SPD": "Tốc Độ",
    "SPEED": "Tốc Độ",
    "BREAK_EFFECT": "Tấn Công Kích Phá",
    "OUTGOING_HEALING": "Tăng Trị Liệu",
    "EFFECT_HIT_RATE": "Chính Xác Hiệu Ứng",
    "EFFECT_RES": "Kháng Hiệu Ứng",
    "PHYSICAL_DMG": "Tăng ST Vật Lý",
    "FIRE_DMG": "Tăng ST Hỏa",
    "ICE_DMG": "Tăng ST Băng",
    "LIGHTNING_DMG": "Tăng ST Lôi",
    "WIND_DMG": "Tăng ST Phong",
    "QUANTUM_DMG": "Tăng ST Lượng Tử",
    "IMAGINARY_DMG": "Tăng ST Số Ảo",
    "ENERGY_REGENERATION_RATE": "Hiệu Suất Hồi Năng Lượng",
}


def translate_stat(stat_key: str) -> str:
    """Chuyển đổi mã thuộc tính sang tiếng Việt thân thiện."""
    clean_key = stat_key.strip().upper()
    return STAT_NAMES_VI.get(clean_key, stat_key)


def format_stat_value(value: float, is_percent: bool = False) -> str:
    """Định dạng giá trị chỉ số hiển thị đẹp."""
    if is_percent:
        return f"{value:.1f}%"
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.1f}"


def get_element_emoji(element_name: str) -> str:
    """Lấy emoji tương ứng với nguyên tố."""
    return ELEMENT_EMOJIS.get(element_name.capitalize(), "✨")
