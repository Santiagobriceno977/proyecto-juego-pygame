import os
import unittest
from collections import defaultdict
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from entities.drop import Drop
from entities.enemies.enemy import Enemy
from entities.weapons.base import Bullet
from main import Juego


class GameFlowTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(pygame.quit)
        for target, kwargs in (
            ("pygame.image.load", {"side_effect": lambda _: pygame.Surface((40, 40))}),
            ("pygame.mixer.music.load", {}),
            ("pygame.mixer.music.play", {}),
            ("pygame.key.get_pressed", {"return_value": defaultdict(bool)}),
            ("pygame.time.get_ticks", {"return_value": 1000}),
        ):
            mock = patch(target, **kwargs)
            result = mock.start()
            self.addCleanup(mock.stop)
            if target == "pygame.time.get_ticks":
                self.ticks = result
        self.game = Juego()

    def key(self, key):
        self.game.procesar_evento(pygame.event.Event(pygame.KEYDOWN, key=key))

    def play(self):
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "NIVELES")
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "JUGANDO")
        return self.game.partida

    def test_main_menu_level_selection_and_escape_back(self):
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "NIVELES")
        self.assertIsNone(self.game.partida)
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.estado, "MENU")

    def test_pause_freezes_world_and_resume_preserves_attempt(self):
        attempt = self.play()
        attempt.jugador.rect.centerx = 1000
        attempt.grupo_enemigos.add(Enemy(800, 488))
        bullet = Bullet(700, 400, 1, 10, 25, (255, 255, 0))
        attempt.grupo_balas.add(bullet)
        before = (attempt.jugador.rect.copy(), bullet.rect.copy(),
                  next(iter(attempt.grupo_enemigos)).rect.copy())
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.estado, "PAUSA")
        for _ in range(60):
            self.game.actualizar()
        self.assertEqual(before, (attempt.jugador.rect, bullet.rect,
                                 next(iter(attempt.grupo_enemigos)).rect))
        self.assertEqual(attempt.spawn_manager.zonas_activadas, set())
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.estado, "JUGANDO")
        self.assertIs(self.game.partida, attempt)

    def test_resume_menu_button(self):
        self.play()
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "JUGANDO")

    def test_gameplay_inputs_are_ignored_during_pause(self):
        attempt = self.play()
        weapon = next(iter(attempt.grupo_armas))
        attempt.grupo_armas.remove(weapon)
        attempt.jugador.inventario[0] = weapon
        attempt.jugador.arma_equipada = weapon
        weapon.balas_en_cargador = 2
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_r)
        self.key(pygame.K_e)
        self.game.actualizar()
        self.assertEqual(weapon.iniciando_recarga, 0)
        self.assertEqual(weapon.balas_en_cargador, 2)

    def test_pause_preserves_reload_cooldown_and_immunity_remaining_time(self):
        attempt = self.play()
        weapon = next(iter(attempt.grupo_armas))
        attempt.grupo_armas.remove(weapon)
        attempt.jugador.inventario[0] = weapon
        attempt.jugador.arma_equipada = weapon
        weapon.balas_en_cargador = 2
        weapon.iniciando_recarga = 100
        weapon.ultimo_disparo = 950
        attempt.jugador.ultimo_daño = 900
        self.key(pygame.K_ESCAPE)
        self.ticks.return_value = 6000
        self.key(pygame.K_ESCAPE)
        self.assertEqual(weapon.iniciando_recarga, 5100)
        self.assertEqual(weapon.ultimo_disparo, 5950)
        self.assertEqual(attempt.jugador.ultimo_daño, 5900)
        self.assertFalse(attempt.jugador.recibir_daño(10))
        weapon.update()
        self.assertEqual(weapon.balas_en_cargador, 2)
        self.ticks.return_value = 6599
        weapon.update()
        self.assertEqual(weapon.balas_en_cargador, 2)
        self.ticks.return_value = 6600
        weapon.update()
        self.assertEqual(weapon.balas_en_cargador, 10)
        self.assertEqual(weapon.municion_total, 22)
        self.ticks.return_value = 6650
        self.assertTrue(attempt.jugador.recibir_daño(10))

    def test_pause_at_zero_ticks_is_valid(self):
        attempt = self.play()
        self.ticks.return_value = 0
        self.key(pygame.K_ESCAPE)
        self.assertEqual(attempt.instante_pausa, 0)
        self.ticks.return_value = 5000
        self.key(pygame.K_ESCAPE)
        self.assertIsNone(attempt.instante_pausa)
        self.assertEqual(attempt.jugador.ultimo_daño, 4250)

    def test_focus_loss_pauses_only_active_game(self):
        self.game.procesar_evento(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertEqual(self.game.estado, "MENU")
        self.play()
        self.game.procesar_evento(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertEqual(self.game.estado, "PAUSA")

    def test_fatal_contact_opens_game_over_before_health_drop(self):
        attempt = self.play()
        attempt.jugador.rect.topleft = (200, 488)
        attempt.jugador.vida = 5
        attempt.jugador.blindaje = 0
        attempt.grupo_enemigos.add(Enemy(200, 488))
        drop = Drop(200, 488)
        drop.tipo, drop.valor = "vida", 25
        attempt.grupo_drops.add(drop)
        self.game.actualizar()
        self.assertEqual(self.game.estado, "GAME_OVER")
        self.assertEqual(attempt.jugador.vida, 0)
        self.assertIn(drop, attempt.grupo_drops)
        before = attempt.jugador.rect.copy()
        self.game.actualizar()
        self.assertEqual(attempt.jugador.rect, before)

    def test_restart_resets_every_part_of_attempt(self):
        old = self.play()
        old.jugador.vida = 0
        old.jugador.blindaje = 0
        old.jugador.rect.x = 2000
        old.spawn_manager.zonas_activadas.update((0, 1, 2))
        weapon = next(iter(old.grupo_armas))
        weapon.balas_en_cargador = 0
        old.grupo_armas.remove(weapon)
        old.jugador.inventario[0] = weapon
        old.jugador.arma_equipada = weapon
        old.grupo_balas.add(Bullet(700, 400, 1, 10, 25, (255, 255, 0)))
        old.grupo_enemigos.add(Enemy(800, 488))
        old.grupo_drops.add(Drop(900, 488))
        self.game.actualizar()
        self.key(pygame.K_RETURN)
        new = self.game.partida
        self.assertEqual(self.game.estado, "JUGANDO")
        self.assertIsNot(new, old)
        self.assertEqual((new.jugador.vida, new.jugador.blindaje), (100, 50))
        self.assertEqual(new.jugador.rect.topleft, (50, 480))
        self.assertEqual(new.jugador.inventario, [None, None, None])
        self.assertIsNone(new.jugador.arma_equipada)
        self.assertEqual(len(new.grupo_armas), 3)
        self.assertTrue(all(a.balas_en_cargador == a.stats.capacidad_cargador
                            for a in new.grupo_armas))
        self.assertFalse(new.grupo_balas or new.grupo_enemigos or new.grupo_drops)
        self.assertEqual(new.spawn_manager.zonas_activadas, set())

    def test_exit_after_death_returns_to_selector_without_closing(self):
        self.play().jugador.vida = 0
        self.game.actualizar()
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "NIVELES")
        self.assertIsNone(self.game.partida)
        self.assertTrue(self.game.activo)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.partida.jugador.vida, 100)

    def test_escape_after_death_cannot_resume_dead_character(self):
        self.play().jugador.vida = 0
        self.game.actualizar()
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.estado, "NIVELES")
        self.assertIsNone(self.game.partida)

    def test_exit_pause_returns_to_selector(self):
        self.play()
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_DOWN)
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.estado, "NIVELES")
        self.assertIsNone(self.game.partida)

    def test_mouse_can_select_and_start_level(self):
        for state in ("MENU", "NIVELES"):
            self.assertEqual(self.game.estado, state)
            rect = self.game.menus[state].botones[0]
            self.game.procesar_evento(pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, pos=rect.center, button=1))
        self.assertEqual(self.game.estado, "JUGANDO")

    def test_quit_is_available_on_every_screen(self):
        for state in ("MENU", "NIVELES", "JUGANDO", "PAUSA", "GAME_OVER"):
            with self.subTest(state=state):
                self.game.activo = True
                self.game.estado = state
                self.game.procesar_evento(pygame.event.Event(pygame.QUIT))
                self.assertFalse(self.game.activo)

    def test_main_menu_exit_closes_application(self):
        self.key(pygame.K_UP)
        self.key(pygame.K_RETURN)
        self.assertFalse(self.game.activo)

    def test_projectiles_advance_once_per_frame(self):
        attempt = self.play()
        bullet = Bullet(700, 400, 1, 10, 25, (255, 255, 0))
        attempt.grupo_balas.add(bullet)
        x = bullet.rect.x
        self.game.actualizar()
        self.assertEqual(bullet.rect.x, x + 10)

    def test_each_screen_renders(self):
        for state in ("MENU", "NIVELES"):
            self.game.cambiar_estado(state)
            self.game.dibujar()
        self.game.iniciar_partida()
        for state in ("JUGANDO", "PAUSA", "GAME_OVER"):
            self.game.cambiar_estado(state)
            self.game.dibujar()


if __name__ == "__main__":
    unittest.main()
