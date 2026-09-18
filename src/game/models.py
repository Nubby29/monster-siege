from dataclasses import dataclass
from enum import Enum

class MonsterRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    ELITE = "elite"

@dataclass
class Monster:
    id: int
    name: str
    rarity: MonsterRarity
    distance_m: float
    hp: int
    threat_value: int
    icon: str = "👾"
    alive: bool = True

@dataclass
class RaidBoss:
    name: str
    hp: int
    max_hp: int
    threat_threshold: int
    icon: str = "🐉"

@dataclass
class GameState:
    threat: int = 0
    threat_threshold: int = 100
    wave: int = 1
    coins: int = 0
    defeated: int = 0
    raid_active: bool = False
    raid_boss: RaidBoss | None = None
