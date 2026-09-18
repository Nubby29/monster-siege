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

if __name__ == "__main__":
    unittest.main()
