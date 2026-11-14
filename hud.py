from pathlib import Path
import pygame
from fuentes import cargar_fuente


AMBAR = (255, 199, 35)


class HUD:
    """Panel superior de Hope, con los valores actuales del jugador."""

    def __init__(self):
        ruta = Path(__file__).resolve().parent / "assets" / "ui" / "hud_frame.png"
        self.marco = pygame.transform.scale(
            pygame.image.load(str(ruta)).convert_alpha(), (768, 72))
        self.fuente = cargar_fuente(34, retro=True)
        self.fuente_arma = cargar_fuente(28, retro=True)
        self.fuente_estado = cargar_fuente(18, retro=True)
        self._iconos = {}

    @staticmethod
    def _porcentaje(valor, maximo):
        return round(max(0, min(1, valor / maximo)) * 100) if maximo > 0 else 0

    def _texto(self, panel, texto, fuente, rect):
        imagen = fuente.render(texto, False, AMBAR)
        if imagen.get_width() > rect.width:
            escala = rect.width / imagen.get_width()
            imagen = pygame.transform.scale(
                imagen, (rect.width, max(1, round(imagen.get_height() * escala))))
        panel.blit(imagen, imagen.get_rect(center=rect.center))

    def _icono(self, original):
        if original not in self._iconos:
            # Conserva la silueta y la transparencia del arma con el color del HUD.
            silueta = pygame.mask.from_surface(original).to_surface(
                setcolor=(*AMBAR, 255), unsetcolor=(0, 0, 0, 0))
            limites = silueta.get_bounding_rect()
            if limites.width and limites.height:
                silueta = silueta.subsurface(limites).copy()
                escala = min(156 / limites.width, 38 / limites.height)
                silueta = pygame.transform.scale(
                    silueta, (max(1, round(limites.width * escala)),
                              max(1, round(limites.height * escala))))
            self._iconos[original] = silueta
        return self._iconos[original]

    def dibujar(self, ventana, jugador):
        panel = self.marco.copy()
        hp = self._porcentaje(jugador.vida, jugador.vida_maxima)
        ap = self._porcentaje(jugador.blindaje, jugador.blindaje_maximo)
        self._texto(panel, f"HP {hp}%", self.fuente, pygame.Rect(107, 14, 134, 44))
        self._texto(panel, f"AP {ap}%", self.fuente, pygame.Rect(257, 14, 128, 44))

        arma = jugador.arma_equipada
        nombre = arma.stats.nombre.upper() if arma else "SIN ARMA"
        municion = f"{arma.balas_en_cargador:02d} / {arma.municion_total:02d}" if arma else "-- / --"
        self._texto(panel, nombre, self.fuente_arma, pygame.Rect(608, 7, 146, 27))
        self._texto(panel, municion, self.fuente_arma, pygame.Rect(608, 36, 146, 28))
        if arma:
            original = getattr(arma, "icono", None)
            if original is not None:
                icono = self._icono(original)
                panel.blit(icono, icono.get_rect(center=(508, 31)))
            if arma.iniciando_recarga > 0:
                self._texto(panel, "RECARGANDO", self.fuente_estado,
                            pygame.Rect(425, 50, 166, 18))

        ancho = min(768, max(1, ventana.get_width() - 32))
        if ancho != 768:
            panel = pygame.transform.scale(panel, (ancho, max(1, round(72 * ancho / 768))))
        ventana.blit(panel, ((ventana.get_width() - ancho) // 2, 12))
