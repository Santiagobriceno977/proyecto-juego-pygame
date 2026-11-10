import pygame
from config import ANCHO_MUNDO


def actualizar_enemigos(grupo_enemigos, grupo_plataformas, jugador):
    for enemigo in grupo_enemigos:
        enemigo.update(grupo_plataformas, jugador)


def gestionar_colisiones_enemigos(grupo_balas, grupo_enemigos, jugador, grupo_drops):
    # 1. Colisiones de balas con enemigos
    colisiones_balas = pygame.sprite.groupcollide(grupo_balas, grupo_enemigos, True, False)

    for bala, enemigos_impactados in colisiones_balas.items():
        for enemigo in enemigos_impactados:
            daño_bala = getattr(bala, "daño", 50)
            enemigo.recibir_daño(daño_bala, grupo_drops, bala_x=bala.rect.centerx)

    # 2. Colisiones de enemigos con el jugador (Daño y empuje)
    colisiones_jugador = pygame.sprite.spritecollide(jugador, grupo_enemigos, False)
    for enemigo in colisiones_jugador:
        if jugador.recibir_daño(enemigo.daño_contacto):

            # Aplicar empuje físico al jugador al tocar al enemigo
            empuje = 12 if enemigo.rect.centerx < jugador.rect.centerx else -12
            jugador.rect.x += empuje
            jugador.rect.x = max(0, min(jugador.rect.x, ANCHO_MUNDO - jugador.rect.width))
