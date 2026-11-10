from entities.game_platform import Platform
from entities.elementos_nivel import Caja, Escombro

def cargar_nivel_prueba(grupo_plataformas, grupo_obstaculos):
    """
    Carga los elementos de prueba (plataformas, cajas y escombros)
    para experimentar con la jugabilidad y las físicas.
    """
    # Lista ampliada con todas las plataformas y elementos de prueba
    datos_nivel = [
        # --- Plataformas flotantes originales ---
        {"tipo": "plataforma", "x": 250, "y": 440, "ancho": 120, "alto": 20},
        {"tipo": "plataforma", "x": 450, "y": 340, "ancho": 160, "alto": 20},
        {"tipo": "plataforma", "x": 700, "y": 260, "ancho": 180, "alto": 20},

        # --- Nuevas plataformas añadidas para extender el nivel ---
        {"tipo": "plataforma", "x": 950, "y": 320, "ancho": 140, "alto": 20},
        {"tipo": "plataforma", "x": 1180, "y": 400, "ancho": 160, "alto": 20},
        {"tipo": "plataforma", "x": 1400, "y": 280, "ancho": 120, "alto": 20},

        # --- Cajas de prueba para obstáculos o coberturas ---
        {"tipo": "caja", "x": 300, "y": 400, "ancho": 40, "alto": 40},
        {"tipo": "caja", "x": 500, "y": 300, "ancho": 40, "alto": 40},
        {"tipo": "caja", "x": 1220, "y": 360, "ancho": 40, "alto": 40},

        # --- Escombros distribuidos en el suelo ---
        {"tipo": "escombro", "x": 550, "y": 516, "ancho": 90, "alto": 20},
        {"tipo": "escombro", "x": 1050, "y": 516, "ancho": 100, "alto": 20},
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