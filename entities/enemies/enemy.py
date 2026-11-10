import pygame
import random
from entities.drop import Drop


class Enemy(pygame.sprite.Sprite):
    """Clase base para los demonios con patrullaje, persecución y retroceso (knockback)."""

    def __init__(self, x, y, vida_base=150):
        super().__init__()

        self.ancho = 32
        self.alto = 48

        self.image = pygame.Surface((self.ancho, self.alto))
        self.image.fill((180, 50, 200))  # Color morado/demoniaco
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Atributos de combate
        self.vida_maxima = vida_base
        self.vida = self.vida_maxima
        self.daño_contacto = 10

        # Físicas y movimiento
        self.velocidad_patrulla = 1.5
        self.velocidad_persecucion = 2.5
        self.vel_x = 0
        self.vel_y = 0
        self.gravedad = 0.5
        self.en_suelo = False

        # IA y Comportamiento por Estados
        self.estado = "PATRULLAR"
        self.rango_vision = 300

        # Variables de patrullaje
        self.punto_inicial_x = x
        self.limite_patrulla = 120
        self.direccion_patrulla = 1
        self.mirando_derecha = True

    def update(self, plataformas, jugador):
        """Actualiza la IA, físicas y el efecto de empuje o velocidad."""
        distancia_x = jugador.rect.centerx - self.rect.centerx
        distancia_y = abs(jugador.rect.centery - self.rect.centery)
        distancia_total = abs(distancia_x)

        # Máquina de estados
        if distancia_total <= self.rango_vision and distancia_y < 120:
            self.estado = "PERSEGUIR"
        else:
            self.estado = "PATRULLAR"

        movimiento_x = 0

        if self.estado == "PATRULLAR":
            movimiento_x = self.velocidad_patrulla * self.direccion_patrulla
            self.mirando_derecha = (self.direccion_patrulla > 0)

            if abs(self.rect.x - self.punto_inicial_x) > self.limite_patrulla:
                self.direccion_patrulla *= -1

        elif self.estado == "PERSEGUIR":
            if distancia_x > 0:
                movimiento_x = self.velocidad_persecucion
                self.mirando_derecha = True
            else:
                movimiento_x = -self.velocidad_persecucion
                self.mirando_derecha = False

        # Aplicar movimiento horizontal (sumando inercia de retroceso si la hubiera)
        self.rect.x += movimiento_x + self.vel_x
        self.gestionar_colisiones_x(plataformas)

        # Amortiguar el empuje del enemigo poco a poco
        if self.vel_x != 0:
            self.vel_x *= 0.8
            if abs(self.vel_x) < 0.2:
                self.vel_x = 0

        # Gravedad y colisiones verticales
        self.vel_y += self.gravedad
        self.rect.y += self.vel_y
        self.en_suelo = False
        self.gestionar_colisiones_y(plataformas)

    def gestionar_colisiones_x(self, plataformas):
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            if self.rect.centerx < plataforma.rect.centerx:
                self.rect.right = plataforma.rect.left
                self.direccion_patrulla = -1
            else:
                self.rect.left = plataforma.rect.right
                self.direccion_patrulla = 1

    def gestionar_colisiones_y(self, plataformas):
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            if self.vel_y > 0:
                self.rect.bottom = plataforma.rect.top
                self.vel_y = 0
                self.en_suelo = True
            elif self.vel_y < 0:
                self.rect.top = plataforma.rect.bottom
                self.vel_y = 0

    def recibir_daño(self, cantidad, grupo_drops, bala_x=None):
        """Resta vida al enemigo y le aplica un empuje en dirección opuesta al impacto."""
        self.vida -= cantidad

        if bala_x is not None:
            if self.rect.centerx < bala_x:
                self.vel_x = -5
            else:
                self.vel_x = 5
        else:
            self.vel_x = -4 if self.mirando_derecha else 4

        if self.vida <= 0:
            self.morir(grupo_drops)

    def morir(self, grupo_drops):
        if random.random() < 0.8:
            nuevo_drop = Drop(self.rect.centerx, self.rect.centery)
            grupo_drops.add(nuevo_drop)
            print("¡Demonio derrotado! Alma liberada con recompensa.")
        else:
            print("¡Demonio derrotado! El alma se desvaneció sin recompensa.")
        self.kill()