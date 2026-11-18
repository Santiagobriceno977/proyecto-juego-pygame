import os
import tempfile
import shutil
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from levels.tiled_map import MAPA_01, MapaTiled
from partida import Partida
from main import Juego


class TiledMapTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.addCleanup(pygame.quit)
        keys = patch("pygame.key.get_pressed", return_value=defaultdict(bool))
        keys.start()
        self.addCleanup(keys.stop)

    def test_real_map_has_three_rows_of_native_tiles_and_collisions(self):
        mapa = MapaTiled(MAPA_01)
        self.assertEqual((mapa.ancho, mapa.alto), (3200, 608))
        self.assertEqual([tuple(p.rect) for p in mapa.colisiones],
                         [(0, 512, 3200, 32), (0, 544, 3200, 32), (0, 576, 3200, 32)])
        tile = pygame.image.load(str(MAPA_01.parent / "1794978491787.png"))
        for y in (512, 544, 576):
            self.assertEqual(pygame.image.tobytes(mapa.imagen.subsurface((0, y, 32, 32)), "RGBA"),
                             pygame.image.tobytes(tile, "RGBA"))

    def test_spawns_camera_and_ground_follow_map(self):
        game = Partida(MAPA_01)
        self.assertEqual(game.camara_y, 8)
        self.assertEqual(game.jugador.rect.bottom, 512)
        for arma in game.grupo_armas:
            self.assertEqual(arma.rect.bottom, 512)
        game.jugador.rect.centerx = 3100
        game.spawn_manager.actualizar(game.jugador, game.grupo_enemigos)
        self.assertEqual(len(game.grupo_enemigos), 8)
        for enemigo in game.grupo_enemigos:
            self.assertEqual(enemigo.rect.bottom, 512)
        pantalla = pygame.Surface((800, 600))
        game.dibujar(pantalla)
        self.assertEqual(pantalla.get_at((790, 599)), game.mapa.imagen.get_at((3190, 607)))

    def test_walk_across_tile_seams_jump_and_land(self):
        game = Partida(MAPA_01)
        with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {pygame.K_d: True})):
            for _ in range(100):
                game.jugador.update(game.grupo_plataformas)
        self.assertEqual(game.jugador.rect.x, 550)
        self.assertEqual(game.jugador.rect.bottom, 512)
        with patch("pygame.key.get_pressed", return_value=defaultdict(bool, {pygame.K_SPACE: True})):
            game.jugador.update(game.grupo_plataformas)
        self.assertLess(game.jugador.rect.bottom, 512)
        for _ in range(90):
            game.jugador.update(game.grupo_plataformas)
        self.assertEqual(game.jugador.rect.bottom, 512)

    def copy_map(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for file in MAPA_01.parent.iterdir():
            if file.is_file():
                shutil.copyfile(file, Path(directory.name) / file.name)
        return Path(directory.name) / MAPA_01.name

    def test_erased_column_is_not_solid(self):
        ruta = self.copy_map()
        tree = ET.parse(ruta)
        data = tree.find("layer/data")
        values = [int(n) for n in data.text.split(",") if n.strip()]
        for row in (16, 17, 18):
            values[row * 100 + 20] = 0
        data.text = ",".join(map(str, values))
        tree.write(ruta)
        mapa = MapaTiled(ruta)
        with self.assertRaisesRegex(ValueError, "No hay suelo"):
            mapa.superficie_en(pygame.Rect(640, 0, 32, 48))
        self.assertEqual(mapa.superficie_en(pygame.Rect(608, 0, 32, 48)), 512)

    def test_tile_without_collision_is_only_visual(self):
        ruta = self.copy_map()
        tsx = ruta.parent / "tierra.tsx"
        tree = ET.parse(tsx)
        tile = tree.find("tile")
        tile.remove(tile.find("objectgroup"))
        tree.write(tsx)
        mapa = MapaTiled(ruta)
        self.assertEqual(len(mapa.colisiones), 0)
        self.assertNotEqual(mapa.imagen.get_at((0, 512)).a, 0)

    def test_unsupported_encoding_reports_clear_error(self):
        ruta = self.copy_map()
        tree = ET.parse(ruta)
        tree.find("layer/data").set("encoding", "base64")
        tree.write(ruta)
        with self.assertRaisesRegex(ValueError, "CSV"):
            MapaTiled(ruta)

    def test_selection_restart_and_return_to_legacy_level(self):
        for target in ("pygame.mixer.music.load", "pygame.mixer.music.play"):
            mock = patch(target)
            mock.start()
            self.addCleanup(mock.stop)
        game = Juego()
        def key(k):
            game.procesar_evento(pygame.event.Event(pygame.KEYDOWN, key=k))
        key(pygame.K_RETURN)
        key(pygame.K_DOWN)
        key(pygame.K_RETURN)
        self.assertIsNotNone(game.partida.mapa)
        original = game.partida
        original.jugador.vida = 0
        game.actualizar()
        self.assertEqual(game.estado, "GAME_OVER")
        key(pygame.K_RETURN)
        self.assertIsNot(game.partida, original)
        self.assertIsNotNone(game.partida.mapa)
        key(pygame.K_ESCAPE)
        self.assertEqual(game.estado, "PAUSA")
        key(pygame.K_ESCAPE)
        game.volver_al_selector()
        with patch("pygame.image.load", side_effect=lambda _: pygame.Surface((40, 40))):
            key(pygame.K_RETURN)
        self.assertIsNone(game.partida.mapa)


if __name__ == "__main__":
    unittest.main()
