import pygame
import sys


class Menu:
    """Gestiona la interfaz del menú principal del juego."""

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.fuente_titulo = pygame.font.Font(None, 64)
        self.fuente_opciones = pygame.font.Font(None, 36)

        # Opciones del menú
        self.opciones = ["JUGAR", "SALIR"]
        self.indice_seleccionado = 0

    def actualizar(self, evento):
        """Gestiona la navegación en el menú con las teclas de flecha y ENTER."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP or evento.key == pygame.K_w:
                self.indice_seleccionado = (self.indice_seleccionado - 1) % len(self.opciones)
            elif evento.key == pygame.K_DOWN or evento.key == pygame.K_s:
                self.indice_seleccionado = (self.indice_seleccionado + 1) % len(self.opciones)
            elif evento.key == pygame.K_RETURN:
                return self.opciones[self.indice_seleccionado]
        return None

    def dibujar(self, superficie):
        """Dibuja los elementos visuales del menú en pantalla."""
        # Fondo oscuro para el menú
        superficie.fill((20, 20, 30))

        # Título del juego
        texto_titulo = self.fuente_titulo.render("DEMON SOULS SURVIVAL", True, (255, 60, 60))
        rect_titulo = texto_titulo.get_rect(center=(self.ancho // 2, self.alto // 3))
        superficie.blit(texto_titulo, rect_titulo)

        # Opciones del menú
        for i, opcion in enumerate(self.opciones):
            # Cambiar color si la opción está seleccionada
            color = (255, 255, 0) if i == self.indice_seleccionado else (200, 200, 200)

            texto_opcion = self.fuente_opciones.render(opcion, True, color)
            rect_opcion = texto_opcion.get_rect(center=(self.ancho // 2, self.alto // 2 + i * 50))
            superficie.blit(texto_opcion, rect_opcion)