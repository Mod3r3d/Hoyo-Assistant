"""Pydantic models cho dữ liệu Genshin Impact."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GenshinWeapon(BaseModel):
    name: str
    rarity: int
    level: int
    promote_level: int = 0
    refinement: int = 1
    icon_url: str = ""


class GenshinArtifact(BaseModel):
    name: str
    set_name: str
    slot: str  # Flower, Plume, Sands, Goblet, Circlet
    rarity: int
    level: int
    main_stat: str
    main_value: str
    sub_stats: List[str] = Field(default_factory=list)
    icon_url: str = ""


class GenshinCharacter(BaseModel):
    id: int
    name: str
    element: str
    rarity: int
    level: int
    max_level: int = 90
    friendship: int = 1
    constellation: int = 0
    icon_url: str = ""
    splash_url: str = ""
    weapon: Optional[GenshinWeapon] = None
    artifacts: List[GenshinArtifact] = Field(default_factory=list)
    stats: Dict[str, str] = Field(default_factory=dict)
    skills: Dict[str, int] = Field(default_factory=dict)


class GenshinProfile(BaseModel):
    uid: int
    nickname: str
    level: int
    world_level: int = 0
    signature: str = ""
    achievement_count: int = 0
    abyss_floor: int = 0
    abyss_chamber: int = 0
    avatar_url: str = ""
    namecard_url: str = ""
    showcase_characters: List[GenshinCharacter] = Field(default_factory=list)


class GenshinBuild(BaseModel):
    character_name: str
    element: str
    rarity: int = 5
    role: str
    weapons: List[str]
    artifact_sets: List[str]
    main_stats: Dict[str, str]  # Sands, Goblet, Circlet
    substats: List[str]
    talent_priority: str
    team_synergy: List[str]
    notes: str = ""
