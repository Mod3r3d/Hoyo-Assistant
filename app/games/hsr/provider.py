"""Honkai: Star Rail Game Provider triển khai GameProvider Protocol."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from loguru import logger
from app.games.base import GameProvider, ProfilePrivateError, PlayerNotFoundError
from app.games.enums import GameType
from app.games.hsr.constants import HSR_CHARACTERS, HSR_ELEMENT_COLORS
from app.games.hsr.models import (
    HSRProfile,
    HSRCharacter,
    HSRLightCone,
    HSRRelic,
    HSRBuild,
)
from app.games.hsr.build_data import get_hsr_build
from app.integrations.enka_client import enka_client

DATA_DIR = Path(__file__).parent / "data"


def _load_hsr_data(filename: str) -> Dict[str, Any]:
    fpath = DATA_DIR / filename
    if fpath.exists():
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.debug(f"Không thể tải HSR data {filename}: {e}")
            return {}
    return {}


LIGHT_CONES = _load_hsr_data("light_cones.json")
RELIC_SETS = _load_hsr_data("relic_sets.json")
PROPERTIES = _load_hsr_data("properties.json")
CHARACTER_PROMOTIONS = _load_hsr_data("character_promotions.json")


class StarRailProvider(GameProvider):
    @property
    def game_type(self) -> GameType:
        return GameType.HSR

    async def get_profile(self, uid: int) -> HSRProfile:
        """Lấy thông tin tổng quan hồ sơ Honkai: Star Rail từ Enka."""
        raw_data = await enka_client.fetch_hsr(uid)
        detail_info = raw_data.get("detailInfo", {})

        if not detail_info:
            raise PlayerNotFoundError(uid, GameType.HSR)

        characters = await self.get_characters(uid)

        record_info = detail_info.get("recordInfo", {})
        head_icon = detail_info.get("headIcon", 1001)
        avatar_url = f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/avatar/{head_icon}.png"

        return HSRProfile(
            uid=uid,
            nickname=detail_info.get("nickname", f"Nhà Khai Phá {uid}"),
            level=detail_info.get("level", 1),
            world_level=detail_info.get("worldLevel", 0),
            signature=detail_info.get("signature", ""),
            achievement_count=record_info.get("achievementCount", 0),
            avatar_count=record_info.get("avatarCount", 0),
            avatar_url=avatar_url,
            showcase_characters=characters,
        )

    async def get_characters(self, uid: int) -> List[HSRCharacter]:
        """Lấy chi tiết các nhân vật trong tủ trưng bày của người chơi Star Rail."""
        raw_data = await enka_client.fetch_hsr(uid)
        detail_info = raw_data.get("detailInfo", {})

        avatar_list = detail_info.get("avatarDetailList", [])
        if not avatar_list:
            if detail_info and not avatar_list:
                raise ProfilePrivateError(uid)
            return []

        results: List[HSRCharacter] = []

        slot_names = {
            1: "Đầu",
            2: "Tay",
            3: "Thân",
            4: "Chân",
            5: "Cầu Vị Diện",
            6: "Dây Liên Kết",
        }

        for raw_char in avatar_list:
            char_id = raw_char.get("avatarId", 0)
            meta = HSR_CHARACTERS.get(char_id, {
                "name": f"Nhân vật #{char_id}",
                "path": "Hư Vô",
                "element": "Vật Lý",
                "rarity": 4,
            })

            eidolon = raw_char.get("rank", 0)
            level = raw_char.get("level", 1)
            promotion = raw_char.get("promotion", 0)

            # Nón ánh sáng (Light Cone)
            equipment = raw_char.get("equipment")
            light_cone: Optional[HSRLightCone] = None
            if equipment:
                eq_id = str(equipment.get("tid", 0))
                eq_meta = LIGHT_CONES.get(eq_id, {})
                lc_name = eq_meta.get("name", f"Nón Ánh Sáng #{eq_id}")
                lc_rarity = eq_meta.get("rarity", equipment.get("rank", 4))
                icon_url = f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/light_cone/{eq_id}.png" if eq_id else ""
                light_cone = HSRLightCone(
                    name=lc_name,
                    rarity=lc_rarity,
                    level=equipment.get("level", 1),
                    promotion=equipment.get("promotion", 0),
                    superimposition=equipment.get("rank", 1),
                    icon_url=icon_url,
                )

            # Di vật & Phụ kiện vị diện (Relics - 6 món)
            relics: List[HSRRelic] = []
            for r in raw_char.get("relicList", []):
                relic_id = r.get("tid", 0)
                relic_type = r.get("type", 1)
                slot_name = slot_names.get(relic_type, "Di Vật")

                set_id = str(r.get("_flat", {}).get("setID", "") or (relic_id // 100) or (relic_id // 10))
                set_meta = RELIC_SETS.get(set_id, {})
                set_name = set_meta.get("name", f"Bộ #{set_id}")

                flat_props = r.get("_flat", {}).get("props", [])
                main_prop = flat_props[0] if flat_props else {}
                main_type = main_prop.get("type", "")
                main_meta = PROPERTIES.get(main_type, {})
                main_name = main_meta.get("name", main_type)
                main_val = main_prop.get("value", 0)
                is_main_percent = main_meta.get("percent", False) or any(
                    k in main_type for k in ["Critical", "Ratio", "Resistance", "Probability"]
                )
                if is_main_percent:
                    main_str = f"{main_val * 100:.1f}%"
                else:
                    main_str = f"{int(round(main_val))}" if main_val >= 1 else f"{main_val}"

                subs: List[str] = []
                for sub in flat_props[1:]:
                    stype = sub.get("type", "")
                    smeta = PROPERTIES.get(stype, {})
                    sval = sub.get("value", 0)
                    sname = smeta.get("name", stype)
                    is_sub_percent = smeta.get("percent", False) or any(
                        k in stype for k in ["Critical", "Ratio", "Resistance", "Probability"]
                    )
                    if is_sub_percent:
                        sstr = f"{sname}: +{sval * 100:.1f}%"
                    elif "Speed" in stype:
                        sstr = f"{sname}: +{sval:.1f}" if not float(sval).is_integer() else f"{sname}: +{int(sval)}"
                    else:
                        sstr = f"{sname}: +{int(round(sval))}"
                    subs.append(sstr)

                icon_url = f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/relic/{set_id}.png"

                relics.append(
                    HSRRelic(
                        name=slot_name,
                        set_name=set_name,
                        slot=slot_name,
                        rarity=5,
                        level=r.get("level", 0),
                        main_stat=main_name,
                        main_value=main_str,
                        sub_stats=subs,
                        icon_url=icon_url,
                    )
                )

            # Tính toán chỉ số chiến đấu hoàn chỉnh
            char_promo = CHARACTER_PROMOTIONS.get(str(char_id), {}).get("values", [])
            promo_idx = min(promotion, len(char_promo) - 1) if char_promo else 0
            c_vals = char_promo[promo_idx] if char_promo else {}

            base_hp = (c_vals.get("hp", {}).get("base", 0) + c_vals.get("hp", {}).get("step", 0) * (level - 1)) if c_vals else 0
            base_atk = (c_vals.get("atk", {}).get("base", 0) + c_vals.get("atk", {}).get("step", 0) * (level - 1)) if c_vals else 0
            base_def = (c_vals.get("def", {}).get("base", 0) + c_vals.get("def", {}).get("step", 0) * (level - 1)) if c_vals else 0
            base_spd = c_vals.get("spd", {}).get("base", 100) if c_vals else 100
            base_cr = c_vals.get("crit_rate", {}).get("base", 0.05) if c_vals else 0.05
            base_cd = c_vals.get("crit_dmg", {}).get("base", 0.5) if c_vals else 0.5

            if equipment:
                for p in equipment.get("_flat", {}).get("props", []):
                    ptype = p.get("type")
                    pval = p.get("value", 0)
                    if ptype == "BaseHP": base_hp += pval
                    elif ptype == "BaseAttack": base_atk += pval
                    elif ptype == "BaseDefence": base_def += pval

            hp_delta, hp_ratio = 0.0, 0.0
            atk_delta, atk_ratio = 0.0, 0.0
            def_delta, def_ratio = 0.0, 0.0
            spd_delta, cr_delta, cd_delta = 0.0, 0.0, 0.0
            break_delta = 0.0
            effect_res_delta = 0.0
            effect_hit_delta = 0.0
            sp_delta = 0.0
            heal_delta = 0.0
            dmg_boosts: Dict[str, float] = {}

            for r in raw_char.get("relicList", []):
                for p in r.get("_flat", {}).get("props", []):
                    ptype = p.get("type", "")
                    pval = p.get("value", 0)
                    if ptype == "HPDelta": hp_delta += pval
                    elif ptype == "HPAddedRatio": hp_ratio += pval
                    elif ptype == "AttackDelta": atk_delta += pval
                    elif ptype == "AttackAddedRatio": atk_ratio += pval
                    elif ptype == "DefenceDelta": def_delta += pval
                    elif ptype == "DefenceAddedRatio": def_ratio += pval
                    elif ptype == "SpeedDelta": spd_delta += pval
                    elif ptype in ["CriticalChance", "CriticalChanceBase"]: cr_delta += pval
                    elif ptype in ["CriticalDamage", "CriticalDamageBase"]: cd_delta += pval
                    elif ptype in ["BreakDamageAddedRatio", "BreakDamageAddedRatioBase"]: break_delta += pval
                    elif ptype in ["StatusResistance", "StatusResistanceBase"]: effect_res_delta += pval
                    elif ptype in ["StatusProbability", "StatusProbabilityBase"]: effect_hit_delta += pval
                    elif ptype in ["SPRatio", "SPRatioBase"]: sp_delta += pval
                    elif ptype in ["HealRatio", "HealRatioBase"]: heal_delta += pval
                    elif "AddedRatio" in ptype and ptype not in [
                        "HPAddedRatio", "AttackAddedRatio", "DefenceAddedRatio",
                        "SpeedAddedRatio", "BreakDamageAddedRatio", "ElationDamageAddedRatio"
                    ]:
                        prop_name = PROPERTIES.get(ptype, {}).get("name", "Tăng Sát Thương")
                        dmg_boosts[prop_name] = dmg_boosts.get(prop_name, 0.0) + pval

            final_hp = int(base_hp * (1 + hp_ratio) + hp_delta)
            final_atk = int(base_atk * (1 + atk_ratio) + atk_delta)
            final_def = int(base_def * (1 + def_ratio) + def_delta)
            final_spd = int(base_spd + spd_delta)
            final_cr = (base_cr + cr_delta) * 100
            final_cd = (base_cd + cd_delta) * 100

            stats_dict: Dict[str, str] = {
                "HP": f"{final_hp:,}",
                "Tấn Công": f"{final_atk:,}",
                "Phòng Thủ": f"{final_def:,}",
                "Tốc Độ": str(final_spd),
                "Tỷ Lệ Bạo Kích": f"{final_cr:.1f}%",
                "ST Bạo Kích": f"{final_cd:.1f}%",
            }

            # Bổ sung các chỉ số thứ cấp (nếu có giá trị > 0)
            for dname, dval in dmg_boosts.items():
                if dval > 0.0001:
                    stats_dict[dname] = f"{dval * 100:.1f}%"
            if break_delta > 0.0001:
                stats_dict["Tấn Công Kích Phá"] = f"{break_delta * 100:.1f}%"
            if effect_res_delta > 0.0001:
                stats_dict["Kháng Hiệu Ứng"] = f"{effect_res_delta * 100:.1f}%"
            if effect_hit_delta > 0.0001:
                stats_dict["Chính Xác Hiệu Ứng"] = f"{effect_hit_delta * 100:.1f}%"
            if sp_delta > 0.0001:
                stats_dict["Hồi Năng Lượng"] = f"{(1.0 + sp_delta) * 100:.1f}%"
            if heal_delta > 0.0001:
                stats_dict["Tăng Trị Liệu"] = f"{heal_delta * 100:.1f}%"

            icon_url = f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/avatar/{char_id}.png"

            results.append(
                HSRCharacter(
                    id=char_id,
                    name=meta["name"],
                    path=meta["path"],
                    element=meta["element"],
                    rarity=meta["rarity"],
                    level=level,
                    promotion=promotion,
                    eidolon=eidolon,
                    icon_url=icon_url,
                    light_cone=light_cone,
                    relics=relics,
                    stats=stats_dict,
                )
            )

        return results

    async def get_build(self, character_name_or_id: str) -> Optional[HSRBuild]:
        """Lấy hướng dẫn build cho nhân vật HSR."""
        if character_name_or_id.isdigit():
            meta = HSR_CHARACTERS.get(int(character_name_or_id))
            if meta:
                return get_hsr_build(meta["name"])
        return get_hsr_build(character_name_or_id)

    async def search(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Tìm kiếm dữ liệu game Honkai: Star Rail."""
        q = query.strip().lower()
        results: List[Dict[str, Any]] = []

        for char_id, meta in HSR_CHARACTERS.items():
            if q in meta["name"].lower() or q in meta["element"].lower() or q in meta["path"].lower():
                results.append({
                    "id": char_id,
                    "title": meta["name"],
                    "category": "Nhân Vật",
                    "rarity": meta["rarity"],
                    "element": meta["element"],
                    "path": meta["path"],
                    "description": f"Nhân vật {meta['rarity']}⭐ Vận mệnh {meta['path']} - Hệ {meta['element']}",
                    "icon_url": f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/avatar/{char_id}.png",
                })

        return results[:25]

    async def get_events(self) -> List[Dict[str, Any]]:
        """Lấy danh sách sự kiện Honkai: Star Rail đang diễn ra."""
        return [
            {
                "title": "Bước Nhảy Sự Kiện Nhân Vật: Kẻ Dệt Mộng & Ngôi Sao Sáng Ngời",
                "type": "Bước Nhảy",
                "status": "Đang diễn ra",
                "duration": "Phiên bản hiện tại",
                "description": "Tăng tỷ lệ nhận nhân vật 5 sao giới hạn và Nón Ánh Sáng độc quyền!",
            },
            {
                "title": "Sự Kiện Ủy Thác Đặc Biệt: Đăng Nhập Nhận Vé Tinh Cầu",
                "type": "Điểm Danh",
                "status": "Đang diễn ra",
                "duration": "Cả phiên bản",
                "description": "Đăng nhập 7 ngày nhận ngay 10 Vé Tinh Cầu Đặc Biệt!",
            },
        ]
