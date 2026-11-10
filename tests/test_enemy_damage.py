import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from config import ANCHO_MUNDO
from entities.player import Player
from entities.enemies.enemy import Enemy
from entities.enemies.enemy_handler import gestionar_colisiones_enemigos
from entities.weapons.base import Bullet


class EnemyDamageTests(unittest.TestCase):
    def setUp(self):
        self.player = Player(100, 100, 800, 600)
        self.enemy = Enemy(100, 100)
        self.enemies = pygame.sprite.Group(self.enemy)
        self.bullets = pygame.sprite.Group()
        self.drops = pygame.sprite.Group()
        self.clock = patch("pygame.time.get_ticks", return_value=0)
        self.ticks = self.clock.start()
        self.addCleanup(self.clock.stop)

    def collide(self):
        gestionar_colisiones_enemigos(
            self.bullets, self.enemies, self.player, self.drops
        )

    def test_contact_damages_shield_and_pushes_player(self):
        self.collide()
        self.assertEqual((self.player.blindaje, self.player.vida), (40, 100))
        self.assertEqual(self.player.rect.x, 88)

    def test_damage_overflows_shield_into_health(self):
        self.player.blindaje = 5
        self.collide()
        self.assertEqual((self.player.blindaje, self.player.vida), (0, 95))

    def test_contact_without_shield_reduces_health(self):
        self.player.blindaje = 0
        self.collide()
        self.assertEqual(self.player.vida, 90)

    def test_immunity_blocks_damage_and_push_until_exact_expiry(self):
        self.collide()
        first_x = self.player.rect.x
        self.ticks.return_value = 749
        self.collide()
        self.assertEqual(self.player.blindaje, 40)
        self.assertEqual(self.player.rect.x, first_x)
        self.ticks.return_value = 750
        self.collide()
        self.assertEqual(self.player.blindaje, 30)
        self.assertEqual(self.player.rect.x, first_x - 12)

    def test_multiple_enemies_only_apply_one_hit_per_cooldown(self):
        self.enemies.add(Enemy(100, 100), Enemy(100, 100))
        self.collide()
        self.assertEqual(self.player.blindaje, 40)
        self.assertEqual(self.player.rect.x, 88)

    def test_no_contact_does_not_damage_player(self):
        self.enemy.rect.x = 300
        self.collide()
        self.assertEqual((self.player.blindaje, self.player.vida), (50, 100))

    def test_health_stops_at_zero_and_dead_player_ignores_hits(self):
        self.player.blindaje = 0
        self.player.vida = 5
        self.collide()
        self.assertEqual(self.player.vida, 0)
        first_x = self.player.rect.x
        self.ticks.return_value = 1000
        self.collide()
        self.assertEqual(self.player.vida, 0)
        self.assertEqual(self.player.rect.x, first_x)

    def test_nonpositive_damage_does_not_start_immunity(self):
        self.assertFalse(self.player.recibir_daño(0))
        self.assertFalse(self.player.recibir_daño(-10))
        self.assertTrue(self.player.recibir_daño(10))
        self.assertEqual((self.player.blindaje, self.player.vida), (40, 100))

    def test_push_stays_within_world_bounds(self):
        for x, enemy_x, expected in ((0, 0, 0), (ANCHO_MUNDO - 32, ANCHO_MUNDO - 40, ANCHO_MUNDO - 32)):
            with self.subTest(x=x):
                self.player.rect.x = x
                self.enemy.rect.x = enemy_x
                self.player.ultimo_daño = -750
                self.collide()
                self.assertEqual(self.player.rect.x, expected)

    def test_bullet_kills_enemy_before_it_can_damage_player(self):
        self.enemy.vida = 25
        bullet = Bullet(116, 124, 1, 10, 25, (255, 255, 0))
        self.bullets.add(bullet)
        with patch("entities.enemies.enemy.random.random", return_value=1):
            self.collide()
        self.assertFalse(self.enemies)
        self.assertFalse(self.bullets)
        self.assertEqual((self.player.blindaje, self.player.vida), (50, 100))


if __name__ == "__main__":
    unittest.main()
