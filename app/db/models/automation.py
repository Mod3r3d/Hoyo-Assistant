"""Pydantic models cho lớp Automation v2."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.games.enums import GameType


class SessionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    discord_user_id: int
    game: GameType
    uid: int
    cookie_encrypted: str
    session_status: str = "VALID"  # VALID, EXPIRED, UNCHECKED, INVALID
    last_auth_check: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AutomationSettingsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    account_id: int
    discord_user_id: int
    automation_enabled: bool = True
    checkin_enabled: bool = True
    redeem_enabled: bool = True
    mimo_enabled: bool = True
    accompany_enabled: bool = False
    event_notify_enabled: bool = True
    notify_mode: str = "FAILURE_ONLY"  # ALL, FAILURE_ONLY, NONE
    notify_channel_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CheckinExecutionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    account_id: int
    game: GameType
    run_date: str  # YYYY-MM-DD
    status: str  # SUCCESS, ALREADY_CHECKED, FAILED, AUTH_REQUIRED, SKIPPED
    reward_summary: Optional[str] = None
    error_code: Optional[str] = None
    executed_at: Optional[datetime] = None


class GiftCodeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    code: str
    game: GameType
    source: str
    sources: Optional[str] = None
    rewards: Optional[str] = None
    confidence: str = "MEDIUM"  # HIGH (Verified), MEDIUM, LOW
    first_seen_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, INVALID


class GiftcodeRedemptionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    account_id: int
    gift_code_id: int
    game: GameType
    code: str
    status: str  # SUCCESS, ALREADY_REDEEMED, INVALID_CODE, EXPIRED, AUTH_REQUIRED, FAILED
    response_msg: Optional[str] = None
    redeemed_at: Optional[datetime] = None


class AutomationTaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    account_id: int
    provider: str  # mimo, accompany
    external_task_id: str
    task_name: str
    status: str  # AVAILABLE, COMPLETED, CLAIMED, FAILED
    reward: Optional[str] = None
    first_seen_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_error: Optional[str] = None


class WebEventModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    external_id: str
    game: GameType
    title: str
    url: str
    banner_url: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None


class AutomationLogModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    task_name: str
    game: Optional[str] = None
    account_id: Optional[int] = None
    status: str
    duration_ms: int = 0
    message: Optional[str] = None
    error_detail: Optional[str] = None
    created_at: Optional[datetime] = None
