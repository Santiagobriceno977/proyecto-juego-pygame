import pygame
from config import ANCHO_MUNDO



class Player(pygame.sprite.Sprite):

  def __init__(self, x, y, ancho_pantalla, alto_pantalla):
    super().__init__()

    # === SISTEMA DE INVENTARIO DE ARMAS (Ranuras fijas: 0=Pistola, 1=Escopeta, 2=Metralleta) ===
    self.inventario = [None, None, None]
    self.indice_arma_activa = 0  # Índice de qué arma estamos usando
    self.arma_equipada = None  # Referencia rápida al arma actual

    # === ATRIBUTOS DE VIDA Y BLINDAJE ===
    self.vida_maxima = 100
    self.vida = 100
    self.blindaje_maximo = 50
    self.blindaje = 50

    # Dimensiones estándar del jugador
    self.ancho = 32
    self.alto_normal = 48
    self.alto_agachado = 24

    # Superficies pre-creadas
    self.imagen_normal = pygame.Surface((self.ancho, self.alto_normal))
    self.imagen_normal.fill((0, 255, 0))

    self.imagen_agachado = pygame.Surface((self.ancho, self.alto_agachado))
    self.imagen_agachado.fill((0, 180, 0))

    self.image = self.imagen_normal
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

    self.ancho_pantalla = ancho_pantalla
    self.alto_pantalla = alto_pantalla

    # Variables de movimiento y físicas
    self.velocidad_x = 5
    self.vel_y = 0
    self.gravedad = 0.5
    self.fuerza_salto = -11
    self.en_suelo = False
    self.agachado = False

    # === ATRIBUTOS PARA EL SISTEMA DE ARMAS ===
    self.mirando_derecha = True  # Dirección inicial del jugador

  def update(self, plataformas):
    teclas = pygame.key.get_pressed()
    movimiento_x = 0

    # Determinar si se desea agachar
    tecla_abajo = teclas[pygame.K_DOWN] or teclas[pygame.K_s]

    if tecla_abajo and self.en_suelo:
      if not self.agachado:
        pie_izquierdo = self.rect.left
        pie_inferior = self.rect.bottom
        self.image = self.imagen_agachado
        self.rect = self.image.get_rect()
        self.rect.left = pie_izquierdo
        self.rect.bottom = pie_inferior
        self.agachado = True
    else:
      if self.agachado and not tecla_abajo:
        pie_izquierdo = self.rect.left
        pie_inferior = self.rect.bottom
        self.image = self.imagen_normal
        self.rect = self.image.get_rect()
        self.rect.left = pie_izquierdo
        self.rect.bottom = pie_inferior
        self.agachado = False

    velocidad_actual = self.velocidad_x / 2 if self.agachado else self.velocidad_x

    # Movimiento horizontal y actualización de la dirección en la que mira
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
      movimiento_x = -velocidad_actual
      self.mirando_derecha = False  # Está mirando a la izquierda
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
      movimiento_x = velocidad_actual
      self.mirando_derecha = True  # Está mirando a la derecha

    self.rect.x += movimiento_x
    self.gestionar_colisiones_x(plataformas)

    if (
        (teclas[pygame.K_SPACE] or teclas[pygame.K_UP])
        and self.en_suelo
        and not self.agachado
    ):
      self.vel_y = self.fuerza_salto
      self.en_suelo = False

    self.vel_y += self.gravedad
    self.rect.y += self.vel_y
    self.en_suelo = False

    self.gestionar_colisiones_y(plataformas)

    if self.rect.left < 0:
      self.rect.left = 0
    elif self.rect.right > ANCHO_MUNDO:
      self.rect.right = ANCHO_MUNDO

    if self.rect.top > self.alto_pantalla:
      self.rect.x = 100
      self.rect.y = 100
      self.vel_y = 0

  def gestionar_colisiones_x(self, plataformas):
    for plataforma in pygame.sprite.spritecollide(
        self, plataformas, False
    ):
      if self.rect.centerx < plataforma.rect.centerx:
        self.rect.right = plataforma.rect.left
      else:
        self.rect.left = plataforma.rect.right

  def gestionar_colisiones_y(self, plataformas):
    for plataforma in pygame.sprite.spritecollide(
        self, plataformas, False
    ):
      if self.vel_y > 0:
        self.rect.bottom = plataforma.rect.top
        self.vel_y = 0
        self.en_suelo = True
      elif self.vel_y < 0:
        self.rect.top = plataforma.rect.bottom
        self.vel_y = 0