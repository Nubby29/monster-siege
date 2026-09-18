import random
from .models import GameState, Monster, MonsterRarity, RaidBoss

MONSTERS = [
    ("Grublet", MonsterRarity.COMMON, "🐛", 5, 8),
    ("Nightfang", MonsterRarity.UNCOMMON, "🐺", 12, 14),
    ("Scorpling", MonsterRarity.RARE, "🦂", 20, 20),
    ("Brutox", MonsterRarity.ELITE, "👹", 35, 30),
]
BOSSES = [("Dreadmaw", 220, "🐉"), ("Iron Behemoth", 280, "🦖"), ("Void Stag", 250, "🦌")]

class SiegeEngine:
    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self.state = GameState()
        self.monsters: list[Monster] = []
        self.next_id = 1
        self.spawn_cooldown = 0.0

    def spawn_monster(self) -> Monster | None:
        if self.state.raid_active or self.state.game_over:
            return None
        name, rarity, icon, threat, hp = self.rng.choice(MONSTERS)
        monster = Monster(self.next_id, name, rarity, round(self.rng.uniform(450, 950), 1), hp, threat, icon)
        self.next_id += 1
        self.monsters.append(monster)
        self.state.threat = min(self.state.threat_threshold, self.state.threat + threat)
        if self.state.threat >= self.state.threat_threshold:
            self.start_raid()
        return monster

    def advance(self, seconds: int = 10) -> None:
        if self.state.game_over:
            return
        seconds = max(0, min(seconds, 300))
        for monster in self.monsters:
            if not monster.alive:
                continue
            old_distance = monster.distance_m
            monster.distance_m = max(0.0, round(monster.distance_m - seconds * self.rng.uniform(3.0, 7.0), 1))
            if monster.distance_m == 0 and not monster.breached:
                monster.breached = True
            if monster.breached:
                # A monster that reaches the base damages it continuously until defeated.
                self.state.base_hp = max(0, self.state.base_hp - int(2 * seconds))
        self.spawn_cooldown -= seconds
        if self.state.base_hp <= 0:
            self.state.game_over = True
            return
        if not self.state.raid_active and self.spawn_cooldown <= 0:
            self.spawn_monster()
            self.spawn_cooldown = self.rng.uniform(8, 18)

    def attack(self, monster_id: int, damage: int = 25) -> bool:
        if self.state.game_over:
            return False
        monster = next((m for m in self.monsters if m.id == monster_id and m.alive), None)
        if not monster:
            return False
        monster.hp = max(0, monster.hp - max(1, min(damage, 100)))
        if monster.hp == 0:
            monster.alive = False
            self.state.defeated += 1
            self.state.coins += 5 + monster.threat_value
            self.state.threat = max(0, self.state.threat - max(1, monster.threat_value // 3))
        return True

    def start_raid(self) -> RaidBoss:
        if self.state.raid_boss:
            return self.state.raid_boss
        name, hp, icon = self.rng.choice(BOSSES)
        boss = RaidBoss(name, hp, hp, self.state.threat_threshold, icon)
        self.state.raid_active = True
        self.state.raid_boss = boss
        return boss

    def attack_boss(self, damage: int = 35) -> bool:
        boss = self.state.raid_boss
        if not boss or self.state.game_over:
            return False
        boss.hp = max(0, boss.hp - max(1, min(damage, 100)))
        if boss.hp == 0:
            self.state.coins += 100
            self.state.wave += 1
            self.state.threat = 0
            self.state.raid_active = False
            self.state.raid_boss = None
            self.monsters.clear()
            self.spawn_cooldown = 0
            self.state.base_hp = min(self.state.max_base_hp, self.state.base_hp + 20)
        return True
