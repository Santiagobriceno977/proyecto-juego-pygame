from dataclasses import dataclass

from entities.enemies.enemy import Enemy


@dataclass(frozen=True)
class ZonaEnemigos:
    """Activa sus posiciones (x, y) al alcanzar una coordenada del mundo."""

    activar_en_x: int
    posiciones: tuple[tuple[int, int], ...]


class SpawnManager:
    """Genera cada encuentro una sola vez, según el avance del jugador."""

    def __init__(self, zonas):
        self.zonas = tuple(zonas)
        self.zonas_activadas = set()

    def actualizar(self, jugador, grupo_enemigos):
        for indice, zona in enumerate(self.zonas):
            if indice in self.zonas_activadas:
                continue
            if jugador.rect.centerx >= zona.activar_en_x:
                for x, y in zona.posiciones:
                    grupo_enemigos.add(Enemy(x, y))
                self.zonas_activadas.add(indice)
