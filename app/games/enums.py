"""Các kiểu dữ liệu Enum dùng trong HoyoBot (Genshin Impact & Honkai: Star Rail)."""

from enum import Enum


class GameType(str, Enum):
    GENSHIN = "genshin"
    HSR = "hsr"

    @property
    def display_name(self) -> str:
        if self == GameType.GENSHIN:
            return "Genshin Impact"
        return "Honkai: Star Rail"

    @property
    def short_name(self) -> str:
        if self == GameType.GENSHIN:
            return "Genshin"
        return "Star Rail"

    @property
    def icon_url(self) -> str:
        if self == GameType.GENSHIN:
            return "https://enka.network/ui/UI_AvatarIcon_PlayerBoy.png"
        return "https://enka.network/ui/hsr/avatar/1001.png"


class ServerRegion(str, Enum):
    ASIA = "Asia"
    AMERICA = "America"
    EUROPE = "Europe"
    TW_HK_MO = "TW/HK/MO"
    CHINA = "China"
    UNKNOWN = "Không xác định"


class GenshinElement(str, Enum):
    PYRO = "Hỏa"
    HYDRO = "Thủy"
    ANEMO = "Phong"
    ELECTRO = "Lôi"
    DENDRO = "Thảo"
    CRYO = "Băng"
    GEO = "Nham"
    NONE = "Vô thuộc tính"


class HSRElement(str, Enum):
    PHYSICAL = "Vật Lý"
    FIRE = "Hỏa"
    ICE = "Băng"
    LIGHTNING = "Lôi"
    WIND = "Phong"
    QUANTUM = "Lượng Tử"
    IMAGINARY = "Số Ảo"
    NONE = "Vô thuộc tính"


class HSRPath(str, Enum):
    DESTRUCTION = "Hủy Diệt"
    HUNT = "Săn Bắn"
    ERUDITION = "Tri Thức"
    HARMONY = "Hòa Hợp"
    NIHILITY = "Hư Vô"
    PRESERVATION = "Bảo Hộ"
    ABUNDANCE = "Trù Phú"
    REMEMBRANCE = "Ký Ức"
    UNKNOWN = "Chưa rõ"


class GenshinWeaponType(str, Enum):
    SWORD = "Kiếm Đơn"
    CLAYMORE = "Trọng Kiếm"
    POLEARM = "Vũ Khí Cán Dài"
    BOW = "Cung"
    CATALYST = "Pháp Khí"
    UNKNOWN = "Khác"
