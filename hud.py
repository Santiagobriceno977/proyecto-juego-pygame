import pygame


def dibujar_hud(ventana, fuente_hud, jugador):
    """Dibuja el HUD: Barras de vida y blindaje arriba, y el icono grande del arma activa abajo a la derecha."""

    # ==========================================
    # 1. BARRAS DE VIDA Y BLINDAJE (Esquina Superior Izquierda)
    # ==========================================
    pos_x_barras = 20
    pos_y_barras = 20
    ancho_barra = 150
    alto_barra = 15

    # Barra de Vida
    proporcion_vida = max(0, jugador.vida / jugador.vida_maxima)
    pygame.draw.rect(ventana, (100, 100, 100), (pos_x_barras, pos_y_barras, ancho_barra, alto_barra))
    pygame.draw.rect(
        ventana, (0, 200, 0), (pos_x_barras, pos_y_barras, ancho_barra * proporcion_vida, alto_barra)
    )

    texto_vida = fuente_hud.render(f"Vida: {int(jugador.vida)}/{jugador.vida_maxima}", True, (255, 255, 255))
    ventana.blit(texto_vida, (pos_x_barras, pos_y_barras + alto_barra + 3))

    # Barra de Blindaje
    pos_y_barras += 40
    proporcion_blindaje = max(0, jugador.blindaje / jugador.blindaje_maximo)
    pygame.draw.rect(ventana, (100, 100, 100), (pos_x_barras, pos_y_barras, ancho_barra, 10))
    pygame.draw.rect(
        ventana,
        (50, 150, 250),
        (pos_x_barras, pos_y_barras, ancho_barra * proporcion_blindaje, 10),
    )
    texto_blindaje = fuente_hud.render(f"Shield: {int(jugador.blindaje)}/{jugador.blindaje_maximo}", True,
                                       (255, 255, 255))
    ventana.blit(texto_blindaje, (pos_x_barras, pos_y_barras + 12))

    # ==========================================
    # 2. ARMA ACTIVA (ICONO GRANDE + MUNICIÓN) (Esquina Inferior Derecha)
    # ==========================================
    ancho_ventana = ventana.get_width()
    alto_ventana = ventana.get_height()

    pos_x_inv = ancho_ventana - 200
    pos_y_inv = alto_ventana - 55

    if jugador.arma_equipada:
        arma = jugador.arma_equipada

        if hasattr(arma, "icono") and arma.icono:
            icono_grande = pygame.transform.scale(arma.icono, (64, 32))
            ventana.blit(icono_grande, (pos_x_inv, pos_y_inv))

        texto_municion = f"{arma.balas_en_cargador} / {arma.municion_total}"
        superficie_municion = fuente_hud.render(texto_municion, True, (255, 255, 255))
        ventana.blit(superficie_municion, (pos_x_inv + 70, pos_y_inv + 8))
    else:
        superficie_texto = fuente_hud.render("- -", True, (180, 180, 180))
        ventana.blit(superficie_texto, (pos_x_inv, pos_y_inv + 10))