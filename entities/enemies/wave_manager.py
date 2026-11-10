import random
from entities.enemies.enemy import Enemy


class WaveManager:
    """Gestiona la aparición progresiva de oleadas de demonios en el juego."""

    def __init__(self):
        self.numero_oleada = 0
        self.enemigos_por_oleada = 2  # Empezamos con 2 enemigos en la primera oleada
        self.temporizador_entre_oleadas = 0
        self.en_pausa_entre_oleadas = False

    def actualizar(self, grupo_enemigos, grupo_drops, plataformas, ancho_pantalla):
        """Verifica el estado de la oleada actual y genera nuevos enemigos si es necesario."""

        # Si ya no quedan enemigos vivos en el mapa, pasamos a la siguiente oleada
        if len(grupo_enemigos) == 0:
            if not self.en_pausa_entre_oleadas:
                self.en_pausa_entre_oleadas = True
                self.temporizador_entre_oleadas = 120  # Fotogramas de espera (aprox. 2 segundos a 60 FPS)
                self.numero_oleada += 1
                print(f"¡Oleada {self.numero_oleada} superada! Preparando la siguiente...")

            # Reducimos el temporizador de espera
            if self.en_pausa_entre_oleadas:
                self.temporizador_entre_oleadas -= 1
                if self.temporizador_entre_oleadas <= 0:
                    self.iniciar_nueva_oleada(grupo_enemigos, plataformas, ancho_pantalla)
                    self.en_pausa_entre_oleadas = False

    def iniciar_nueva_oleada(self, grupo_enemigos, plataformas, ancho_pantalla):
        """Instancia los enemigos de la nueva oleada en posiciones aleatorias válidas."""
        cantidad_enemigos = self.enemigos_por_oleada + (self.numero_oleada - 1)
        print(f"--- INICIANDO OLEADA {self.numero_oleada} ({cantidad_enemigos} demonios) ---")

        for _ in range(cantidad_enemigos):
            pos_x = random.randint(100, ancho_pantalla - 100)
            pos_y = 400  # Altura base sobre la plataforma principal

            nuevo_enemigo = Enemy(pos_x, pos_y)
            grupo_enemigos.add(nuevo_enemigo)