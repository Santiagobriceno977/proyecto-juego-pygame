import pygame
from config import ANCHO_MUNDO


def actualizar_enemigos(grupo_enemigos, grupo_plataformas, jugador):
    for enemigo in grupo_enemigos:
        enemigo.update(grupo_plataformas, jugador)


def gestionar_colisiones_enemigos(grupo_balas, grupo_enemigos, jugador, grupo_drops, plataformas=()):
    # 1. Colisiones de balas con enemigos
    colisiones_balas = pygame.sprite.groupcollide(grupo_balas, grupo_enemigos, True, False)

    for bala, enemigos_impactados in colisiones_balas.items():
        for enemigo in enemigos_impactados:
            daño_bala = getattr(bala, "daño", 50)
            enemigo.recibir_daño(daño_bala, grupo_drops, bala_x=bala.rect.centerx)

    # 2. Solo el zarpazo activo causa daño; el contacto por sí solo no golpea.
    for enemigo in grupo_enemigos:
        if enemigo.intentar_golpe(jugador, plataformas):
            empuje = 12 if enemigo.mirando_derecha else -12
            jugador.rect.x += empuje
            ancho = getattr(jugador, "ancho_mundo", ANCHO_MUNDO)
            jugador.rect.x = max(0, min(jugador.rect.x, ancho - jugador.rect.width))
            # El empuje tampoco puede introducir al jugador en una pared.
            for plataforma in plataformas:
                if jugador.rect.colliderect(plataforma.rect):
                    if empuje > 0:
                        jugador.rect.right = plataforma.rect.left
                    else:
                        jugador.rect.left = plataforma.rect.right
