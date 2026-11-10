from entities.weapons.base import BaseWeapon
from config import METRALLETA_STATS


class Metralleta(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(x, y, METRALLETA_STATS)