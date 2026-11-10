import pygame
from entities.weapons.pistol import Pistol
from entities.weapons.shotgun import Shotgun
from entities.weapons.metralleta import Metralleta

# Variable global para el sonido de recogida (inicialmente None)
_sonido_recoger = None


def obtener_sonido_recoger():
    """Carga el sonido de recogida de forma segura solo cuando el mezclador ya está inicializado."""
    global _sonido_recoger
    if _sonido_recoger is None:
        try:
            _sonido_recoger = pygame.mixer.Sound("assets/sounds/recoger.wav")
            _sonido_recoger.set_volume(0.5)
        except Exception as e:
            print(f"No se pudo cargar el sonido de recogida: {e}")
    return _sonido_recoger


def gestionar_eventos_teclado(evento, jugador, grupo_armas):
    """Gestiona todas las acciones de eventos discretos (KEYDOWN): recargar, cambiar arma, recoger."""
    if evento.type != pygame.KEYDOWN:
        return

    # Recargar arma activa con la tecla R
    if evento.key == pygame.K_r:
        if jugador.arma_equipada:
            jugador.arma_equipada.iniciar_recarga()

    # Recoger cualquier arma disponible con la tecla E (Ranuras fijas)
    if evento.key == pygame.K_e:
        for arma in grupo_armas:
            if jugador.rect.colliderect(arma.rect) and not arma.recogida:
                arma.recogida = True

                # === REPRODUCIR SONIDO DE RECOGIDA DE FORMA SEGURA ===
                sonido = obtener_sonido_recoger()
                if sonido:
                    sonido.play()

                if isinstance(arma, Pistol):
                    jugador.inventario[0] = arma
                    jugador.indice_arma_activa = 0
                elif isinstance(arma, Shotgun):
                    jugador.inventario[1] = arma
                    jugador.indice_arma_activa = 1
                elif isinstance(arma, Metralleta):
                    jugador.inventario[2] = arma
                    jugador.indice_arma_activa = 2

                jugador.arma_equipada = arma
                grupo_armas.remove(arma)
                break

    # Cambiar de arma con las teclas numéricas fijas (1, 2 y 3)
    if evento.key == pygame.K_1:
        if len(jugador.inventario) > 0 and jugador.inventario[0] is not None:
            jugador.arma_equipada = jugador.inventario[0]
            jugador.indice_arma_activa = 0

    elif evento.key == pygame.K_2:
        if len(jugador.inventario) > 1 and jugador.inventario[1] is not None:
            jugador.arma_equipada = jugador.inventario[1]
            jugador.indice_arma_activa = 1

    elif evento.key == pygame.K_3:
        if len(jugador.inventario) > 2 and jugador.inventario[2] is not None:
            jugador.arma_equipada = jugador.inventario[2]
            jugador.indice_arma_activa = 2



def gestionar_disparo_continuo(jugador, grupo_balas):
    """Gestiona el disparo continuo si el jugador mantiene presionada la tecla correspondiente."""
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_f] and jugador.arma_equipada:
        # Asignamos 1 si mira a la derecha, -1 si mira a la izquierda
        if jugador.mirando_derecha:
            x_bala = jugador.rect.right
            direccion = 1
        else:
            x_bala = jugador.rect.left - 10
            direccion = -1

        y_bala = jugador.rect.centery

        # Llamamos a disparar pasando los argumentos correctos
        nuevos_proyectiles = jugador.arma_equipada.disparar(x_bala, y_bala, direccion)

        if nuevos_proyectiles:
            grupo_balas.add(nuevos_proyectiles)