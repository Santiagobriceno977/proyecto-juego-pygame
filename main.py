import sys
import pygame
from config import ANCHO_PANTALLA, ALTO_PANTALLA, ANCHO_MUNDO
from entities.game_platform import Platform
from entities.player import Player
from entities.weapons.pistol import Pistol
from entities.weapons.shotgun import Shotgun
from entities.weapons.metralleta import Metralleta
from entities.enemies.enemy_handler import actualizar_enemigos, gestionar_colisiones_enemigos
from entities.enemies.wave_manager import WaveManager
from hud import dibujar_hud
from input_handler import gestionar_eventos_teclado, gestionar_disparo_continuo
from menu import Menu  # Importamos nuestro nuevo módulo de menú

# 1. Inicialización
pygame.init()
pygame.mixer.init()
ventana = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Mi juego")
reloj = pygame.time.Clock()
FPS = 60

# Estado inicial del juego ("MENU" o "JUGANDO")
estado_juego = "MENU"
menu_principal = Menu(ANCHO_PANTALLA, ALTO_PANTALLA)

# === CARGA DE MÚSICA DE FONDO ===
try:
    pygame.mixer.music.load("assets/sounds/background_music.ogg")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"No se pudo cargar la música de fondo: {e}")

# === CARGA DE LA IMAGEN DE FONDO ===
try:
    imagen_fondo = pygame.image.load("assets/background.png").convert()
    imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
except Exception as e:
    imagen_fondo = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    imagen_fondo.fill((30, 30, 40))

fuente_hud = pygame.font.Font(None, 24)

# Inicializar elementos del juego (listos para cuando comience la partida)
grupo_plataformas = pygame.sprite.Group()
todas_las_entidades = pygame.sprite.Group()
grupo_armas = pygame.sprite.Group()
grupo_balas = pygame.sprite.Group()
grupo_drops = pygame.sprite.Group()
grupo_enemigos = pygame.sprite.Group()

wave_manager = WaveManager()
jugador = Player(50, 480, ANCHO_PANTALLA, ALTO_PANTALLA)
suelo = Platform(0, 536, ANCHO_MUNDO, 64, ruta_imagen="assets/items/suelo_tile.png")

arma_metralleta = Metralleta(100, 480)
arma_suelo = Pistol(150, 480)
arma_escopeta = Shotgun(200, 480)
grupo_armas.add(arma_suelo, arma_escopeta, arma_metralleta)

grupo_plataformas.add(suelo)
todas_las_entidades.add(jugador, suelo)

# 3. Bucle principal del juego
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if estado_juego == "MENU":
            # Si estamos en el menú, delegamos los eventos al objeto Menu
            accion = menu_principal.actualizar(evento)
            if accion == "JUGAR":
                estado_juego = "JUGANDO"
            elif accion == "SALIR":
                pygame.quit()
                sys.exit()

        elif estado_juego == "JUGANDO":
            # Delegamos los eventos de teclado al jugador y armas
            gestionar_eventos_teclado(evento, jugador, grupo_armas)

    if estado_juego == "MENU":
        # Dibujar las opciones del menú principal
        menu_principal.dibujar(ventana)

    elif estado_juego == "JUGANDO":
        # === LÓGICA DE LA PARTIDA ===
        gestionar_disparo_continuo(jugador, grupo_balas)
        jugador.update(grupo_plataformas)

        if jugador.arma_equipada:
            jugador.arma_equipada.update()

        grupo_balas.update()
        grupo_armas.update()   # las armas resuelven su recarga por sí mismas
        grupo_balas.update()

        actualizar_enemigos(grupo_enemigos, grupo_plataformas, jugador)
        gestionar_colisiones_enemigos(grupo_balas, grupo_enemigos, jugador, grupo_drops)
        wave_manager.actualizar(grupo_enemigos, grupo_drops, grupo_plataformas, ANCHO_MUNDO)

        drops_recogidos = pygame.sprite.spritecollide(jugador, grupo_drops, True)
        for drop in drops_recogidos:
            drop.aplicar_efecto(jugador)

        # === CÁLCULO DE LA CÁMARA ===
        camara_x = jugador.rect.centerx - ANCHO_PANTALLA // 3
        if camara_x < 0:
            camara_x = 0
        elif camara_x > ANCHO_MUNDO - ANCHO_PANTALLA:
            camara_x = ANCHO_MUNDO - ANCHO_PANTALLA

        # === DIBUJAR JUEGO CON CÁMARA ===
        ventana.blit(imagen_fondo, (0, 0))

        for plataforma in grupo_plataformas:
            ventana.blit(plataforma.image, (plataforma.rect.x - camara_x, plataforma.rect.y))

        for arma in grupo_armas:
            ventana.blit(arma.image, (arma.rect.x - camara_x, arma.rect.y))
            area_proximidad = arma.rect.inflate(40, 40)
            if jugador.rect.colliderect(area_proximidad):
                texto_e = fuente_hud.render("[E]", True, (255, 255, 0))
                ventana.blit(texto_e, (arma.rect.x - camara_x - 10, arma.rect.y - 25))

        for bala in grupo_balas:
            ventana.blit(bala.image, (bala.rect.x - camara_x, bala.rect.y))

        for enemigo in grupo_enemigos:
            ventana.blit(enemigo.image, (enemigo.rect.x - camara_x, enemigo.rect.y))

        for drop in grupo_drops:
            ventana.blit(drop.image, (drop.rect.x - camara_x, drop.rect.y))

        ventana.blit(jugador.image, (jugador.rect.x - camara_x, jugador.rect.y))
        dibujar_hud(ventana, fuente_hud, jugador)

    pygame.display.flip()
    reloj.tick(FPS)