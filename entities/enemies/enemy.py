import pygame
import random
from entities.drop import Drop

class Enemy(pygame.sprite.Sprite):
    """Clase base para todos los demonios del juego."""

    def __init__(self, x, y, vida_base=75):
        super().__init__()

        # Dimensiones visuales temporales
        self.ancho = 32
        self.alto = 48

        self.image = pygame.Surface((self.ancho, self.alto))
        self.image.fill((180, 50, 200))  # Color morado/demoniaco para diferenciarlo
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Atributos de combate con vida base fija e independiente
        self.vida_maxima = vida_base  # 75 HP por defecto para el enemigo básico
        self.vida = self.vida_maxima
        self.daño_contacto = 5  # Daño que le inflige al jugador al tocarlo

        # Físicas y movimiento
        self.velocidad = 2
        self.vel_y = 0
        self.gravedad = 0.5
        self.en_suelo = False

        # IA y Comportamiento
        self.rango_vision = 250  # Distancia en píxeles para empezar a seguir al jugador
        self.mirando_derecha = True

    def update(self, plataformas, jugador):
        """Actualiza la física, la IA de persecución y las colisiones del enemigo."""
        # 1. Inteligencia Artificial: Persecución basada en distancia
        distancia_x = jugador.rect.centerx - self.rect.centerx
        distancia_y = abs(jugador.rect.centery - self.rect.centery)

        movimiento_x = 0

        # Si el jugador está dentro del rango de visión horizontal y cerca en altura
        if abs(distancia_x) < self.rango_vision and distancia_y < 100:
            if distancia_x > 0:
                movimiento_x = self.velocidad
                self.mirando_derecha = True
            elif distancia_x < 0:
                movimiento_x = -self.velocidad
                self.mirando_derecha = False

        # 2. Aplicar movimiento horizontal y colisiones en X
        self.rect.x += movimiento_x
        self.gestionar_colisiones_x(plataformas)

        # 3. Aplicar gravedad y colisiones en Y
        self.vel_y += self.gravedad
        self.rect.y += self.vel_y
        self.en_suelo = False
        self.gestionar_colisiones_y(plataformas)

    def gestionar_colisiones_x(self, plataformas):
        """Maneja las colisiones horizontales con las plataformas."""
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            if self.rect.centerx < plataforma.rect.centerx:
                self.rect.right = plataforma.rect.left
            else:
                self.rect.left = plataforma.rect.right

    def gestionar_colisiones_y(self, plataformas):
        """Maneja las colisiones verticales con las plataformas y el suelo."""
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            if self.vel_y > 0:
                self.rect.bottom = plataforma.rect.top
                self.vel_y = 0
                self.en_suelo = True
            elif self.vel_y < 0:
                self.rect.top = plataforma.rect.bottom
                self.vel_y = 0

    def recibir_daño(self, cantidad, grupo_drops):
        """Resta vida al enemigo cuando recibe el impacto de una bala."""
        self.vida -= cantidad
        if self.vida <= 0:
            self.morir(grupo_drops)

    def morir(self, grupo_drops):
        """Gestiona la muerte del enemigo, liberando su alma en forma de recompensa."""
        if random.random() < 0.8:
            nuevo_drop = Drop(self.rect.centerx, self.rect.centery)
            grupo_drops.add(nuevo_drop)
            print("¡Demonio derrotado! Alma liberada con recompensa.")
        else:
            print("¡Demonio derrotado! El alma se desvaneció sin recompensa.")

        self.kill()