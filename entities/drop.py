import pygame
import random


class Drop(pygame.sprite.Sprite):
    """Representa los objetos (munición, vida o blindaje) que sueltan los demonios al morir."""

    def __init__(self, x, y):
        super().__init__()

        # Definimos de manera aleatoria el tipo de recompensa:
        # 'municion', 'vida', o 'blindaje'
        self.tipo = random.choice(["municion", "vida", "blindaje"])

        # Dimensiones y representación visual temporal según el tipo
        self.ancho = 20
        self.alto = 20
        self.image = pygame.Surface((self.ancho, self.alto))

        # Color diferenciador para cada recompensa
        if self.tipo == "municion":
            self.image.fill((255, 165, 0))  # Naranja para munición
            self.valor = 15  # Cantidad de balas que otorga
        elif self.tipo == "vida":
            self.image.fill((0, 255, 0))  # Verde para vida
            self.valor = 25  # Cantidad de vida que recupera
        elif self.tipo == "blindaje":
            self.image.fill((0, 191, 255))  # Azul claro para blindaje
            self.valor = 20  # Cantidad de blindaje que otorga

        self.rect = self.image.get_rect()
        # Centramos el objeto en la posición donde murió el enemigo
        self.rect.x = x
        self.rect.y = y

    def aplicar_efecto(self, jugador):
        """Aplica la recompensa correspondiente al jugador cuando la recoge."""
        if self.tipo == "municion":
            if jugador.arma_equipada:
                jugador.arma_equipada.municion_total += self.valor
                print(f"¡Munición recogida! +{self.valor} balas.")
        elif self.tipo == "vida":
            jugador.vida += self.valor
            # Respetamos la vida máxima del jugador
            if jugador.vida > jugador.vida_maxima:
                jugador.vida = jugador.vida_maxima
            print(f"¡Vida recuperada! +{self.valor} HP.")
        elif self.tipo == "blindaje":
            jugador.blindaje += self.valor
            # CORRECCIÓN: Respetamos estrictamente el límite máximo de blindaje (50)
            if jugador.blindaje > jugador.blindaje_maximo:
                jugador.blindaje = jugador.blindaje_maximo
            print(f"¡Blindaje recargado! +{self.valor} armadura.")

        # Elimina el objeto del mapa una vez recogido
        self.kill()