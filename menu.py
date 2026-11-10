import pygame


class Menu:
    """Menú reutilizable con teclado y ratón."""

    def __init__(
        self, ancho, alto, titulo="DEMON SOULS SURVIVAL",
        opciones=(("Jugar", "JUGAR"), ("Salir", "SALIR")),
        subtitulo="",
    ):
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.opciones = tuple(opciones)
        self.subtitulo = subtitulo
        self.indice_seleccionado = 0
        self.fuente_titulo = pygame.font.Font(None, 52)
        self.fuente_opciones = pygame.font.Font(None, 32)
        self.fuente_ayuda = pygame.font.Font(None, 23)
        self.botones = [
            pygame.Rect(ancho // 2 - 160, alto // 2 + indice * 64, 320, 50)
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
            velo.fill((8, 10, 18, 215))
            superficie.blit(velo, (0, 0))
        else:
            superficie.fill((15, 18, 28))

        pygame.draw.line(superficie, (230, 70, 70), (self.ancho // 2 - 36, 150),
                         (self.ancho // 2 + 36, 150), 3)
        self._texto_centrado(superficie, self.fuente_titulo, self.titulo,
                            205, (245, 90, 90))
        self._texto_centrado(superficie, self.fuente_ayuda, self.subtitulo,
                            252, (185, 192, 208))
        for indice, (etiqueta, _) in enumerate(self.opciones):
            seleccionado = indice == self.indice_seleccionado
            rect = self.botones[indice]
            pygame.draw.rect(superficie, (56, 66, 87) if seleccionado else (28, 34, 49),
                             rect, border_radius=8)
            pygame.draw.rect(superficie, (245, 100, 90) if seleccionado else (55, 65, 85),
                             rect, width=2, border_radius=8)
            self._texto_centrado(superficie, self.fuente_opciones, etiqueta,
                                rect.centery, (255, 255, 255))
        self._texto_centrado(
            superficie, self.fuente_ayuda, "Flechas / W-S y Enter · También puedes usar el ratón",
            self.alto - 65, (145, 156, 177),
        )
