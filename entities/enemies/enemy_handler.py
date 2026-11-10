import pygame


def actualizar_enemigos(grupo_enemigos, plataformas, jugador):
    """Actualiza el movimiento, la IA y las físicas de todos los enemigos en lote."""
    for enemigo in grupo_enemigos:
        enemigo.update(plataformas, jugador)


def gestionar_colisiones_enemigos(grupo_balas, grupo_enemigos, jugador, grupo_drops):
    """Gestiona las colisiones de las balas con los enemigos y de los enemigos con el jugador."""

    # 1. Colisión entre Balas y Enemigos
    # groupcollide(kill1=True, kill2=False): la bala se consume, el enemigo se actualiza.
    colisiones_balas = pygame.sprite.groupcollide(
        grupo_balas, grupo_enemigos, True, False
    )

    for bala, enemigos_impactados in colisiones_balas.items():
        daño = getattr(bala, "daño", 25)  # la bala lleva su propio daño
        for enemigo in enemigos_impactados:
            enemigo.recibir_daño(daño, grupo_drops)

    # 2. Colisión entre el Jugador y los Enemigos
    enemigos_tocados = pygame.sprite.spritecollide(jugador, grupo_enemigos, False)

    if enemigos_tocados:
        for enemigo in enemigos_tocados:
            if jugador.blindaje > 0:
                jugador.blindaje -= 1
                if jugador.blindaje < 0:
                    jugador.blindaje = 0
            else:
                jugador.vida -= 1
                if jugador.vida < 0:
                    jugador.vida = 0