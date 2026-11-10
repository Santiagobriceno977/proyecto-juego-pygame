import pygame
from config import ANCHO_PANTALLA, ALTO_PANTALLA, FPS
from menu import Menu
from partida import Partida


class Juego:
    """Controla las pantallas; solo JUGANDO actualiza la partida."""

    def __init__(self):
        pygame.init()
        self.ventana = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Mi juego")
        self.reloj = pygame.time.Clock()
        self.activo = True
        self.estado = "MENU"
        self.partida = None
        self.menus = {
            "MENU": Menu(ANCHO_PANTALLA, ALTO_PANTALLA),
            "NIVELES": Menu(
                ANCHO_PANTALLA, ALTO_PANTALLA, "SELECCIÓN DE NIVELES",
                (("Nivel de prueba", "INICIAR"), ("Volver", "MENU")),
                "Explora el mapa y encuentra a los enemigos.",
            ),
            "PAUSA": Menu(
                ANCHO_PANTALLA, ALTO_PANTALLA, "PAUSA",
                (("Reanudar", "REANUDAR"), ("Salir al selector", "NIVELES")),
                "La partida está detenida.",
            ),
            "GAME_OVER": Menu(
                ANCHO_PANTALLA, ALTO_PANTALLA, "GAME OVER",
                (("Reiniciar", "INICIAR"), ("Exit", "NIVELES")),
                "Exit vuelve a la selección de niveles.",
            ),
        }
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.load("assets/sounds/background_music.ogg")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except (pygame.error, FileNotFoundError) as error:
                print(f"No se pudo cargar la música de fondo: {error}")

    def _silenciar_partida(self):
        if pygame.mixer.get_init():
            pygame.mixer.pause()
            pygame.mixer.music.pause()

    def _restaurar_audio(self, descartar=False):
        if pygame.mixer.get_init():
            if descartar:
                pygame.mixer.stop()
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()

    def cambiar_estado(self, estado):
        self.estado = estado
        if estado in self.menus:
            self.menus[estado].reiniciar_seleccion()

    def iniciar_partida(self):
        # Una instancia nueva restablece jugador, inventario, mapa y encuentros.
        self.partida = Partida()
        self._restaurar_audio(descartar=True)
        self.cambiar_estado("JUGANDO")

    def pausar(self):
        if self.estado == "JUGANDO":
            self.partida.pausar()
            self._silenciar_partida()
            self.cambiar_estado("PAUSA")

    def reanudar(self):
        if self.estado == "PAUSA":
            self.partida.reanudar()
            self._restaurar_audio()
            self.cambiar_estado("JUGANDO")

    def volver_al_selector(self):
        self.partida = None
        self._restaurar_audio(descartar=True)
        self.cambiar_estado("NIVELES")

    def procesar_evento(self, evento):
        if evento.type == pygame.QUIT:
            self.activo = False
            return
        if evento.type == pygame.WINDOWFOCUSLOST:
            self.pausar()
            return
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.estado == "JUGANDO":
                self.pausar()
            elif self.estado == "PAUSA":
                self.reanudar()
            elif self.estado == "GAME_OVER":
                self.volver_al_selector()
            elif self.estado == "NIVELES":
                self.cambiar_estado("MENU")
            return

        if self.estado == "JUGANDO":
            self.partida.procesar_evento(evento)
            return

        accion = self.menus[self.estado].actualizar(evento)
        if accion == "JUGAR":
            self.cambiar_estado("NIVELES")
        elif accion == "INICIAR":
            self.iniciar_partida()
        elif accion == "REANUDAR":
            self.reanudar()
        elif accion == "NIVELES":
            self.volver_al_selector()
        elif accion == "MENU":
            self.cambiar_estado("MENU")
        elif accion == "SALIR":
            self.activo = False

    def actualizar(self):
        if self.estado == "JUGANDO":
            self.partida.actualizar()
            if self.partida.jugador.vida <= 0:
                self._silenciar_partida()
                self.cambiar_estado("GAME_OVER")

    def dibujar(self):
        if self.estado in ("JUGANDO", "PAUSA", "GAME_OVER"):
            self.partida.dibujar(self.ventana)
        if self.estado in self.menus:
            self.menus[self.estado].dibujar(
                self.ventana, superpuesto=self.estado in ("PAUSA", "GAME_OVER")
            )

    def ejecutar(self):
        try:
            while self.activo:
                for evento in pygame.event.get():
                    self.procesar_evento(evento)
                    if not self.activo:
                        break
                if not self.activo:
                    break
                self.actualizar()
                self.dibujar()
                pygame.display.flip()
                self.reloj.tick(FPS)
        finally:
            pygame.quit()


if __name__ == "__main__":
    Juego().ejecutar()
