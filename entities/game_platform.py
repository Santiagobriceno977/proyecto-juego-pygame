import pygame


class Platform(pygame.sprite.Sprite):

    def __init__(self, x, y, ancho, alto, ruta_imagen=None):
        super().__init__()
        # Creamos la superficie de la plataforma con transparencia (SRCALPHA)
        self.image = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        if ruta_imagen:
            try:
                # Cargamos la textura original
                textura = pygame.image.load(ruta_imagen).convert_alpha()

                # Forzamos a que el bloque sea un cuadrado perfecto basado en la altura de la plataforma (ej. 64x64)
                # Esto evita que la textura se estire de forma desproporcionada.
                tamano_bloque = alto
                textura_escalada = pygame.transform.scale(textura, (tamano_bloque, tamano_bloque))

                ancho_textura = textura_escalada.get_width()

                # Dibujamos en mosaico horizontal sin estirar los bloques individuales
                x_actual = 0
                while x_actual < ancho:
                    espacio_restante = ancho - x_actual

                    if espacio_restante < ancho_textura:
                        # Recortamos limpiamente el último bloque si rebasa los 800 píxeles de la pantalla
                        textura_recortada = textura_escalada.subsurface((0, 0, espacio_restante, alto))
                        self.image.blit(textura_recortada, (x_actual, 0))
                        break
                    else:
                        # Dibujamos el bloque cuadrado completo
                        self.image.blit(textura_escalada, (x_actual, 0))
                        x_actual += ancho_textura

            except Exception as e:
                print(f"No se pudo cargar la textura de plataforma: {e}")
                self.image.fill((70, 70, 70))
        else:
            self.image.fill((70, 70, 70))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y