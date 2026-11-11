# === CONFIGURACIÓN GLOBAL DEL JUEGO ===

# Pantalla visible
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

# Dimensiones del nivel actual (puedes cambiarlo fácilmente aquí: 2400, 3200, 4800, etc.)
ANCHO_MUNDO = 3200
ALTO_MUNDO = 600

# FPS objetivo (útil para hacer la física estable con dt)
FPS = 60


# ============================================================
#   SISTEMA DE ARMAS — UNA ÚNICA FUENTE DE VERDAD
# ============================================================
# Añadir un arma = añadir una línea aquí. Nada más.
# ============================================================

from dataclasses import dataclass


@dataclass
class WeaponStats:
    """Define TODO lo que una arma necesita. Los datos, no el comportamiento."""

    nombre: str
    capacidad_cargador: int
    municion_total: int
    cadencia: int          # milisegundos entre disparos
    tiempo_recarga: int    # milisegundos de recarga
    velocidad_bala: int
    daño_bala: int
    color_bala: tuple
    icono: str
    sonido_disparo: str | None = None
    sonido_recarga: str | None = None
    volumen_disparo: float = 0.25


PISTOL_STATS = WeaponStats(
    nombre="Pistola",
    capacidad_cargador=10,
    municion_total=30,
    cadencia=250,
    tiempo_recarga=1500,
    velocidad_bala=10,
    daño_bala=25,
    color_bala=(255, 255, 0),
    icono="assets/items/pistol_icon.png",
    sonido_disparo="assets/sounds/pistol_shot.wav",
    sonido_recarga="assets/sounds/pistol_reload.wav"



)

SHOTGUN_STATS = WeaponStats(
    nombre="Escopeta",
    capacidad_cargador=5,
    municion_total=20,
    cadencia=800,
    tiempo_recarga=2500,
    velocidad_bala=12,
    daño_bala=25,
    color_bala=(255, 150, 0),
    icono="assets/items/shotgun_icon.png",
    sonido_disparo="assets/sounds/shotgun_shot.wav",
    sonido_recarga="assets/sounds/shotgun_reload.wav",
    volumen_disparo=0.12,
)

METRALLETA_STATS = WeaponStats(
    nombre="Metralleta",
    capacidad_cargador=30,
    municion_total=90,
    cadencia=100,
    tiempo_recarga=1500,
    velocidad_bala=12,
    daño_bala=15,
    color_bala=(255, 255, 0),
    icono="assets/items/metralleta_icon.png",
    sonido_disparo="assets/sounds/metralleta_disparo.wav",
    sonido_recarga="assets/sounds/metralleta_reload.wav",
)


# Mapa nombre -> stats, para spawnear armas por nombre desde los niveles
ARMAS_STATS = {
    PISTOL_STATS.nombre: PISTOL_STATS,
    SHOTGUN_STATS.nombre: SHOTGUN_STATS,
    METRALLETA_STATS.nombre: METRALLETA_STATS,
}
