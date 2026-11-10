import pygame
from fuentes import cargar_fuente


FONDO = (10, 17, 24, 235)
BORDE = (48, 77, 88)
TEXTO = (225, 238, 240)
APAGADO = (136, 159, 168)
CIAN = (85, 210, 225)
VERDE = (110, 225, 173)
ROJO = (255, 105, 95)
AMBAR = (245, 190, 90)


class HUD:
    """Interfaz de la terminal de Hope: solo muestra el estado real de la partida."""

    def __init__(self):
        self.fuente = cargar_fuente(22)
        self.pequena = cargar_fuente(19)
        self.retro = cargar_fuente(28, retro=True)
        self.numero = cargar_fuente(44, retro=True)

    def _texto(self, superficie, texto, posicion, color=TEXTO, fuente=None):
        imagen = (fuente or self.fuente).render(texto, True, color)
        superficie.blit(imagen, posicion)
        return imagen.get_width()

    def _panel(self, superficie, rect, acento=CIAN):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill(FONDO)
        superficie.blit(panel, rect)
        pygame.draw.rect(superficie, BORDE, rect, width=1)
        pygame.draw.line(superficie, acento, rect.topleft, (rect.left + 34, rect.top), 3)
        pygame.draw.line(superficie, acento, (rect.right - 34, rect.bottom - 1),
                         (rect.right - 1, rect.bottom - 1), 2)

    def _medidor(self, superficie, etiqueta, valor, maximo, x, y, color):
        valor_visible = max(0, min(int(valor), int(maximo)))
        proporcion = valor_visible / maximo if maximo > 0 else 0
        self._texto(superficie, etiqueta, (x, y), APAGADO, self.pequena)
        numero = self.fuente.render(f"{valor_visible:03d} / {int(maximo):03d}", True, color)
        superficie.blit(numero, (x + 270 - numero.get_width(), y - 2))
        for indice in range(20):
            rect = pygame.Rect(x + indice * 13.5, y + 28, 10, 7)
            pygame.draw.rect(superficie, (30, 47, 55), rect)
            relleno = min(1, max(0, proporcion * 20 - indice))
            if relleno:
                pygame.draw.rect(superficie, color,
                                 (rect.x, rect.y, max(1, round(rect.width * relleno)), rect.height))

    def dibujar(self, ventana, jugador):
        ancho, alto = ventana.get_size()
        self._panel(ventana, pygame.Rect(16, 16, 304, 148))
        self._texto(ventana, "HOPE // SOPORTE TÁCTICO", (32, 24), CIAN, self.retro)
        self._texto(ventana, "JHAN · OPERADOR", (32, 54), APAGADO, self.pequena)
        color_vida = ROJO if jugador.vida <= jugador.vida_maxima * 0.25 else VERDE
        self._medidor(ventana, "VIDA", jugador.vida, jugador.vida_maxima,
                      32, 78, color_vida)
        self._medidor(ventana, "BLINDAJE", jugador.blindaje, jugador.blindaje_maximo,
                      32, 119, CIAN)

        self._inventario(ventana, jugador, alto)
        self._arma(ventana, jugador, ancho, alto)

    def _inventario(self, ventana, jugador, alto):
        self._texto(ventana, "EQUIPO", (16, alto - 104), APAGADO, self.pequena)
        for indice, arma in enumerate(jugador.inventario):
            rect = pygame.Rect(16 + indice * 66, alto - 76, 58, 60)
            activa = arma is not None and arma is jugador.arma_equipada
            color = CIAN if activa else BORDE
            self._panel(ventana, rect, color)
            pygame.draw.rect(ventana, color, rect, width=2 if activa else 1)
            self._texto(ventana, str(indice + 1), (rect.x + 6, rect.y + 2),
                        CIAN if activa else APAGADO, self.pequena)
            if arma is not None and getattr(arma, "icono", None) is not None:
                icono = pygame.transform.scale(arma.icono, (40, 20))
                ventana.blit(icono, (rect.x + 9, rect.y + 29))
            else:
                pygame.draw.line(ventana, BORDE, (rect.x + 23, rect.y + 40),
                                 (rect.x + 35, rect.y + 40), 2)

    def _arma(self, ventana, jugador, ancho, alto):
        rect = pygame.Rect(ancho - 322, alto - 140, 306, 124)
        self._panel(ventana, rect)
        x, y = rect.x + 16, rect.y + 10
        arma = jugador.arma_equipada
        self._texto(ventana, "SISTEMA DE ARMAS", (x, y), APAGADO, self.pequena)
        if arma is None:
            self._texto(ventana, "SIN ARMA", (x, y + 27), TEXTO, self.retro)
            self._texto(ventana, "E · Recoger un arma cercana", (x, y + 69), APAGADO)
            return

        self._texto(ventana, arma.stats.nombre.upper(), (x, y + 25), CIAN, self.retro)
        icono = getattr(arma, "icono", None)
        if icono is not None:
            ventana.blit(pygame.transform.scale(icono, (64, 32)), (x + 196, y + 26))

        recargando = arma.iniciando_recarga > 0
        color = AMBAR if recargando else (ROJO if arma.balas_en_cargador == 0 else TEXTO)
        self._texto(ventana, f"{arma.balas_en_cargador:02d}", (x, y + 55), color, self.numero)
        self._texto(ventana, f"/ {arma.municion_total:03d}", (x + 56, y + 68), APAGADO)
        if recargando:
            estado = "RECARGANDO"
        elif arma.balas_en_cargador == 0:
            estado = "SIN MUNICIÓN" if arma.municion_total <= 0 else "R · RECARGAR"
        else:
            estado = "R · RECARGAR"
        self._texto(ventana, estado, (x + 142, y + 72), color, self.pequena)
