# Nivel 01 en Tiled

En el juego: Iniciar Partida → Nivel 01 · Tierra.

Abre `nivel_01.tmx` en Tiled. Guarda los cambios y reinicia el intento para
recargarlos; no hace falta exportar a JSON. Conserva juntos el TMX, `tierra.tsx`
y `1794978491787.png`. Las rutas son relativas a cada archivo.

El mapa mide 100 × 19 casillas de 32 × 32 px: 3200 × 608 px.
Las tres filas inferiores forman 96 px de suelo. La cámara se desplaza 8 px
verticalmente para mostrar el fondo del mapa dentro de la ventana de 800 × 600.
La textura se repite a 32 × 32 sin ampliarla.

El cargador lee capas de patrones CSV y rectángulos de colisión del tileset.
Un tile sin rectángulo es decorativo. Los rectángulos contiguos se unen por
fila; las casillas vacías no tienen colisión. Se admiten varios tiles y capas.
Por ahora no se admiten mapas infinitos, capas de objetos, grupos, imágenes de
fondo de Tiled, tiles girados/volteados, animaciones ni colisiones poligonales.
Estas variantes muestran un error en vez de cargarse con colisiones incorrectas.

Las posiciones horizontales de jugador, armas y encuentros siguen en el código;
su altura se calcula a partir de las colisiones del mapa. Mantén suelo bajo esas
posiciones mientras no se implemente la edición de apariciones en Tiled.
Mantén el ancho de 3200 px por ahora: los proyectiles aún usan el ancho global.
El nivel de prueba anterior conserva su suelo de 128 px y sus plataformas.

Se completó la tercera fila del mapa recibido, se corrigió la referencia
`Desktop/1794978491787.png` y se eliminó un rectángulo de colisión duplicado.
