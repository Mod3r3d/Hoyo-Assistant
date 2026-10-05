"""Hệ thống Giftcode Aggregator nhiều nguồn chuẩn v2 cho Genshin Impact & Honkai: Star Rail.

Tuân thủ kiến trúc phân tầng độc lập:
1. Public Discovery (Không cần tài khoản): Thu thập, Chuẩn hóa, Khử trùng, Định danh độ tin cậy.
2. Account Automation (Auto Redeem): Độc lập, bảo mật tuyệt đối, sử dụng session đã mã hóa.
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import aiohttp
from loguru import logger
from app.games.enums import GameType


@dataclass(slots=True)
class GiftCodeCandidate:
    """Đối tượng mã quà tặng ứng viên được thu thập từ một nguồn."""
    code: str
    game: GameType
    source: str
    rewards: Optional[str] = None
    expires_at: Optional[datetime] = None
    discovered_at: datetime = field(default_factory=datetime.now)


class GiftCodeSource(ABC):
    """Giao diện trừu tượng cho mọi nguồn cung cấp Giftcode."""
    name: str

    @abstractmethod
    async def fetch_codes(self, game: GameType) -> List[GiftCodeCandidate]:
        """Thu thập danh sách mã ứng viên từ nguồn."""
        pass


class SeriaCodesSource(GiftCodeSource):
    """Nguồn cấp mã tự động qua hoyo-codes.seria.moe API."""
    name = "seria"
    BASE_URL = "https://hoyo-codes.seria.moe/codes"

    async def fetch_codes(self, game: GameType) -> List[GiftCodeCandidate]:
        candidates: List[GiftCodeCandidate] = []
        # Query parameter: 'genshin' cho Genshin Impact, 'hkrpg' cho Honkai: Star Rail
        query_game = "genshin" if game == GameType.GENSHIN else "hkrpg"
        url = f"{self.BASE_URL}?game={query_game}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        codes_list = data.get("codes", []) if isinstance(data, dict) else []
                        for item in codes_list:
                            raw_code = item.get("code")
                            status = item.get("status", "OK")
                            if raw_code and status == "OK":
                                candidates.append(
                                    GiftCodeCandidate(
                                        code=raw_code,
                                        game=game,
                                        source=self.name,
                                        rewards=item.get("rewards") or None,
                                    )
                                )
        except Exception as e:
            logger.warning(f"[{self.name}] Lỗi khi tải mã {game.value}: {e}")

        return candidates


class BabalaeCodesSource(GiftCodeSource):
    """Nguồn cấp mã qua kho lưu trữ cộng đồng babalae/genshin-redeem-code."""
    name = "babalae"
    GENSHIN_URL = "https://raw.githubusercontent.com/babalae/genshin-redeem-code/main/codes.json"

    async def fetch_codes(self, game: GameType) -> List[GiftCodeCandidate]:
        candidates: List[GiftCodeCandidate] = []
        if game != GameType.GENSHIN:
            return candidates

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.GENSHIN_URL, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        if isinstance(data, list):
                            now_date = datetime.now().strftime("%Y-%m-%d")
                            for entry in data:
                                valid_date = entry.get("valid")
                                # Kiểm tra thời hạn nếu có
                                if valid_date and valid_date < now_date:
                                    continue

                                rewards = entry.get("content") or entry.get("title")
                                for c in entry.get("codes", []):
                                    if c and isinstance(c, str):
                                        candidates.append(
                                            GiftCodeCandidate(
                                                code=c,
                                                game=game,
                                                source=self.name,
                                                rewards=rewards,
                                            )
                                        )
        except Exception as e:
            logger.warning(f"[{self.name}] Lỗi khi tải mã {game.value}: {e}")

        return candidates


class PermanentOfficialSource(GiftCodeSource):
    """Nguồn các mã chính thức vĩnh viễn và sự kiện phiên bản chuẩn."""
    name = "official"

    GENSHIN_CODES = [
        {"code": "GENSHINGIFT", "rewards": "50 Nguyên Thạch, 3 Kinh Nghiệm Anh Hùng"},
    ]
    HSR_CODES = [
        {"code": "STARRAILGIFT", "rewards": "50 Ngọc Ánh Sao, 10.000 Điểm Tín Dụng, 2 Hướng Dẫn Dạo Chơi"},
    ]

    async def fetch_codes(self, game: GameType) -> List[GiftCodeCandidate]:
        candidates: List[GiftCodeCandidate] = []
        preset = self.GENSHIN_CODES if game == GameType.GENSHIN else self.HSR_CODES
        for item in preset:
            candidates.append(
                GiftCodeCandidate(
                    code=item["code"],
                    game=game,
                    source=self.name,
                    rewards=item["rewards"],
                )
            )
        return candidates


class GiftcodeAggregator:
    """Bộ thu thập, hợp nhất và xác thực Giftcode từ nhiều nguồn độc lập."""

    def __init__(self, sources: Optional[List[GiftCodeSource]] = None):
        self.sources: List[GiftCodeSource] = sources or [
            SeriaCodesSource(),
            BabalaeCodesSource(),
            PermanentOfficialSource(),
        ]

    @staticmethod
    def normalize_code(raw_code: str) -> Optional[str]:
        """Chuẩn hóa chuỗi mã giftcode (bóc tách URL, viết hoa, loại bỏ khoảng trắng thừa)."""
        if not raw_code:
            return None

        c = raw_code.strip()

        # Nếu là đường dẫn URL, bóc tách tham số ?code=...
        if c.startswith("http://") or c.startswith("https://"):
            try:
                parsed = urlparse(c)
                qs = parse_qs(parsed.query)
                if "code" in qs and qs["code"]:
                    c = qs["code"][0].strip()
            except Exception:
                pass

        c = c.upper()
        # Chỉ giữ lại các ký tự hợp lệ cho mã quà tặng HoYoverse: chữ cái, số, gạch dưới, gạch ngang
        # Độ dài thường từ 4 đến 30 ký tự
        if re.match(r"^[A-Z0-9_\-]{4,30}$", c):
            return c
        return None

    async def collect(self, game: GameType) -> List[Dict[str, Any]]:
        """
        Thu thập mã từ tất cả các nguồn theo thời gian thực,
        chuẩn hóa, khử trùng lặp và tính toán độ tin cậy.
        """
        tasks = [source.fetch_codes(game) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_candidates: List[GiftCodeCandidate] = []
        for i, res in enumerate(results):
            src_name = self.sources[i].name
            if isinstance(res, Exception):
                logger.error(f"[Aggregator] Nguồn {src_name} gặp sự cố: {res}")
            elif isinstance(res, list):
                all_candidates.extend(res)

        return self._deduplicate_and_score(all_candidates, game)

    def _deduplicate_and_score(
        self, candidates: List[GiftCodeCandidate], game: GameType
    ) -> List[Dict[str, Any]]:
        """Hợp nhất mã trùng lặp từ các nguồn khác nhau và chấm điểm tin cậy."""
        grouped: Dict[str, Dict[str, Any]] = {}

        for cand in candidates:
            clean_code = self.normalize_code(cand.code)
            if not clean_code:
                continue

            if clean_code not in grouped:
                grouped[clean_code] = {
                    "code": clean_code,
                    "game": game,
                    "sources": set(),
                    "rewards": cand.rewards,
                    "expires_at": cand.expires_at,
                    "status": "ACTIVE",
                }

            entry = grouped[clean_code]
            entry["sources"].add(cand.source)

            # Ưu tiên mô tả phần thưởng chi tiết hơn
            if cand.rewards and (not entry["rewards"] or len(cand.rewards) > len(entry["rewards"])):
                entry["rewards"] = cand.rewards

            if cand.expires_at:
                entry["expires_at"] = cand.expires_at

        # Tính toán độ tin cậy (Confidence)
        final_list: List[Dict[str, Any]] = []
        for code, info in grouped.items():
            sources_set = info["sources"]
            # Nếu có xác nhận từ nguồn chính thức hoặc từ 2 nguồn độc lập trở lên -> HIGH (Verified)
            if "official" in sources_set or len(sources_set) >= 2:
                confidence = "HIGH"
            else:
                confidence = "MEDIUM"

            final_list.append({
                "code": code,
                "game": game,
                "source": ", ".join(sorted(sources_set)),
                "sources_list": sorted(list(sources_set)),
                "rewards": info["rewards"],
                "expires_at": info["expires_at"],
                "confidence": confidence,
                "status": info["status"],
            })

        return final_list


# Định danh tương thích ngược cho hệ thống tác vụ
GiftcodeDiscoveryProvider = GiftcodeAggregator
