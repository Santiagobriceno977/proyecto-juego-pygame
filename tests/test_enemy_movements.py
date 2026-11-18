import os
import unittest
from unittest.mock import patch
from collections import defaultdict

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from entities.enemies.enemy import Enemy
from entities.enemies.enemy_handler import gestionar_colisiones_enemigos
from entities.game_platform import Platform
from entities.player import Player
from entities.weapons.base import Bullet
from partida import Partida
from levels.tiled_map import MAPA_01


class EnemyMovementTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.addCleanup(pygame.quit)
        self.floor = Platform(0, 200, 1000, 96)
        self.platforms = pygame.sprite.Group(self.floor)
        self.enemy = Enemy(100, 152)
        self.player = Player(140, 152, 800, 600)
        self.enemies = pygame.sprite.Group(self.enemy)
        self.bullets = pygame.sprite.Group()
        self.drops = pygame.sprite.Group()
        clock = patch('pygame.time.get_ticks', return_value=1000)
        self.ticks = clock.start()
        self.addCleanup(clock.stop)

    def collide(self):
        gestionar_colisiones_enemigos(self.bullets, self.enemies, self.player,
                                     self.drops, self.platforms)

    def tick(self):
        self.enemy.update(self.platforms, self.player)
        self.collide()

    def test_windup_is_harmless_then_one_hit_then_recovery(self):
        self.tick()
        self.assertEqual(self.enemy.accion, 'PREPARAR')
        for _ in range(self.enemy.PREPARACION - 1):
            self.tick()
            self.assertEqual(self.player.blindaje, 50)
        self.tick()
        self.assertEqual(self.enemy.accion, 'GOLPEAR')
        self.assertEqual(self.player.blindaje, 40)
        # Incluso sin inmunidad y volviendo al alcance, no repite el mismo golpe.
        for _ in range(self.enemy.GOLPE - 1):
            self.player.rect.x = 140
            self.player.ultimo_daño = -1000
            self.tick()
            self.assertEqual(self.player.blindaje, 40)
        for _ in range(self.enemy.RECUPERACION):
            self.tick()
            self.assertEqual(self.player.blindaje, 40)
        self.tick()
        self.assertIsNone(self.enemy.fase_ataque)
        self.tick()
        self.assertEqual(self.enemy.fase_ataque, 'PREPARAR')

    def test_contact_without_attack_does_not_hurt(self):
        self.player.rect.topleft = self.enemy.rect.topleft
        self.collide()
        self.assertEqual(self.player.blindaje, 50)

    def test_dodge_behind_during_windup_avoids_committed_attack(self):
        self.tick()
        self.player.rect.x = 60
        for _ in range(self.enemy.PREPARACION + self.enemy.GOLPE):
            self.tick()
        self.assertEqual(self.player.blindaje, 50)
        self.assertTrue(self.enemy.mirando_derecha)

    def test_jump_above_attack_avoids_damage(self):
        self.tick()
        self.player.rect.y = 80
        for _ in range(self.enemy.PREPARACION + self.enemy.GOLPE):
            self.tick()
        self.assertEqual(self.player.blindaje, 50)

    def test_surviving_bullet_interrupts_active_swipe_before_damage(self):
        self.enemy.fase_ataque = 'GOLPEAR'
        self.bullets.add(Bullet(116, 176, 1, 10, 25, (255, 255, 0)))
        self.collide()
        self.assertEqual(self.player.blindaje, 50)
        self.assertEqual(self.enemy.vida, 125)
        self.assertEqual(self.enemy.accion, 'HERIDO')
        self.assertIsNone(self.enemy.fase_ataque)
        self.assertTrue(self.enemy.alertado_por_disparo)
        self.player.rect.x = 900
        for _ in range(self.enemy.TAMBALEO + 1):
            self.enemy.update(self.platforms, self.player)
        self.assertEqual(self.enemy.accion, 'CORRER')

    def test_swipe_does_not_cross_wall(self):
        self.enemy.fase_ataque = 'GOLPEAR'
        self.platforms.add(Platform(134, 140, 4, 60))
        self.collide()
        self.assertEqual(self.player.blindaje, 50)

    def test_safe_jump_clears_32px_step_in_both_directions(self):
        self.platforms.add(Platform(170, 168, 32, 32))
        for start, target, direction in ((130, 500, 1), (210, 0, -1)):
            with self.subTest(direction=direction):
                enemy = Enemy(start, 152)
                enemy.alertado_por_disparo = True
                self.player.rect.x = target
                actions = []
                for _ in range(90):
                    enemy.update(self.platforms, self.player)
                    actions.append(enemy.accion)
                    self.assertFalse(any(enemy.rect.colliderect(p.rect) for p in self.platforms))
                self.assertIn('SALTAR', actions)
                self.assertEqual(enemy.rect.bottom, 200)
                self.assertGreater((enemy.rect.x - start) * direction, 70)

    def test_tall_obstacle_and_low_ceiling_block_jump(self):
        for obstacle, ceiling in ((Platform(140, 136, 32, 64), None),
                                  (Platform(140, 168, 32, 32), Platform(80, 140, 150, 8))):
            with self.subTest(ceiling=bool(ceiling)):
                platforms = pygame.sprite.Group(self.floor, obstacle)
                if ceiling:
                    platforms.add(ceiling)
                enemy = Enemy(100, 152)
                self.player.rect.x = 500
                enemy.alertado_por_disparo = True
                for _ in range(45):
                    enemy.update(platforms, self.player)
                    self.assertNotEqual(enemy.accion, 'SALTAR')
                    self.assertLessEqual(enemy.rect.right, 140)

    def test_edge_does_not_cause_suicidal_chase(self):
        platforms = pygame.sprite.Group(Platform(0, 200, 160, 96))
        self.player.rect.x = 400
        for _ in range(100):
            self.enemy.alertado_por_disparo = True
            self.enemy.update(platforms, self.player)
        self.assertLessEqual(self.enemy.rect.right, 160)
        self.assertEqual(self.enemy.rect.bottom, 200)

    def test_no_landing_beyond_thin_obstacle_rejects_jump(self):
        platforms = pygame.sprite.Group(Platform(0, 200, 132, 96),
                                       Platform(138, 168, 2, 32))
        self.enemy.en_suelo = True
        self.assertFalse(self.enemy._salto_seguro(platforms, 1))

    def test_procedural_image_changes_pose_without_changing_hitbox(self):
        bounds = self.enemy.rect.copy()
        poses = []
        with patch('pygame.image.load', side_effect=AssertionError('No textures')):
            enemy = Enemy(100, 152)
            for action in ('CAMINAR', 'CORRER', 'PREPARAR', 'GOLPEAR', 'HERIDO', 'SALTAR'):
                enemy.accion = action
                enemy.fase_paso = 1
                enemy._dibujar_pose()
                poses.append(pygame.image.tobytes(enemy.image, 'RGBA'))
                self.assertEqual(enemy.rect, bounds)
                self.assertEqual(enemy.image.get_at((0, 0)).a, 0)
        self.assertEqual(len(set(poses)), 6)

    def test_facing_left_is_exact_mirror_without_ghost_pixels(self):
        self.enemy.accion = 'GOLPEAR'
        self.enemy._dibujar_pose()
        right = self.enemy.image.copy()
        self.enemy.mirando_derecha = False
        self.enemy._dibujar_pose()
        self.assertEqual(pygame.image.tobytes(self.enemy.image, 'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(right, True, False), 'RGBA'))

    def test_pause_freezes_attack_and_pose_in_tiled_level(self):
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            game = Partida(MAPA_01)
            game.jugador.rect.x = 140
            enemy = Enemy(100, 464)
            game.grupo_enemigos.add(enemy)
            game.actualizar()
            self.assertEqual(enemy.fase_ataque, 'PREPARAR')
            game.pausar()
            before = (enemy.tiempo_ataque, enemy.rect.copy(), pygame.image.tobytes(enemy.image, 'RGBA'))
            self.ticks.return_value += 10000
            for _ in range(60):
                game.actualizar()
                game.dibujar(pygame.display.get_surface())
            self.assertEqual(before, (enemy.tiempo_ataque, enemy.rect, pygame.image.tobytes(enemy.image, 'RGBA')))
            game.reanudar()
            game.actualizar()
            self.assertEqual(enemy.tiempo_ataque, before[0] - 1)


if __name__ == '__main__':
    unittest.main()
