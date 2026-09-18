import unittest
from src.game.engine import SiegeEngine

class SiegeEngineTests(unittest.TestCase):
    def test_spawn_increases_threat(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        self.assertIsNotNone(monster)
        self.assertGreater(game.state.threat, 0)

    def test_defeat_rewards_and_reduces_threat(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        before = game.state.threat
        game.attack(monster.id, 100)
        self.assertFalse(monster.alive)
        self.assertEqual(game.state.defeated, 1)
        self.assertGreater(game.state.coins, 0)
        self.assertLess(game.state.threat, before)

    def test_threshold_starts_raid(self):
        game = SiegeEngine(seed=1)
        while not game.state.raid_active:
            game.spawn_monster()
        self.assertIsNotNone(game.state.raid_boss)
        self.assertEqual(game.state.threat, game.state.threat_threshold)

    def test_boss_defeat_starts_next_wave(self):
        game = SiegeEngine(seed=1)
        game.start_raid()
        old_wave = game.state.wave
        for _ in range(10):
            game.attack_boss(100)
            if not game.state.raid_active:
                break
        self.assertEqual(game.state.wave, old_wave + 1)
        self.assertFalse(game.state.raid_active)
        self.assertEqual(game.state.threat, 0)

    def test_breached_monster_damages_base(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        monster.distance_m = 1
        before = game.state.base_hp
        game.advance(1)
        self.assertTrue(monster.breached)
        self.assertLess(game.state.base_hp, before)

    def test_attack_causes_monster_counter(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        before = game.state.player_hp
        game.attack(monster.id, 1)
        self.assertLess(game.state.player_hp, before)

    def test_defend_reduces_incoming_damage(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        game.state.player_hp = 100
        game.defend(monster.id)
        self.assertLess(game.state.player_hp, 100)
        self.assertFalse(game.state.defending)

    def test_potion_consumes_and_heals(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        game.state.player_hp = 50
        before = game.state.potions
        game.use_potion(monster.id)
        self.assertEqual(game.state.potions, before - 1)
        self.assertGreater(game.state.player_hp, 50)

    def test_skill_has_cooldown(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        game.use_skill(monster.id, 1)
        self.assertEqual(game.state.skill_cooldown, 3)
        self.assertFalse(game.use_skill(monster.id, 1))

    def test_attack_causes_monster_counter(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        before = game.state.player_hp
        game.attack(monster.id, 1)
        self.assertLess(game.state.player_hp, before)

    def test_defend_reduces_damage_and_clears_guard(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        game.defend(monster.id)
        self.assertFalse(game.state.defending)
        self.assertLess(game.state.player_hp, game.state.max_player_hp)

    def test_potion_heals_and_consumes_charge(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        game.state.player_hp = 50
        game.use_potion(monster.id)
        self.assertEqual(game.state.potions, 2)
        self.assertGreater(game.state.player_hp, 50)

    def test_power_strike_has_cooldown(self):
        game = SiegeEngine(seed=1)
        monster = game.spawn_monster()
        self.assertTrue(game.use_skill(monster.id))
        self.assertEqual(game.state.skill_cooldown, 3)
        self.assertFalse(game.use_skill(monster.id))

if __name__ == "__main__":
    unittest.main()
