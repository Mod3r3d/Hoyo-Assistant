"""Genshin Impact Game Provider triển khai GameProvider Protocol."""

from typing import Any, Dict, List, Optional
from loguru import logger
from app.games.base import GameProvider, ProfilePrivateError, PlayerNotFoundError
from app.games.enums import GameType
from app.games.genshin.constants import (
    GENSHIN_CHARACTERS,
    FIGHT_PROP_MAP,
    ELEMENT_COLORS,
)
from app.games.genshin.models import (
    GenshinProfile,
    GenshinCharacter,
    GenshinWeapon,
    GenshinArtifact,
    GenshinBuild,
)
from app.games.genshin.build_data import get_genshin_build
from app.integrations.enka_client import enka_client
from app.utils.localization import translate_stat, format_stat_value
import json
import re
from pathlib import Path

LOC_VI_PATH = Path(__file__).parent / "loc_vi.json"
LOC_VI: Dict[str, str] = {}
if LOC_VI_PATH.exists():
    try:
        with open(LOC_VI_PATH, "r", encoding="utf-8") as f:
            LOC_VI = json.load(f)
    except Exception:
        pass


def get_text_map(hash_id: Any, default: str = "") -> str:
    """Tra cứu tên tiếng Việt từ hash của Enka/Genshin."""
    if not hash_id:
        return default
    return LOC_VI.get(str(hash_id), default)


SLOT_NAMES: Dict[str, str] = {
    "EQUIP_BRACER": "Hoa Sự Sống",
    "EQUIP_NECKLACE": "Lông Vũ Tử Vong",
    "EQUIP_SHOES": "Cát Thời Gian",
    "EQUIP_RING": "Ly Không Gian",
    "EQUIP_DRESS": "Nón Lý Trí",
}

GENSHIN_RELIC_SETS: Dict[str, str] = {
    "15001": "Lễ Bế Mạc Của Giác Đấu Sĩ",
    "15002": "Đoàn Hát Lang Thang Đại Lục",
    "15003": "Đoàn Hát Lang Thang Đại Lục",
    "15005": "Nghi Thức Tông Thất Cổ",
    "15006": "Kỵ Sĩ Đạo Nhuốm Máu",
    "15007": "Thiếu Nữ Đáng Yêu",
    "15008": "Bóng Hình Của Gió",
    "15009": "Phiến Đá Lâu Đời",
    "15010": "Sao Băng Bay Ngược",
    "15011": "Diệm Liệt Ma Nữ Cháy Rực",
    "15012": "Hiền Giả Bốc Lửa",
    "15013": "Dũng Sĩ Băng Giá",
    "15014": "Trầm Luân Giữa Tâm Hải",
    "15015": "Thiên Nham Vững Chắc",
    "15016": "Lửa Trắng Xám",
    "15017": "Dòng Hồi Ức Bất Tận",
    "15018": "Giấc Mộng Phù Hoa",
    "15019": "Xà Cừ Đại Dương",
    "15020": "Dấu Ấn Ngăn Cách",
    "15021": "Tử Sa Chìm Đắm",
    "15022": "Dư Âm Tế Lễ",
    "15023": "Ký Ức Rừng Sâu",
    "15024": "Giấc Mộng Hoàng Kim",
    "15025": "Sử Ký Đình Cát",
    "15026": "Đóa Hoa Trang Viên Đánh Mất",
    "15027": "Giấc Mộng Thủy Tiên",
    "15028": "Vầng Sáng Vourukasha",
    "15029": "Thợ Săn Marechaussee",
    "15030": "Đoàn Kịch Hoàng Kim",
    "15031": "Bài Ca Ngày Cũ",
    "15032": "Tiếng Thì Thầm Trong Rừng Vang",
    "15033": "Mảnh Ảo Tưởng Hài Hòa",
    "15034": "Ảo Tưởng Chưa Hoàn Thành",
    "15035": "Bí Điển Dũng Sĩ Tro Tàn",
    "15036": "Mật Mã Hắc Diệu",
    "14001": "Giáo Quan",
    "14002": "Kẻ Lưu Đày",
    "14003": "Học Sĩ",
    "14004": "Thiếu Nữ Đáng Yêu",
    "10003": "Cuồng Chiến",
}


def get_genshin_icon_url(char_id: int) -> str:
    """Tạo URL ảnh đại diện cho nhân vật Genshin từ Enka CDN."""
    meta = GENSHIN_CHARACTERS.get(char_id)
    if meta and meta.get("icon_name"):
        return f"https://enka.network/ui/{meta['icon_name']}.png"
    return f"https://enka.network/ui/UI_AvatarIcon_{char_id}.png"


