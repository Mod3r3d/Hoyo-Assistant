"""Lớp cơ sở trừu tượng AutomationTask và Runner bảo vệ."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
from app.config import settings
from app.db.repositories.automation import AutomationLogRepository
from app.games.enums import GameType


class AutomationTask(ABC):
    def __init__(self, name: str, game: Optional[GameType] = None):
        self.name = name
        self.game = game

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Thực hiện công việc tự động hóa và trả về kết quả."""
        pass

    async def run(self) -> Dict[str, Any]:
        """Bọc logic thực thi với đo thời gian, ghi nhật ký và cách ly lỗi."""
        start_time = time.time()
        logger.info(f"[Task Start] Bắt đầu tác vụ: {self.name}")

        try:
            result = await self.execute()
            duration_ms = int((time.time() - start_time) * 1000)
            status = result.get("status", "SUCCESS")
            message = result.get("message", "Thực thi thành công")

            await AutomationLogRepository.log(
                task_name=self.name,
                game=self.game.value if self.game else None,
                status=status,
                duration_ms=duration_ms,
                message=message,
            )
            logger.info(f"[Task End] {self.name} hoàn thành trong {duration_ms}ms ({status}): {message}")
            return result

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.exception(f"[Task Error] {self.name} gặp lỗi sau {duration_ms}ms: {e}")

            await AutomationLogRepository.log(
                task_name=self.name,
                game=self.game.value if self.game else None,
                status="FAILED",
                duration_ms=duration_ms,
                message=str(e),
                error_detail=repr(e),
            )
            return {
                "status": "FAILED",
                "message": f"Lỗi thực thi: {e}",
                "error": str(e),
            }
