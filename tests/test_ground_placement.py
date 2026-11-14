import os
import unittest
from collections import defaultdict
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config import ALTO_MUNDO, ALTO_SUELO, Y_SUELO
from entities.elementos_nivel import Caja, Escombro
from entities.enemies.enemy import Enemy
from entities.enemies.spawn_manager import SpawnManager, ZonaEnemigos
from partida import Partida


class GroundPlacementTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.addCleanup(pygame.quit)
        loader = patch("pygame.image.load",
                       side_effect=lambda _: pygame.Surface((40, 40)))
        loader.start()
        self.addCleanup(loader.stop)
        keys = patch("pygame.key.get_pressed", return_value=defaultdict(bool))
        keys.start()
        self.addCleanup(keys.stop)

    def test_ground_has_requested_height_and_reaches_world_bottom(self):
        game = Partida()
        self.assertEqual(ALTO_SUELO, 128)
        self.assertEqual(game.suelo.rect.height, 128)
        self.assertEqual(game.suelo.rect.top, 472)
        self.assertEqual(game.suelo.rect.bottom, ALTO_MUNDO)

    def test_player_weapons_and_encounters_follow_different_ground_heights(self):
        for height in (64, 128, 192):
            with self.subTest(height=height), patch("partida.ALTO_SUELO", height), \
                    patch("partida.Y_SUELO", ALTO_MUNDO - height):
                game = Partida()
                top = game.suelo.rect.top
                self.assertEqual(game.jugador.rect.bottom, top)
                for weapon in game.grupo_armas:
                    self.assertEqual(weapon.rect.bottom, top)
                game.jugador.rect.centerx = 3100
                game.spawn_manager.actualizar(game.jugador, game.grupo_enemigos)
                self.assertEqual(len(game.grupo_enemigos), 8)
                for enemy in game.grupo_enemigos:
                    self.assertEqual(enemy.rect.bottom, top)
                    self.assertFalse(enemy.rect.colliderect(game.suelo.rect))

    def test_player_stays_above_ground_and_can_jump_immediately(self):
        game = Partida()
        keys = defaultdict(bool, {pygame.K_SPACE: True})
        with patch("pygame.key.get_pressed", return_value=keys):
            game.jugador.update(game.grupo_plataformas)
        self.assertLess(game.jugador.rect.bottom, game.suelo.rect.top)
        for _ in range(90):
            game.jugador.update(game.grupo_plataformas)
        self.assertEqual(game.jugador.rect.bottom, game.suelo.rect.top)

    def test_debris_and_boxes_keep_their_supports(self):
        game = Partida()
        for obstacle in game.grupo_obstaculos:
            if isinstance(obstacle, Escombro):
                self.assertEqual(obstacle.rect.bottom, game.suelo.rect.top)
            elif isinstance(obstacle, Caja):
                self.assertTrue(any(
                    obstacle.rect.bottom == platform.rect.top
                    and platform.rect.left <= obstacle.rect.left
                    and obstacle.rect.right <= platform.rect.right
                    for platform in game.grupo_plataformas))

    def test_ground_spawn_uses_actual_enemy_height_and_preserves_explicit_y(self):
        def taller_enemy(x, y):
            enemy = Enemy(x, y)
            enemy.rect.height = 80
            return enemy
        game = Partida()
        manager = SpawnManager((ZonaEnemigos(0, ((100, None), (200, 120))),), Y_SUELO)
        with patch("entities.enemies.spawn_manager.Enemy", side_effect=taller_enemy):
            manager.actualizar(game.jugador, game.grupo_enemigos)
        grounded, explicit = game.grupo_enemigos.sprites()
        self.assertEqual(grounded.rect.bottom, Y_SUELO)
        self.assertEqual(grounded.rect.height, 80)
        self.assertEqual(explicit.rect.top, 120)


if __name__ == "__main__":
    unittest.main()
