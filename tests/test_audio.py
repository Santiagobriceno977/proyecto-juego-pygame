import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from entities.weapons.pistol import Pistol
from entities.weapons.shotgun import Shotgun
from entities.weapons.metralleta import Metralleta
from main import Juego


class AudioTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(pygame.quit)
        self.mocks = {}
        for target, kwargs in (
            ("pygame.image.load", {"side_effect": lambda _: pygame.Surface((40, 40))}),
            ("pygame.mixer.music.load", {}),
            ("pygame.mixer.music.play", {}),
            ("pygame.mixer.music.stop", {}),
            ("pygame.mixer.music.unpause", {}),
        ):
            mock = patch(target, **kwargs)
            self.mocks[target] = mock.start()
            self.addCleanup(mock.stop)
        self.game = Juego()
        self.play = self.mocks["pygame.mixer.music.play"]
        self.stop = self.mocks["pygame.mixer.music.stop"]

    def test_menu_and_selector_share_continuous_music(self):
        self.play.assert_called_once_with(-1)
        self.game.cambiar_estado("NIVELES")
        self.game.cambiar_estado("MENU")
        self.play.assert_called_once_with(-1)
        self.stop.assert_not_called()

    def test_start_pause_resume_and_restart_do_not_play_menu_track(self):
        self.game.iniciar_partida()
        self.stop.assert_called_once_with()
        self.play.reset_mock()
        self.game.pausar()
        self.game.reanudar()
        self.game.partida.jugador.vida = 0
        self.game.actualizar()
        self.assertEqual(self.game.estado, "GAME_OVER")
        self.game.iniciar_partida()
        self.play.assert_not_called()
        self.mocks["pygame.mixer.music.unpause"].assert_not_called()

    def test_exiting_pause_returns_music_to_selector(self):
        self.game.iniciar_partida()
        self.game.pausar()
        self.play.reset_mock()
        self.game.volver_al_selector()
        self.assertEqual(self.game.estado, "NIVELES")
        self.play.assert_called_once_with(-1)

    def test_exiting_game_over_returns_music_to_selector(self):
        self.game.iniciar_partida()
        self.game.partida.jugador.vida = 0
        self.game.actualizar()
        self.play.reset_mock()
        self.game.volver_al_selector()
        self.play.assert_called_once_with(-1)

    def test_missing_track_does_not_break_navigation(self):
        self.mocks["pygame.mixer.music.load"].side_effect = FileNotFoundError("missing")
        self.play.reset_mock()
        with patch("builtins.print"):
            game = Juego()
        game.cambiar_estado("NIVELES")
        game.iniciar_partida()
        game.volver_al_selector()
        self.play.assert_not_called()

    def test_only_shotgun_shot_volume_is_lower(self):
        original_sound = pygame.mixer.Sound
        with patch("pygame.mixer.Sound", side_effect=lambda _: original_sound(buffer=bytes(256))):
            pistol, shotgun, machine_gun = Pistol(0, 0), Shotgun(0, 0), Metralleta(0, 0)
        self.assertAlmostEqual(pistol.sonido_disparo.get_volume(), 0.25, delta=1/128)
        self.assertAlmostEqual(machine_gun.sonido_disparo.get_volume(), 0.25, delta=1/128)
        self.assertAlmostEqual(shotgun.sonido_disparo.get_volume(), 0.12, delta=1/128)
        for weapon in (pistol, shotgun, machine_gun):
            self.assertAlmostEqual(weapon.sonido_recarga.get_volume(), 0.3, delta=1/128)


if __name__ == "__main__":
    unittest.main()
