"""Pydantic models cho dữ liệu Honkai: Star Rail."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HSRLightCone(BaseModel):
    name: str
    rarity: int
    level: int
    promotion: int = 0
    superimposition: int = 1
    icon_url: str = ""


class HSRRelic(BaseModel):
    name: str
    set_name: str
    slot: str  # Đầu, Tay, Thân, Chân, Cầu Vị Diện, Dây Liên Kết
    rarity: int
    level: int
    main_stat: str
    main_value: str
    sub_stats: List[str] = Field(default_factory=list)
    icon_url: str = ""


class HSRCharacter(BaseModel):
    id: int
    name: str
    path: str
    element: str
    rarity: int
    level: int
    promotion: int = 6
    eidolon: int = 0
    icon_url: str = ""
    splash_url: str = ""
    light_cone: Optional[HSRLightCone] = None
    relics: List[HSRRelic] = Field(default_factory=list)
    stats: Dict[str, str] = Field(default_factory=dict)


class HSRProfile(BaseModel):
    uid: int
    nickname: str
    level: int  # Trailblaze Level
    world_level: int = 0  # Equilibrium Level
    signature: str = ""
    achievement_count: int = 0
    avatar_count: int = 0
    avatar_url: str = ""
    showcase_characters: List[HSRCharacter] = Field(default_factory=list)


class HSRBuild(BaseModel):
    character_name: str
    path: str
    element: str
    rarity: int = 5
    role: str
    light_cones: List[str]
    relic_sets: List[str]
    planar_sets: List[str]
    main_stats: Dict[str, str]  # Body, Feet, Planar Sphere, Link Rope
    substats: List[str]
    trace_priority: str
    team_synergy: List[str]
    notes: str = ""
