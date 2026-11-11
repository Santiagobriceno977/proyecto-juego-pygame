import pygame
from config import ANCHO_MUNDO, WeaponStats


class Bullet(pygame.sprite.Sprite):
    """Proyectil genérico. Cada arma decide cómo lo crea, pero aquí vive su física."""

    def __init__(self, x, y, direccion, velocidad, daño, color):
        super().__init__()
        self.image = pygame.Surface((8, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocidad = velocidad * direccion
        self.daño = daño

    def update(self):
        self.rect.x += self.velocidad
        if self.rect.right < 0 or self.rect.left > ANCHO_MUNDO:
            self.kill()


class BaseWeapon(pygame.sprite.Sprite):
    """Clase padre única. TODO el comportamiento común de las armas vive aquí.

    Cada arma hija solo declara qué stats usar y, si necesita,
    cómo genera sus proyectiles (sobrescribe `_proyectiles`).
    """

    def __init__(self, x, y, stats: WeaponStats):
        super().__init__()
        self.stats = stats
        self.recogida = False
        self.balas_en_cargador = stats.capacidad_cargador
        self.municion_total = stats.municion_total
        self.ultimo_disparo = -stats.cadencia  # permite el primer disparo inmediato
        self.iniciando_recarga = 0
        self.direccion = 1

        self._cargar_imagen(stats.icono, stats.color_bala)
        self.sonido_disparo = self._cargar_sonido(stats.sonido_disparo, volumen=stats.volumen_disparo)
        self.sonido_recarga = self._cargar_sonido(stats.sonido_recarga, volumen=0.3)  # 30% de volumen para recargas

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # ------------------------------------------------------------------
    # Carga auxiliar (una sola vez, con fallback seguro)
    # ------------------------------------------------------------------
    def _cargar_imagen(self, ruta, color_fallback):
        try:
            self.icono = pygame.image.load(ruta).convert_alpha()
            self.icono = pygame.transform.scale(self.icono, (30, 15))
            self.image = pygame.Surface((32, 16), pygame.SRCALPHA)
            self.image.blit(self.icono, (1, 1))
        except Exception:
            self.icono = pygame.Surface((30, 15))
            self.icono.fill(color_fallback)
            self.image = pygame.Surface((32, 16), pygame.SRCALPHA)
            self.image.fill(color_fallback)

    def _cargar_sonido(self, ruta, volumen=0.3):
        """Carga un sonido y ajusta su volumen (de 0.0 a 1.0)."""
        if not ruta:
            return None
        try:
            sonido = pygame.mixer.Sound(ruta)
            sonido.set_volume(volumen)  # <--- AQUÍ REGULAMOS EL VOLUMEN
            return sonido
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Disparo y recarga — la única implementación del juego
    # ------------------------------------------------------------------
    def disparar(self, x, y, direccion):
        """Devuelve una LISTA de proyectiles (vacía si no se puede disparar).
        x, y: punto de origen del disparo (ej. mano del jugador).
        direccion: 1 (derecha) o -1 (izquierda).
        """
        tiempo = pygame.time.get_ticks()

        if self.iniciando_recarga > 0:
            return []
        if self.balas_en_cargador <= 0:
            self.iniciar_recarga()
            return []
        if tiempo - self.ultimo_disparo < self.stats.cadencia:
            return []

        self.balas_en_cargador -= 1
        self.ultimo_disparo = tiempo
        if self.sonido_disparo:
            self.sonido_disparo.play()
        if self.balas_en_cargador <= 0:
            self.iniciar_recarga()
        return self._proyectiles(x, y, direccion)

    def _proyectiles(self, x, y, direccion):
        """Por defecto: un proyectil central. Sobrescribir para múltiples."""
        return [self._criar_bala(x, y, direccion, 0)]

    def _criar_bala(self, x, y, direccion, offset_y):
        return Bullet(x, y + offset_y, direccion, self.stats.velocidad_bala,
                      self.stats.daño_bala, self.stats.color_bala)

    def iniciar_recarga(self):
        if (self.municion_total <= 0
                or self.balas_en_cargador >= self.stats.capacidad_cargador):
            return
        if self.iniciando_recarga == 0:
            self.iniciando_recarga = pygame.time.get_ticks()
            if self.sonido_recarga:
                self.sonido_recarga.play()

    def update(self):
        """Resuelve la recarga en curso sin que nadie la empuje."""
        if self.iniciando_recarga > 0:
            tiempo = pygame.time.get_ticks()
            if tiempo - self.iniciando_recarga >= self.stats.tiempo_recarga:
                necesarias = self.stats.capacidad_cargador - self.balas_en_cargador
                if self.municion_total >= necesarias:
                    self.balas_en_cargador += necesarias
                    self.municion_total -= necesarias
                else:
                    self.balas_en_cargador += self.municion_total
                    self.municion_total = 0
                self.iniciando_recarga = 0
