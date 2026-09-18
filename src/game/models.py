from dataclasses import dataclass, field, field
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
    breached: bool = False

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
    base_hp: int = 100
    max_base_hp: int = 100
    player_hp: int = 100
    max_player_hp: int = 100
    potions: int = 3
    skill_cooldown: int = 0
    defending: bool = False
    raid_active: bool = False
    raid_boss: RaidBoss | None = None
    game_over: bool = False
    player_hp: int = 100
    max_player_hp: int = 100
    potions: int = 3
    skill_cooldown: int = 0
    defending: bool = False
    combat_log: list[str] = field(default_factory=list)
    combat_log: list[str] = field(default_factory=list)
