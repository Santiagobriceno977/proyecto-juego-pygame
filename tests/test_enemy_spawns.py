import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config import ANCHO_MUNDO, Y_SUELO
from entities.enemies.spawn_manager import SpawnManager, ZonaEnemigos
from entities.player import Player
from levels.nivel_prueba import ZONAS_ENEMIGOS


class EnemySpawnTests(unittest.TestCase):
    def setUp(self):
        self.player = Player(50, 480, 800, 600)
        self.enemies = pygame.sprite.Group()
        self.zonas = (
            ZonaEnemigos(300, ((650, 488), (900, 488))),
            ZonaEnemigos(1000, ((1320, 488),)),
        )
        self.manager = SpawnManager(self.zonas)

    def advance_to(self, x):
        self.player.rect.centerx = x
        self.manager.actualizar(self.player, self.enemies)

    def test_waiting_before_first_zone_does_not_spawn_enemies(self):
        for _ in range(180):
            self.advance_to(299)
        self.assertEqual(len(self.enemies), 0)

    def test_exact_threshold_spawns_at_level_positions(self):
        self.advance_to(300)
        self.assertCountEqual(
            [enemy.rect.topleft for enemy in self.enemies],
            [(650, 488), (900, 488)],
        )

    def test_same_zone_does_not_repeat_across_frames(self):
        for _ in range(180):
            self.advance_to(500)
        self.assertEqual(len(self.enemies), 2)

    def test_killing_every_enemy_does_not_start_a_new_wave(self):
        self.advance_to(300)
        for enemy in self.enemies.sprites():
            enemy.kill()
        self.advance_to(500)
        self.assertEqual(len(self.enemies), 0)

    def test_backtracking_and_returning_does_not_respawn(self):
        self.advance_to(300)
        self.enemies.empty()
        self.advance_to(50)
        self.advance_to(300)
        self.assertEqual(len(self.enemies), 0)

    def test_next_zone_activates_even_with_previous_enemies_alive(self):
        self.advance_to(300)
        self.advance_to(1000)
        self.assertEqual(len(self.enemies), 3)

    def test_large_advance_activates_all_passed_zones(self):
        self.advance_to(1500)
        self.assertEqual(len(self.enemies), 3)
        self.assertEqual(self.manager.zonas_activadas, {0, 1})

    def test_new_level_manager_has_independent_progress(self):
        self.advance_to(1000)
        second_manager = SpawnManager(self.zonas)
        second_group = pygame.sprite.Group()
        second_manager.actualizar(self.player, second_group)
        self.assertEqual(len(second_group), 3)

    def test_empty_level_has_no_encounters(self):
        SpawnManager(()).actualizar(self.player, self.enemies)
        self.assertEqual(len(self.enemies), 0)

    def test_test_level_encounters_are_inside_world_and_on_ground(self):
        self.assertEqual(len(ZONAS_ENEMIGOS), 4)
        manager = SpawnManager(ZONAS_ENEMIGOS)
        for zona in ZONAS_ENEMIGOS:
            self.assertGreater(zona.activar_en_x, 66)
            self.assertLess(zona.activar_en_x, ANCHO_MUNDO)
            self.player.rect.centerx = zona.activar_en_x
            manager.actualizar(self.player, self.enemies)
        self.assertEqual(len(self.enemies), 8)
        for enemy in self.enemies:
            self.assertGreaterEqual(enemy.rect.left, 0)
            self.assertLessEqual(enemy.rect.right, ANCHO_MUNDO)
            self.assertEqual(enemy.rect.bottom, Y_SUELO)


if __name__ == "__main__":
    unittest.main()
