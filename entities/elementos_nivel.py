import pygame


class Caja(pygame.sprite.Sprite):
    """Representa una caja en el escenario utilizando una textura de pixel art de 40x40."""

    def __init__(self, x, y, ancho=40, alto=40, ruta_imagen="assets/items/caja.png"):
        super().__init__()


        try:
            imagen_original = pygame.image.load(ruta_imagen).convert_alpha()

            self.image = pygame.transform.scale(imagen_original, (ancho, alto))
        except pygame.error as e:
            print(f"No se pudo cargar la textura de la caja en {ruta_imagen}: {e}")
            # Superficie de respaldo en caso de error de ruta
            self.image = pygame.Surface((ancho, alto))
            self.image.fill((139, 69, 19))  # Color marrón madera

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Escombro(pygame.sprite.Sprite):
    """Representa escombros en el suelo."""
    def __init__(self, x, y, ancho=60, alto=20):
        super().__init__()
        self.image = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        self.image.fill((100, 100, 100, 200))  # Gris semi-transparente
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y