from entities.weapons.base import BaseWeapon
from config import PISTOL_STATS


class Pistol(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(x, y, PISTOL_STATS)