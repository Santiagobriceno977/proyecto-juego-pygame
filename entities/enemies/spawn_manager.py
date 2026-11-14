from dataclasses import dataclass

from config import Y_SUELO

from entities.enemies.enemy import Enemy


@dataclass(frozen=True)
class ZonaEnemigos:
    """Posiciones (x, y): y=None coloca los pies sobre el suelo del nivel."""

    activar_en_x: int
    posiciones: tuple[tuple[int, int | None], ...]


class SpawnManager:
    """Genera cada encuentro una sola vez, según el avance del jugador."""

    def __init__(self, zonas, suelo_y=Y_SUELO):
        self.suelo_y = suelo_y
        self.zonas = tuple(zonas)
        self.zonas_activadas = set()

    def actualizar(self, jugador, grupo_enemigos):
        for indice, zona in enumerate(self.zonas):
            if indice in self.zonas_activadas:
                continue
            if jugador.rect.centerx >= zona.activar_en_x:
                for x, y in zona.posiciones:
                    enemigo = Enemy(x, 0 if y is None else y)
                    if y is None:
                        enemigo.rect.bottom = self.suelo_y
                        enemigo.en_suelo = True
                    grupo_enemigos.add(enemigo)
                self.zonas_activadas.add(indice)
