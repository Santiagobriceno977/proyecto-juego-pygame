from entities.weapons.base import BaseWeapon
from config import SHOTGUN_STATS


class Shotgun(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(x, y, SHOTGUN_STATS)

    def _proyectiles(self, x, y, direccion):
        """La escopeta dispara 3 perdigones verticales en lugar de uno."""
        return [self._criar_bala(x, y, direccion, off) for off in (-10, 0, 10)]