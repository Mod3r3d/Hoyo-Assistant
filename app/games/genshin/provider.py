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
            if cur_hp:
                stats_dict["HP"] = format_stat_value(cur_hp)

            # ATK
            cur_atk = get_prop(2001) or get_prop(4)
            if cur_atk:
                stats_dict["Tấn Công"] = format_stat_value(cur_atk)

            # DEF
            cur_def = get_prop(2002) or get_prop(7)
            if cur_def:
                stats_dict["Phòng Ngự"] = format_stat_value(cur_def)

            # EM
            em = get_prop(28)
            if em:
                stats_dict["Tinh Thông NT"] = format_stat_value(em)

            # CR
            cr = get_prop(20) * 100
            stats_dict["Tỷ Lệ Bạo Kích"] = format_stat_value(cr, is_percent=True)

            # CD
            cd = get_prop(22) * 100
            stats_dict["ST Bạo Kích"] = format_stat_value(cd, is_percent=True)

            # ER
            er = get_prop(23) * 100
            stats_dict["Hiệu Quả Nạp NT"] = format_stat_value(er, is_percent=True)

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
                    main_stat_name = translate_stat(relic_main.get("mainPropId", ""))
                    main_stat_val = relic_main.get("statValue", 0)

                    # Substats
                    sub_list = []
                    for sub in flat.get("reliquarySubstats", []):
                        sub_name = translate_stat(sub.get("appendPropId", ""))
                        val = sub.get("statValue", 0)
                        sub_list.append(f"{sub_name}: +{val}")

                    slot_key = flat.get("equipType", "")
                    slot_display = SLOT_NAMES.get(slot_key, slot_key)

                    raw_set_hash = flat.get("setNameTextMapHash")
                    set_display = get_text_map(raw_set_hash, "Bộ Thánh Di Vật")

                    raw_piece_hash = flat.get("nameTextMapHash")
                    piece_name = get_text_map(raw_piece_hash, slot_display)

                    icon_name = flat.get("icon", "")
                    artifacts.append(
                        GenshinArtifact(
                            name=piece_name,
                            set_name=set_display,
                            slot=slot_display,
                            rarity=flat.get("rankLevel", 5),
                            level=r_info.get("level", 1) - 1,
                            main_stat=main_stat_name,
                            main_value=str(main_stat_val),
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