class GenshinProvider(GameProvider):
    @property
    def game_type(self) -> GameType:
        return GameType.GENSHIN

    async def get_profile(self, uid: int) -> GenshinProfile:
        """Lấy thông tin tổng quan hồ sơ người chơi Genshin từ Enka."""
        raw_data = await enka_client.fetch_genshin(uid)
        player_info = raw_data.get("playerInfo", {})

        if not player_info:
            raise PlayerNotFoundError(uid, GameType.GENSHIN)

        characters = await self.get_characters(uid)

        # Avatar icon
        profile_pic = player_info.get("profilePicture", {})
        avatar_id = profile_pic.get("avatarId")
        avatar_url = ""
        if avatar_id:
            avatar_url = get_genshin_icon_url(avatar_id)

        return GenshinProfile(
            uid=uid,
            nickname=player_info.get("nickname", f"Traveler {uid}"),
            level=player_info.get("level", 1),
            world_level=player_info.get("worldLevel", 0),
            signature=player_info.get("signature", ""),
            achievement_count=player_info.get("finishAchievementNum", 0),
            abyss_floor=player_info.get("towerFloorIndex", 0),
            abyss_chamber=player_info.get("towerLevelIndex", 0),
            avatar_url=avatar_url,
            showcase_characters=characters,
        )

    async def get_characters(self, uid: int) -> List[GenshinCharacter]:
        """Lấy chi tiết các nhân vật trong tủ trưng bày của người chơi."""
        raw_data = await enka_client.fetch_genshin(uid)
        avatar_list = raw_data.get("avatarInfoList", [])

        if not avatar_list:
            # Nếu có playerInfo nhưng avatarInfoList rỗng -> profile bị ẩn showcase
            player_info = raw_data.get("playerInfo", {})
            if player_info and not player_info.get("showAvatarInfoList"):
                raise ProfilePrivateError(uid)
            return []

        results: List[GenshinCharacter] = []

        for raw_char in avatar_list:
            char_id = raw_char.get("avatarId", 0)
            meta = GENSHIN_CHARACTERS.get(char_id, {
                "name": f"Nhân vật #{char_id}",
                "element": "None",
                "rarity": 4,
            })

            # Constellation: đếm số talentIdList
            constellation = len(raw_char.get("talentIdList", []))

            # Level
            prop_map = raw_char.get("propMap", {})
            level = int(prop_map.get("4001", {}).get("val", 1))

            # Stats (HP, ATK, DEF, Crit Rate, Crit DMG, ER, EM)
            fight_props = raw_char.get("fightPropMap", {})
            stats_dict: Dict[str, str] = {}

            def get_prop(prop_id: int) -> float:
                return float(fight_props.get(str(prop_id), fight_props.get(prop_id, 0)) or 0)

            # HP
            cur_hp = get_prop(2000) or get_prop(1)
            stats_dict["HP"] = f"{int(round(cur_hp)):,}"

            # Tấn Công
            cur_atk = get_prop(2001) or get_prop(4)
            stats_dict["Tấn Công"] = f"{int(round(cur_atk)):,}"

            # Phòng Ngự
            cur_def = get_prop(2002) or get_prop(7)
            stats_dict["Phòng Ngự"] = f"{int(round(cur_def)):,}"

            # Tinh Thông NT (Luôn hiển thị kể cả = 0)
            em = get_prop(28)
            stats_dict["Tinh Thông NT"] = f"{int(round(em)):,}"

            # CR
            cr = get_prop(20) * 100
            stats_dict["Tỷ Lệ Bạo Kích"] = f"{cr:.1f}%"

            # CD
            cd = get_prop(22) * 100
            stats_dict["ST Bạo Kích"] = f"{cd:.1f}%"

            # ER
            er = get_prop(23) * 100
            stats_dict["Hiệu Quả Nạp NT"] = f"{er:.1f}%"

            # Năng Lượng NT (Chi phí Kỹ Năng Nộ / Burst Cost)
            burst_costs = [get_prop(p) for p in range(70, 79)]
            energy_cost = int(round(max(burst_costs))) if burst_costs else 0
            if energy_cost > 0:
                stats_dict["Năng Lượng NT"] = str(energy_cost)

            # Sát Thương Nguyên Tố của nhân vật (Luôn hiển thị theo hệ của nhân vật)
            element_prop_map = {
                "Pyro": (40, "Tăng ST Hỏa"),
                "Electro": (41, "Tăng ST Lôi"),
                "Hydro": (42, "Tăng ST Thủy"),
                "Dendro": (43, "Tăng ST Thảo"),
                "Anemo": (44, "Tăng ST Phong"),
                "Geo": (45, "Tăng ST Nham"),
                "Cryo": (46, "Tăng ST Băng"),
            }
            char_elem = meta.get("element", "")
            primary_elem_prop, primary_elem_name = element_prop_map.get(char_elem, (None, None))
            if primary_elem_prop:
                val = get_prop(primary_elem_prop) * 100
                stats_dict[primary_elem_name] = f"{val:.1f}%"

            # Các thuộc tính sát thương khác (Vật lý hoặc nguyên tố khác nếu > 0.05%)
            elemental_props = [
                (40, "Tăng ST Hỏa"),
                (41, "Tăng ST Lôi"),
                (42, "Tăng ST Thủy"),
                (43, "Tăng ST Thảo"),
                (44, "Tăng ST Phong"),
                (45, "Tăng ST Nham"),
                (46, "Tăng ST Băng"),
                (30, "Tăng ST Vật Lý"),
            ]
            for prop_id, prop_name in elemental_props:
                if prop_name != primary_elem_name:
                    val = get_prop(prop_id) * 100
                    if val > 0.05:
                        stats_dict[prop_name] = f"{val:.1f}%"

            # Tăng Trị Liệu (Nếu có)
            heal_bonus = get_prop(26) * 100
            if heal_bonus > 0.05:
                stats_dict["Tăng Trị Liệu"] = f"{heal_bonus:.1f}%"

            # Hiệu Quả Khiên (Nếu có)
            shield_bonus = get_prop(81) * 100
            if shield_bonus > 0.05:
                stats_dict["Hiệu Quả Khiên"] = f"{shield_bonus:.1f}%"

            # Trang bị (Vũ khí & Thánh Di Vật)
            weapon: Optional[GenshinWeapon] = None
            artifacts: List[GenshinArtifact] = []

            for equip in raw_char.get("equipList", []):
                flat = equip.get("flat", {})
                item_type = flat.get("itemType")

                if item_type == "ITEM_WEAPON":
                    w_info = equip.get("weapon", {})
                    # Tinh luyện (affixMap key -> level + 1)
                    refinement = 1
                    affix_map = w_info.get("affixMap", {})
                    if affix_map:
                        refinement = next(iter(affix_map.values())) + 1

                    icon_name = flat.get("icon", "")
                    raw_w_name = flat.get("nameTextMapHash")
                    weapon_name = get_text_map(raw_w_name, "Vũ Khí")

                    weapon = GenshinWeapon(
                        name=weapon_name,
                        rarity=flat.get("rankLevel", 4),
                        level=w_info.get("level", 1),
                        promote_level=w_info.get("promoteLevel", 0),
                        refinement=refinement,
                        icon_url=f"https://enka.network/ui/{icon_name}.png" if icon_name else "",
                    )
                elif item_type == "ITEM_RELIQUARY":
                    r_info = equip.get("reliquary", {})
                    relic_main = flat.get("reliquaryMainstat", {})
                    main_prop_id = relic_main.get("mainPropId", "")
                    main_stat_name = translate_stat(main_prop_id)
                    main_stat_val = relic_main.get("statValue", 0)
                    is_percent_main = (
                        "PERCENT" in main_prop_id
                        or main_prop_id in [
                            "FIGHT_PROP_CHARGE_EFFICIENCY",
                            "FIGHT_PROP_CRITICAL",
                            "FIGHT_PROP_CRITICAL_HURT",
                            "FIGHT_PROP_HEAL_ADD",
                        ]
                        or "_ADD_HURT" in main_prop_id
                    )
                    main_val_str = f"{main_stat_val:.1f}%" if is_percent_main else f"{int(round(main_stat_val)):,}"

                    # Substats
                    sub_list = []
                    for sub in flat.get("reliquarySubstats", []):
                        prop_id = sub.get("appendPropId", "")
                        sub_name = translate_stat(prop_id)
                        val = sub.get("statValue", 0)
                        is_percent_sub = (
                            "PERCENT" in prop_id
                            or prop_id in [
                                "FIGHT_PROP_CHARGE_EFFICIENCY",
                                "FIGHT_PROP_CRITICAL",
                                "FIGHT_PROP_CRITICAL_HURT",
                                "FIGHT_PROP_HEAL_ADD",
                            ]
                            or "_ADD_HURT" in prop_id
                        )
                        val_str = f"+{val:.1f}%" if is_percent_sub else f"+{int(round(val))}"
                        sub_list.append(f"{sub_name}: {val_str}")

                    slot_key = flat.get("equipType", "")
                    slot_display = SLOT_NAMES.get(slot_key, slot_key)

                    raw_set_hash = flat.get("setNameTextMapHash")
                    set_display = get_text_map(raw_set_hash, "Bộ Thánh Di Vật")

                    icon_name = flat.get("icon", "")
                    if set_display in ["Bộ Thánh Di Vật", ""] and icon_name:
                        m = re.search(r"UI_RelicIcon_(\d+)_\d+", icon_name)
                        if m and m.group(1) in GENSHIN_RELIC_SETS:
                            set_display = GENSHIN_RELIC_SETS[m.group(1)]

                    raw_piece_hash = flat.get("nameTextMapHash")
                    piece_name = get_text_map(raw_piece_hash, slot_display)

                    artifacts.append(
                        GenshinArtifact(
                            name=piece_name,
                            set_name=set_display,
                            slot=slot_display,
                            rarity=flat.get("rankLevel", 5),
                            level=r_info.get("level", 1) - 1,
                            main_stat=main_stat_name,
                            main_value=main_val_str,
                            sub_stats=sub_list,
                            icon_url=f"https://enka.network/ui/{icon_name}.png" if icon_name else "",
                        )
                    )


            icon_url = get_genshin_icon_url(char_id)

            results.append(
                GenshinCharacter(
                    id=char_id,
                    name=meta["name"],
                    element=meta["element"],
                    rarity=meta["rarity"],
                    level=level,
                    constellation=constellation,
                    icon_url=icon_url,
                    weapon=weapon,
                    artifacts=artifacts,
                    stats=stats_dict,
                )
            )

        return results

    async def get_build(self, character_name_or_id: str) -> Optional[GenshinBuild]:
        """Lấy hướng dẫn build cho nhân vật Genshin."""
        # Thử tìm theo ID nếu là số
        if character_name_or_id.isdigit():
            meta = GENSHIN_CHARACTERS.get(int(character_name_or_id))
            if meta:
                return get_genshin_build(meta["name"])
        return get_genshin_build(character_name_or_id)

    async def search(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Tìm kiếm nhân vật hoặc vũ khí trong cơ sở dữ liệu Genshin."""
        q = query.strip().lower()
        results: List[Dict[str, Any]] = []

        # Tìm kiếm nhân vật
        for char_id, meta in GENSHIN_CHARACTERS.items():
            if q in meta["name"].lower() or q in meta["element"].lower() or q in str(char_id):
                results.append({
                    "id": char_id,
                    "title": meta["name"],
                    "category": "Nhân Vật",
                    "rarity": meta["rarity"],
                    "element": meta["element"],
                    "description": f"Nhân vật {meta['rarity']}⭐ hệ {meta['element']}",
                    "icon_url": get_genshin_icon_url(char_id),
                })

        return results[:25]

    async def get_events(self) -> List[Dict[str, Any]]:
        """Danh sách sự kiện Genshin Impact đang diễn ra."""
        # Dữ liệu sự kiện tổng hợp chính xác theo các banner & sự kiện cập nhật
        return [
            {
                "title": "Cầu Nguyện Nhân Vật: Tụ Khí Ngàn Non & Ánh Sáng Rực Rỡ",
                "type": "Cầu Nguyện",
                "status": "Đang diễn ra",
                "duration": "Bắt đầu từ phiên bản hiện tại",
                "description": "Tăng tỷ lệ cầu nguyện nhận nhân vật giới hạn 5 sao và vũ khí độc quyền!",
                "image_url": "https://enka.network/ui/UI_Gacha_A01.png",
                "link": "https://genshin.hoyoverse.com/vi/news",
            },
            {
                "title": "Sự Kiện Chủ Đề Phiên Bản: Vương Quốc Natlan",
                "type": "Sự Kiện Trò Chơi",
                "status": "Đang diễn ra",
                "duration": "Còn 14 ngày",
                "description": "Khám phá vùng đất Lửa Natlan, tham gia thử thách cùng Saurian để nhận Nguyên Thạch và Vương Miện Trí Thức.",
                "image_url": "https://enka.network/ui/UI_Activity_Default.png",
                "link": "https://genshin.hoyoverse.com/vi/news",
            },
            {
                "title": "La Hoàn Thâm Cảnh (Spiral Abyss) Kỳ Mới",
                "type": "Chiến Đấu Kỳ Hạn",
                "status": "Đang diễn ra",
                "duration": "Làm mới vào ngày 1 và 16 hàng tháng",
                "description": "Vượt tầng 9 đến 12 nhận tới 800 Nguyên Thạch và phần thưởng tài nguyên phong phú.",
                "image_url": "https://enka.network/ui/UI_Tower_Icon.png",
                "link": "https://genshin.hoyoverse.com/vi/news",
            },
        ]
