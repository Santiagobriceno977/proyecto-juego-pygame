import math
import random
import pygame
from entities.drop import Drop
from entities.enemies.enemy_draw import TAMANO, dibujar_cria


class Enemy(pygame.sprite.Sprite):
    """Cría con animación procedural y combate anunciado, sin texturas.

    Los tiempos se cuentan en actualizaciones a los 60 FPS del juego; así se
    detienen junto con la partida al pausar, sin depender del reloj de pared.
    """
    PREPARACION = 24
    GOLPE = 8
    RECUPERACION = 30
    TAMBALEO = 10
    ALCANCE = 18
    ALTURA_SALTO = 32
    FUERZA_SALTO = -7

    def __init__(self, x, y, vida_base=150):
        super().__init__()
        self.ancho, self.alto = 32, 48
        # La imagen tiene margen para brazos; las colisiones siguen siendo 32x48.
        self.image = pygame.Surface(TAMANO, pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, self.ancho, self.alto)
        self.vida_maxima = vida_base
        self.vida = vida_base
        self.daño_contacto = 10  # Se aplica al zarpazo, ya no al simple contacto.
        self.velocidad_patrulla = 1.5
        self.velocidad_persecucion = 2.5
        self.vel_x = self.vel_y = 0
        self.gravedad = 0.5
        self.en_suelo = False
        self.estado = "PATRULLAR"
        self.accion = "CAMINAR"
        self.rango_vision = 300
        self.alertado_por_disparo = False
        self.punto_inicial_x = x
        self.limite_patrulla = 120
        self.direccion_patrulla = 1
        self.mirando_derecha = True
        self.fase_paso = 0.0
        self.fase_ataque = None
        self.tiempo_ataque = 0
        self.golpe_consumido = False
        self.tiempo_herido = 0
        self.espera_salto = 0
        self.direccion_salto = 0
        self._resto_x = self._resto_y = 0.0
        self._dibujar_pose()

    def _dibujar_pose(self):
        progreso = 1 - self.tiempo_herido / self.TAMBALEO if self.tiempo_herido else 0
        dibujar_cria(self.image, self.accion, self.fase_paso, progreso, self.mirando_derecha)

    def dibujar(self, superficie, camara_x=0, camara_y=0):
        destino = self.image.get_rect(midbottom=(self.rect.centerx - camara_x,
                                                self.rect.bottom - camara_y))
        superficie.blit(self.image, destino)

    def alcance_ataque(self):
        x = self.rect.centerx if self.mirando_derecha else self.rect.left - self.ALCANCE
        return pygame.Rect(x, self.rect.top + 10,
                           self.rect.width // 2 + self.ALCANCE, 30)

    def intentar_golpe(self, jugador, plataformas=()):
        """Un solo impacto por zarpazo; no golpea hacia atrás ni a través de paredes."""
        if self.vida <= 0 or self.fase_ataque != "GOLPEAR" or self.golpe_consumido:
            return False
        golpe = self.alcance_ataque()
        if not golpe.colliderect(jugador.rect):
            return False
        zona = golpe.clip(jugador.rect)
        trayectoria = pygame.Rect(min(self.rect.centerx, zona.centerx), zona.centery,
                                  max(1, abs(self.rect.centerx - zona.centerx)), 1)
        if any(p.rect.colliderect(trayectoria) for p in plataformas):
            return False
        self.golpe_consumido = True
        return jugador.recibir_daño(self.daño_contacto)

    def _avanzar_ataque(self):
        self.tiempo_ataque -= 1
        if self.tiempo_ataque <= 0:
            if self.fase_ataque == "PREPARAR":
                self.fase_ataque, self.tiempo_ataque = "GOLPEAR", self.GOLPE
            elif self.fase_ataque == "GOLPEAR":
                self.fase_ataque, self.tiempo_ataque = "RECUPERAR", self.RECUPERACION
            else:
                self.fase_ataque = None

    def _salto_seguro(self, plataformas, direccion):
        """Simula un salto corto antes de iniciarlo: techo libre y apoyo de llegada."""
        if not self.en_suelo or self.espera_salto:
            return False
        sonda = self.rect.move(direccion * 10, 0)
        obstaculos = [p.rect for p in plataformas if sonda.colliderect(p.rect)]
        if not obstaculos or any(not 0 < self.rect.bottom - r.top <= self.ALTURA_SALTO
                                for r in obstaculos):
            return False
        prueba = self.rect.copy()
        vy = self.FUERZA_SALTO
        resto_x = resto_y = 0.0
        for _ in range(60):
            resto_x += direccion * self.velocidad_persecucion
            dx = math.trunc(resto_x)
            resto_x -= dx
            prueba.x += dx
            for p in plataformas:
                if prueba.colliderect(p.rect):
                    if direccion > 0:
                        prueba.right = p.rect.left
                    else:
                        prueba.left = p.rect.right
            vy += self.gravedad
            resto_y += vy
            dy = math.trunc(resto_y)
            resto_y -= dy
            prueba.y += dy
            for p in plataformas:
                if prueba.colliderect(p.rect):
                    if vy < 0:
                        return False  # Techo bajo.
                    if vy > 0:
                        prueba.bottom = p.rect.top
                        return ((prueba.x - self.rect.x) * direccion > 8
                                and prueba.bottom <= self.rect.bottom
                                and not any(prueba.colliderect(q.rect) for q in plataformas))
        return False

    def update(self, plataformas, jugador):
        if self.vida <= 0:
            return
        plataformas = tuple(plataformas)
        self.espera_salto = max(0, self.espera_salto - 1)
        self.en_suelo = self.vel_y >= 0 and any(
            self.rect.move(0, 1).colliderect(p.rect) for p in plataformas)
        distancia_x = jugador.rect.centerx - self.rect.centerx
        distancia_y = abs(jugador.rect.centery - self.rect.centery)
        perseguir = self.alertado_por_disparo or (abs(distancia_x) <= self.rango_vision and distancia_y < 120)
        self.estado = "PERSEGUIR" if perseguir else "PATRULLAR"
        movimiento_x = 0
        if self.tiempo_herido:
            self.accion = "HERIDO"
            self.tiempo_herido -= 1
        elif self.fase_ataque:
            self._avanzar_ataque()
            self.accion = self.fase_ataque or "QUIETO"
        else:
            if perseguir:
                if distancia_x:
                    self.mirando_derecha = distancia_x > 0
                direccion = 1 if self.mirando_derecha else -1
                if self.en_suelo and self.alcance_ataque().colliderect(jugador.rect):
                    self.fase_ataque = "PREPARAR"
                    self.tiempo_ataque = self.PREPARACION
                    self.golpe_consumido = False
                    self.accion = "PREPARAR"
                else:
                    # Impulsos cortos; la velocidad media mantiene el valor anterior.
                    impulso = 1 + 0.3 * math.sin(self.fase_paso * 2)
                    movimiento_x = direccion * self.velocidad_persecucion * impulso
                    self.accion = "CORRER"
                    if self._salto_seguro(plataformas, direccion):
                        self.vel_y = self.FUERZA_SALTO
                        self._resto_y = 0
                        self.en_suelo = False
                        self.direccion_salto = direccion
                        self.espera_salto = 60
            else:
                if self.rect.x >= self.punto_inicial_x + self.limite_patrulla:
                    self.direccion_patrulla = -1
                elif self.rect.x <= self.punto_inicial_x - self.limite_patrulla:
                    self.direccion_patrulla = 1
                movimiento_x = self.velocidad_patrulla * self.direccion_patrulla
                self.mirando_derecha = self.direccion_patrulla > 0
                self.accion = "CAMINAR"
            if self.direccion_salto and not self.en_suelo:
                movimiento_x = self.direccion_salto * self.velocidad_persecucion
                self.accion = "SALTAR"
            elif self.en_suelo and movimiento_x:
                # No se lanza voluntariamente al vacío.
                adelante = self.rect.right + 3 if movimiento_x > 0 else self.rect.left - 4
                apoyo = pygame.Rect(adelante, self.rect.bottom, 1, self.ALTURA_SALTO + 8)
                if not any(apoyo.colliderect(p.rect) for p in plataformas):
                    movimiento_x = 0
                    if not perseguir:
                        self.direccion_patrulla *= -1
                    self.accion = "QUIETO"
        if movimiento_x:
            self.fase_paso += 0.24 if self.accion in ("CORRER", "SALTAR") else 0.12
        self._resto_x += movimiento_x + self.vel_x
        paso_x = math.trunc(self._resto_x)
        self._resto_x -= paso_x
        self.rect.x += paso_x
        self.gestionar_colisiones_x(plataformas, paso_x)
        self.vel_x *= 0.8
        if abs(self.vel_x) < 0.2:
            self.vel_x = 0
        self.vel_y += self.gravedad
        self._resto_y += self.vel_y
        paso_y = math.trunc(self._resto_y)
        self._resto_y -= paso_y
        self.rect.y += paso_y
        self.gestionar_colisiones_y(plataformas)
        if self.en_suelo:
            self.direccion_salto = 0
        self._dibujar_pose()

    def gestionar_colisiones_x(self, plataformas, paso_x=None):
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            derecha = paso_x > 0 if paso_x else self.rect.centerx < plataforma.rect.centerx
            if derecha:
                self.rect.right = plataforma.rect.left
                self.direccion_patrulla = -1
            else:
                self.rect.left = plataforma.rect.right
                self.direccion_patrulla = 1
            self._resto_x = 0

    def gestionar_colisiones_y(self, plataformas):
        for plataforma in pygame.sprite.spritecollide(self, plataformas, False):
            if self.vel_y > 0:
                self.rect.bottom = plataforma.rect.top
                self.vel_y = 0
                self._resto_y = 0
                self.en_suelo = True
            elif self.vel_y < 0:
                self.rect.top = plataforma.rect.bottom
                self.vel_y = 0
                self._resto_y = 0

    def recibir_daño(self, cantidad, grupo_drops, bala_x=None):
        if cantidad <= 0 or self.vida <= 0:
            return
        self.vida -= cantidad
        if bala_x is not None and self.vida > 0:
            self.alertado_por_disparo = True
            self.estado = "PERSEGUIR"
        if bala_x is not None:
            self.vel_x = -5 if self.rect.centerx < bala_x else 5
        else:
            self.vel_x = -4 if self.mirando_derecha else 4
        if self.vida <= 0:
            self.morir(grupo_drops)
        else:
            self.tiempo_herido = self.TAMBALEO
            self.fase_ataque = None  # El impacto interrumpe el zarpazo.
            self.golpe_consumido = True
            self.accion = "HERIDO"
            self._dibujar_pose()

    def morir(self, grupo_drops):
        if random.random() < 0.8:
            grupo_drops.add(Drop(self.rect.centerx, self.rect.centery))
        self.kill()
