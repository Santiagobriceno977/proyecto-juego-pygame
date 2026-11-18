# Crías básicas provisionales

Se dibujan con `pygame.draw` en `entities/enemies/enemy_draw.py`; no necesitan
PNG ni hojas de sprites. La imagen de 80 × 64 tiene márgenes para brazos y aviso,
pero el cuerpo conserva su rectángulo de colisión de 32 × 48. El dibujo se ancla
por los pies, incluyendo el desplazamiento de la cámara del nivel de Tiled.

## Comportamiento

- Patrulla encorvada con brazos caídos y pasos alternados.
- Al detectar al jugador corre a tirones, alrededor de la velocidad anterior.
- Si sobrevive a un disparo mantiene la persecución hasta morir o reiniciar.
- Cerca del jugador se detiene, levanta un brazo y muestra un aviso ámbar.
- El zarpazo conserva la dirección elegida al prepararlo. Se puede esquivar
  retrocediendo, saltando o pasando detrás; no atraviesa paredes.
- Un disparo interrumpe el zarpazo y provoca tambaleo con retroceso.
- Salta obstáculos de hasta 32 px solo si la trayectoria simulada no toca un
  techo y encuentra una superficie de llegada. No es navegación entre plataformas.
- Evita avanzar voluntariamente hacia caídas mayores de unos 32 px; el retroceso
  de un disparo todavía puede empujarlo por un borde.

## Ajustes en Enemy

Los tiempos se cuentan en actualizaciones del juego a 60 FPS y se congelan en pausa.

| Constante | Valor | Efecto |
|---|---:|---|
| PREPARACION | 24 | 0,4 s de aviso antes del golpe |
| GOLPE | 8 | Ventana activa de unos 0,13 s |
| RECUPERACION | 30 | 0,5 s sin atacar ni avanzar |
| TAMBALEO | 10 | Reacción de unos 0,17 s al impacto |
| ALCANCE | 18 | Píxeles por delante del cuerpo |
| ALTURA_SALTO | 32 | Altura máxima del obstáculo |
| FUERZA_SALTO | -7 | Velocidad vertical inicial |

Cada zarpazo puede aplicar 10 puntos de daño una sola vez y respeta la inmunidad
del jugador. El simple contacto ya no causa daño. La muerte y los drops mantienen
su funcionamiento; no se añade animación de muerte en esta versión.
