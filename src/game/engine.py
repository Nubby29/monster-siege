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

    def log(self, message: str):
        self.state.combat_log.append(message)
        self.state.combat_log = self.state.combat_log[-8:]

    def spawn_monster(self) -> Monster | None:
        if self.state.raid_active or self.state.game_over:
            return None
        name, rarity, icon, threat, hp = self.rng.choice(MONSTERS)
        monster = Monster(self.next_id, name, rarity, round(self.rng.uniform(450, 950), 1), hp, threat, icon)
        self.next_id += 1
        self.monsters.append(monster)
        self.state.threat = min(self.state.threat_threshold, self.state.threat + threat)
        self.log(f"{name} entered the siege zone (+{threat} threat).")
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
            monster.distance_m = max(0.0, round(monster.distance_m - seconds * self.rng.uniform(3.0, 7.0), 1))
            if monster.distance_m == 0 and not monster.breached:
                monster.breached = True
                self.log(f"⚠ {monster.name} breached the base!")
            if monster.breached:
                self.state.base_hp = max(0, self.state.base_hp - int(2 * seconds))
        self.spawn_cooldown -= seconds
        if self.state.base_hp <= 0:
            self.state.game_over = True
            self.log("💥 Base destroyed.")
            return
        if not self.state.raid_active and self.spawn_cooldown <= 0:
            self.spawn_monster()
            self.spawn_cooldown = self.rng.uniform(8, 18)

    def _cooldown_tick(self):
        self.state.skill_cooldown = max(0, self.state.skill_cooldown - 1)

    def _monster_counter(self, monster: Monster):
        if not monster.alive or self.state.game_over:
            return
        damage = self.rng.randint(5, 12)
        if monster.rarity == MonsterRarity.ELITE:
            damage += 3
        if self.state.defending:
            damage = max(1, damage // 2)
            self.state.defending = False
            self.log(f"You defended. {monster.name}'s attack was reduced to {damage}.")
        else:
            self.log(f"{monster.name} attacked you for {damage} damage.")
        self.state.player_hp = max(0, self.state.player_hp - damage)
        if self.state.player_hp == 0:
            self.state.game_over = True
            self.log("💀 You were defeated. The siege continues no further.")

    def attack(self, monster_id: int, damage: int = 25) -> bool:
        if self.state.game_over:
            return False
        monster = next((m for m in self.monsters if m.id == monster_id and m.alive), None)
        if not monster:
            return False
        damage = max(1, min(damage, 100))
        monster.hp = max(0, monster.hp - damage)
        self.log(f"You attacked {monster.name} for {damage} damage.")
        if monster.hp == 0:
            monster.alive = False
            self.state.defeated += 1
            reward = 5 + monster.threat_value
            self.state.coins += reward
            self.state.threat = max(0, self.state.threat - max(1, monster.threat_value // 3))
            self.log(f"✓ {monster.name} defeated. +{reward} coins.")
        else:
            self._monster_counter(monster)
        self._cooldown_tick()
        return True

    def defend(self, monster_id: int) -> bool:
        if self.state.game_over:
            return False
        monster = next((m for m in self.monsters if m.id == monster_id and m.alive), None)
        if not monster:
            return False
        self.state.defending = True
        self.log(f"You raised your guard against {monster.name}.")
        self._monster_counter(monster)
        self._cooldown_tick()
        return True

    def use_potion(self, monster_id: int) -> bool:
        if self.state.game_over or self.state.potions <= 0:
            return False
        monster = next((m for m in self.monsters if m.id == monster_id and m.alive), None)
        if not monster:
            return False
        if self.state.player_hp >= self.state.max_player_hp:
            return False
        before = self.state.player_hp
        self.state.player_hp = min(self.state.max_player_hp, self.state.player_hp + 30)
        self.state.potions -= 1
        self.log(f"You used a potion and recovered {self.state.player_hp - before} HP.")
        self._monster_counter(monster)
        self._cooldown_tick()
        return True

    def use_skill(self, monster_id: int, damage: int = 45) -> bool:
        if self.state.game_over or self.state.skill_cooldown > 0:
            return False
        monster = next((m for m in self.monsters if m.id == monster_id and m.alive), None)
        if not monster:
            return False
        damage = max(1, min(damage, 100))
        monster.hp = max(0, monster.hp - damage)
        self.state.skill_cooldown = 3
        self.log(f"⚡ Power Strike dealt {damage} damage to {monster.name}.")
        if monster.hp == 0:
            monster.alive = False
            self.state.defeated += 1
            reward = 5 + monster.threat_value
            self.state.coins += reward
            self.state.threat = max(0, self.state.threat - max(1, monster.threat_value // 3))
            self.log(f"✓ {monster.name} defeated. +{reward} coins.")
        else:
            self._monster_counter(monster)
        return True

    def start_raid(self) -> RaidBoss:
        if self.state.raid_boss:
            return self.state.raid_boss
        name, hp, icon = self.rng.choice(BOSSES)
        boss = RaidBoss(name, hp, hp, self.state.threat_threshold, icon)
        self.state.raid_active = True
        self.state.raid_boss = boss
        self.log(f"🚨 RAID BOSS: {name} has appeared!")
        return boss

    def attack_boss(self, damage: int = 35) -> bool:
        boss = self.state.raid_boss
        if not boss or self.state.game_over:
            return False
        boss.hp = max(0, boss.hp - max(1, min(damage, 100)))
        self.log(f"You attacked {boss.name} for {damage} damage.")
        if boss.hp == 0:
            self.state.coins += 100
            self.state.wave += 1
            self.state.threat = 0
            self.state.raid_active = False
            self.state.raid_boss = None
            self.monsters.clear()
            self.spawn_cooldown = 0
            self.state.base_hp = min(self.state.max_base_hp, self.state.base_hp + 20)
            self.log("🏆 RAID CLEARED! +100 coins. Next wave begins.")
        return True
