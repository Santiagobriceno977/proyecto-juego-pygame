from pathlib import Path

import pygame


DIRECTORIO_FUENTES = Path(__file__).resolve().parent / "assets" / "fonts"


def cargar_fuente(tamano, retro=False):
    """Carga las fuentes incluidas en el juego, sin instalarlas en el sistema."""
    nombre = "VT323-Regular.ttf" if retro else "Rajdhani-Medium.ttf"
    return pygame.font.Font(str(DIRECTORIO_FUENTES / nombre), tamano)
