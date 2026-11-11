from pathlib import Path
import pygame
from fuentes import cargar_fuente


class Menu:
    """Menú reutilizable con teclado y ratón."""

    def __init__(
        self, ancho, alto, titulo="DEMON SOULS SURVIVAL",
        opciones=(("Iniciar Partida", "JUGAR"), ("Controles", "CONTROLES"), ("Salir", "SALIR")),
        subtitulo="",
        controles=False,
    ):
        self.controles = controles
        assets = Path(__file__).resolve().parent / "assets" / "ui"
        self.fondo = pygame.transform.scale(pygame.image.load(str(assets / "menu_background.png")).convert(), (ancho, alto))
        self.boton = pygame.image.load(str(assets / "menu_button.png")).convert_alpha()
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.opciones = tuple(opciones)
        self.subtitulo = subtitulo
        self.indice_seleccionado = 0
        self.fuente_titulo = cargar_fuente(64, retro=True)
        self.fuente_opciones = cargar_fuente(30, retro=True)
        self.fuente_ayuda = cargar_fuente(26)
        self.botones = [
            pygame.Rect(40, (490 if controles else 250) + indice * 60, 240, 40)
            for indice in range(len(self.opciones))
        ]

    def reiniciar_seleccion(self):
        self.indice_seleccionado = 0

    def actualizar(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.indice_seleccionado = (self.indice_seleccionado - 1) % len(self.opciones)
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.indice_seleccionado = (self.indice_seleccionado + 1) % len(self.opciones)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.opciones[self.indice_seleccionado][1]
        elif evento.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            for indice, rect in enumerate(self.botones):
                if rect.collidepoint(evento.pos):
                    self.indice_seleccionado = indice
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        return self.opciones[indice][1]
        return None

    def _texto_centrado(self, superficie, fuente, texto, y, color):
        imagen = fuente.render(texto, True, color)
        superficie.blit(imagen, imagen.get_rect(center=(self.ancho // 2, y)))

    def dibujar(self, superficie, superpuesto=False):
        if superpuesto:
            velo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            velo.fill((8, 10, 18, 200))
            superficie.blit(velo, (0, 0))
        else:
            superficie.blit(self.fondo, (0, 0))
        superficie.blit(self.fuente_titulo.render(self.titulo, True, (0, 0, 0)), (42, 82))
        superficie.blit(self.fuente_titulo.render(self.titulo, True, (240, 240, 225)), (40, 80))
        if self.subtitulo:
            superficie.blit(self.fuente_ayuda.render(self.subtitulo, True, (210, 215, 210)), (40, 170))
        if self.controles:
            panel = pygame.Surface((700, 285), pygame.SRCALPHA)
            panel.fill((5, 12, 17, 225))
            superficie.blit(panel, (32, 180))
            filas = (("A / D o flechas izquierda / derecha", "Moverse"),
                     ("Espacio o flecha arriba", "Saltar"),
                     ("S o flecha abajo", "Agacharse"), ("F", "Disparar"),
                     ("R", "Recargar"), ("E", "Recoger arma"),
                     ("1 / 2 / 3", "Cambiar arma"), ("Esc", "Pausar / reanudar"))
            for i, (tecla, accion) in enumerate(filas):
                superficie.blit(self.fuente_ayuda.render(tecla, True, (245, 187, 98)), (48, 190 + i * 32))
                superficie.blit(self.fuente_ayuda.render(accion, True, (225, 230, 225)), (500, 190 + i * 32))
        for i, (etiqueta, _) in enumerate(self.opciones):
            rect = self.botones[i]
            superficie.blit(self.boton, rect)
            activo = i == self.indice_seleccionado
            if activo:
                pygame.draw.rect(superficie, (245, 185, 88), rect.inflate(-4, -4), 1)
            texto = self.fuente_opciones.render(etiqueta, True, (255, 211, 130) if activo else (225, 230, 220))
            superficie.blit(texto, texto.get_rect(center=(rect.centerx + 10, rect.centery + 2)))
