import pygame
from config import ANCHO_PANTALLA, ALTO_PANTALLA, ANCHO_MUNDO, ALTO_SUELO, Y_SUELO
from entities.game_platform import Platform
from entities.player import Player
from entities.weapons.pistol import Pistol
from entities.weapons.shotgun import Shotgun
from entities.weapons.metralleta import Metralleta
from entities.enemies.enemy_handler import actualizar_enemigos, gestionar_colisiones_enemigos
from entities.enemies.spawn_manager import SpawnManager
from levels.nivel_prueba import cargar_nivel_prueba, ZONAS_ENEMIGOS
from hud import HUD
from input_handler import gestionar_eventos_teclado, gestionar_disparo_continuo
from fuentes import cargar_fuente


class Partida:
    """Estado completo de un intento del nivel de prueba."""

    def __init__(self):
        self.grupo_plataformas = pygame.sprite.Group()
        self.grupo_obstaculos = pygame.sprite.Group()
        self.grupo_armas = pygame.sprite.Group()
        self.grupo_balas = pygame.sprite.Group()
        self.grupo_drops = pygame.sprite.Group()
        self.grupo_enemigos = pygame.sprite.Group()
        self.suelo = Platform(
            0, Y_SUELO, ANCHO_MUNDO, ALTO_SUELO,
            ruta_imagen="assets/items/suelo_tile.png",
        )
        cargar_nivel_prueba(
            self.grupo_plataformas, self.grupo_obstaculos, self.suelo.rect.top)
        self.grupo_plataformas.add(self.suelo)
        self.jugador = Player(50, 0, ANCHO_PANTALLA, ALTO_PANTALLA)
        self.jugador.rect.bottom = self.suelo.rect.top
        self.jugador.en_suelo = True
        for tipo, x in ((Pistol, 150), (Shotgun, 200), (Metralleta, 100)):
            arma = tipo(x, 0)
            arma.rect.bottom = self.suelo.rect.top
            self.grupo_armas.add(arma)
        self.spawn_manager = SpawnManager(ZONAS_ENEMIGOS, self.suelo.rect.top)
        self.instante_pausa = None
        self.fuente_hud = cargar_fuente(28)
        self.hud = HUD()
        try:
            fondo = pygame.image.load("assets/background.png").convert()
            self.imagen_fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
        except (pygame.error, FileNotFoundError):
            self.imagen_fondo = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
            self.imagen_fondo.fill((30, 30, 40))

    def pausar(self):
        if self.instante_pausa is None:
            self.instante_pausa = pygame.time.get_ticks()

    def reanudar(self):
        if self.instante_pausa is None:
            return
        duracion = pygame.time.get_ticks() - self.instante_pausa
        self.jugador.ultimo_daño += duracion
        armas = set(self.grupo_armas)
        armas.update(arma for arma in self.jugador.inventario if arma is not None)
        if self.jugador.arma_equipada is not None:
            armas.add(self.jugador.arma_equipada)
        for arma in armas:
            arma.ultimo_disparo += duracion
            if arma.iniciando_recarga > 0:
                arma.iniciando_recarga += duracion
        self.instante_pausa = None

    def procesar_evento(self, evento):
        if self.instante_pausa is None and self.jugador.vida > 0:
            gestionar_eventos_teclado(evento, self.jugador, self.grupo_armas)

    def actualizar(self):
        if self.instante_pausa is not None or self.jugador.vida <= 0:
            return
        gestionar_disparo_continuo(self.jugador, self.grupo_balas)
        self.jugador.update(self.grupo_plataformas)
        if self.jugador.arma_equipada:
            self.jugador.arma_equipada.update()
        self.grupo_balas.update()
        self.grupo_armas.update()
        self.spawn_manager.actualizar(self.jugador, self.grupo_enemigos)
        actualizar_enemigos(self.grupo_enemigos, self.grupo_plataformas, self.jugador)
        gestionar_colisiones_enemigos(
            self.grupo_balas, self.grupo_enemigos, self.jugador, self.grupo_drops
        )
        # Un drop de vida no puede revivir al jugador tras un golpe mortal.
        if self.jugador.vida <= 0:
            return
        for drop in pygame.sprite.spritecollide(self.jugador, self.grupo_drops, True):
            drop.aplicar_efecto(self.jugador)

    def dibujar(self, ventana):
        camara_x = max(0, min(
            self.jugador.rect.centerx - ANCHO_PANTALLA // 3,
            ANCHO_MUNDO - ANCHO_PANTALLA,
        ))
        ventana.blit(self.imagen_fondo, (0, 0))
        for grupo in (
            self.grupo_plataformas, self.grupo_obstaculos, self.grupo_armas,
            self.grupo_balas, self.grupo_enemigos, self.grupo_drops,
        ):
            for entidad in grupo:
                ventana.blit(entidad.image, (entidad.rect.x - camara_x, entidad.rect.y))
        for arma in self.grupo_armas:
            if self.jugador.rect.colliderect(arma.rect.inflate(40, 40)):
                texto = self.fuente_hud.render("[E]", True, (255, 255, 0))
                ventana.blit(texto, (arma.rect.x - camara_x - 10, arma.rect.y - 25))
        ventana.blit(self.jugador.image, (self.jugador.rect.x - camara_x, self.jugador.rect.y))
        self.hud.dibujar(ventana, self.jugador)
        ayuda = self.fuente_hud.render("Esc · Pausa", True, (230, 230, 240))
        ventana.blit(ayuda, (ANCHO_PANTALLA - ayuda.get_width() - 20, 92))


