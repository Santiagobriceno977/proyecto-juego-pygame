from config import Y_SUELO
from entities.game_platform import Platform
from entities.elementos_nivel import Caja, Escombro
from entities.enemies.spawn_manager import ZonaEnemigos


# Coordenadas del mundo, independientes del desplazamiento de la cámara.
# Cada zona se activa una vez al alcanzar activar_en_x con el centro del jugador.
# y=None alinea los pies con el suelo, independientemente del alto del enemigo.
# Un valor numérico de y sigue indicando su esquina superior izquierda.
ZONAS_ENEMIGOS = (
    ZonaEnemigos(300, ((650, None), (900, None))),
    ZonaEnemigos(1000, ((1320, None), (1500, None))),
    ZonaEnemigos(1800, ((2100, None), (2300, None))),
    ZonaEnemigos(2500, ((2800, None), (3000, None))),
)


def cargar_nivel_prueba(grupo_plataformas, grupo_obstaculos, suelo_y=Y_SUELO):
    """
    Carga los elementos de prueba (plataformas, cajas y escombros)
    para experimentar con la jugabilidad y las físicas.
    """
    # Alturas relativas a la superficie: mantiene saltos y apoyos al cambiar el suelo.
    datos_nivel = [
        # --- Plataformas flotantes originales ---
        {"tipo": "plataforma", "x": 250, "y": suelo_y - 96, "ancho": 120, "alto": 20},
        {"tipo": "plataforma", "x": 450, "y": suelo_y - 196, "ancho": 160, "alto": 20},
        {"tipo": "plataforma", "x": 700, "y": suelo_y - 276, "ancho": 180, "alto": 20},

        # --- Nuevas plataformas añadidas para extender el nivel ---
        {"tipo": "plataforma", "x": 950, "y": suelo_y - 216, "ancho": 140, "alto": 20},
        {"tipo": "plataforma", "x": 1180, "y": suelo_y - 136, "ancho": 160, "alto": 20},
        {"tipo": "plataforma", "x": 1400, "y": suelo_y - 256, "ancho": 120, "alto": 20},

        # --- Cajas de prueba para obstáculos o coberturas ---
        {"tipo": "caja", "x": 300, "y": suelo_y - 136, "ancho": 40, "alto": 40},
        {"tipo": "caja", "x": 500, "y": suelo_y - 236, "ancho": 40, "alto": 40},
        {"tipo": "caja", "x": 1220, "y": suelo_y - 176, "ancho": 40, "alto": 40},

        # --- Escombros distribuidos en el suelo ---
        {"tipo": "escombro", "x": 550, "y": suelo_y - 20, "ancho": 90, "alto": 20},
        {"tipo": "escombro", "x": 1050, "y": suelo_y - 20, "ancho": 100, "alto": 20},
    ]

    # Iteramos sobre los datos para instanciar y agregar cada objeto a su grupo correspondiente
    for item in datos_nivel:
        if item["tipo"] == "plataforma":
            plat = Platform(item["x"], item["y"], item["ancho"], item["alto"])
            grupo_plataformas.add(plat)
        elif item["tipo"] == "caja":
            caja = Caja(item["x"], item["y"], item["ancho"], item["alto"])
            grupo_obstaculos.add(caja)
        elif item["tipo"] == "escombro":
            escombro = Escombro(item["x"], item["y"], item["ancho"], item["alto"])
            grupo_obstaculos.add(escombro)
