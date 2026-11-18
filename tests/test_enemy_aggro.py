import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from entities.enemies.enemy import Enemy
from entities.enemies.enemy_handler import gestionar_colisiones_enemigos
from entities.player import Player
from entities.weapons.base import Bullet


class EnemyAggroTests(unittest.TestCase):
    def setUp(self):
        self.player = Player(100, 100, 800, 600)
        self.enemy = Enemy(1000, 100)
        self.enemies = pygame.sprite.Group(self.enemy)
        self.drops = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

    def hit(self, damage=25):
        bullet = Bullet(self.enemy.rect.centerx, self.enemy.rect.centery,
                        1, 10, damage, (255, 255, 0))
        bullets = pygame.sprite.Group(bullet)
        gestionar_colisiones_enemigos(bullets, self.enemies, self.player, self.drops)
        self.assertFalse(bullets)

    def test_distant_enemy_patrols_until_bullet_hits(self):
        self.enemy.update(self.platforms, self.player)
        self.assertEqual(self.enemy.estado, "PATRULLAR")
        self.hit()
        self.assertEqual(self.enemy.vida, 125)
        self.assertEqual(self.enemy.estado, "PERSEGUIR")
        self.assertNotEqual(self.enemy.vel_x, 0)  # El impacto conserva su retroceso.
        start = self.enemy.rect.x
        for _ in range(30):
            self.enemy.update(self.platforms, self.player)
        self.assertLess(self.enemy.rect.x, start)
        self.assertFalse(self.enemy.mirando_derecha)

    def test_alert_tracks_player_on_either_side_even_at_different_height(self):
        self.hit()
        for x in (10, 2000):
            with self.subTest(player_x=x):
                self.player.rect.topleft = (x, -400)
                self.enemy.vel_x = 0
                start = self.enemy.rect.x
                self.enemy.update(self.platforms, self.player)
                self.assertEqual(self.enemy.estado, "PERSEGUIR")
                self.assertEqual(self.enemy.mirando_derecha, x > start)
                self.assertGreater(abs(self.enemy.rect.x - x), 0)
                self.assertLess(abs(self.enemy.rect.x - x), abs(start - x))

    def test_unhit_nearby_enemy_keeps_existing_detection(self):
        self.player.rect.x = 900
        self.enemy.update(self.platforms, self.player)
        self.assertEqual(self.enemy.estado, "PERSEGUIR")
        self.player.rect.x = 10
        self.enemy.update(self.platforms, self.player)
        self.assertEqual(self.enemy.estado, "PATRULLAR")

    def test_alert_is_individual_and_new_enemy_starts_unalerted(self):
        other = Enemy(1500, 100)
        self.enemies.add(other)
        self.hit()
        other.update(self.platforms, self.player)
        self.assertEqual(other.estado, "PATRULLAR")
        self.assertFalse(other.alertado_por_disparo)
        self.assertFalse(Enemy(1000, 100).alertado_por_disparo)

    def test_nonpositive_hits_do_not_alert_or_heal_enemy(self):
        for damage in (0, -10):
            self.hit(damage)
            self.assertFalse(self.enemy.alertado_por_disparo)
            self.assertEqual(self.enemy.vida, 150)

    def test_lethal_hit_removes_enemy_without_alert(self):
        with patch("entities.enemies.enemy.random.random", return_value=1):
            self.hit(150)
        self.assertFalse(self.enemies)
        self.assertFalse(self.enemy.alertado_por_disparo)


if __name__ == "__main__":
    unittest.main()
