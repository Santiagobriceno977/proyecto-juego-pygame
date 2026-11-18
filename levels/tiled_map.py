"""Carga mapas ortogonales finitos CSV y colisiones rectangulares de TSX.

No requiere dependencias adicionales a pygame. Las variantes no soportadas
se rechazan expresamente para evitar mapas con colisiones incorrectas.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import pygame


MAPA_01 = Path(__file__).resolve().parents[1] / "assets" / "maps" / "nivel_01.tmx"


class Colision(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = pygame.Rect(rect)


class MapaTiled:
    def __init__(self, ruta):
        ruta = Path(ruta).resolve()
        raiz = ET.parse(ruta).getroot()
        if raiz.get("orientation") != "orthogonal" or raiz.get("infinite", "0") != "0":
            raise ValueError("Usa un mapa Tiled ortogonal y finito.")
        if any(raiz.find(tag) is not None for tag in ("group", "objectgroup", "imagelayer")):
            raise ValueError("Este cargador admite capas de patrones; aún no capas de objetos o grupos.")
        tw, th = int(raiz.get("tilewidth")), int(raiz.get("tileheight"))
        columnas, filas = int(raiz.get("width")), int(raiz.get("height"))
        self.ancho, self.alto = columnas * tw, filas * th
        self.imagen = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        tiles = {}
        for referencia in raiz.findall("tileset"):
            primero = int(referencia.get("firstgid"))
            fuente = referencia.get("source")
            tsx = (ruta.parent / fuente).resolve() if fuente else ruta
            ts = ET.parse(tsx).getroot() if fuente else referencia
            if (int(ts.get("tilewidth")), int(ts.get("tileheight"))) != (tw, th):
                raise ValueError("Los tiles deben tener el mismo tamaño que las casillas.")
            if ts.find("tileoffset") is not None:
                raise ValueError("No se admiten desplazamientos del tileset.")
            imagen = ts.find("image")
            if imagen is None:
                raise ValueError("Usa un tileset basado en una sola imagen.")
            atlas = pygame.image.load(str(tsx.parent / imagen.get("source"))).convert_alpha()
            cols = int(ts.get("columns"))
            margen, espacio = int(ts.get("margin", 0)), int(ts.get("spacing", 0))
            for indice in range(int(ts.get("tilecount"))):
                recorte = pygame.Rect(margen + (indice % cols) * (tw + espacio),
                                      margen + (indice // cols) * (th + espacio), tw, th)
                dibujo = atlas.subsurface(recorte).copy()
                formas = set()
                tile = ts.find(f"tile[@id='{indice}']")
                if tile is not None:
                    if tile.find("animation") is not None:
                        raise ValueError("Los tiles animados aún no están soportados.")
                    for obj in tile.findall("objectgroup/object"):
                        if any(obj.find(tag) is not None for tag in ("ellipse", "polygon", "polyline", "point")) or float(obj.get("rotation", 0)):
                            raise ValueError("Usa rectángulos de colisión sin rotación.")
                        rect = tuple(round(float(obj.get(k, 0))) for k in ("x", "y", "width", "height"))
                        if rect[2] > 0 and rect[3] > 0:
                            formas.add(rect)
                tiles[primero + indice] = dibujo, formas
        rectangulos = set()
        for capa in raiz.findall("layer"):
            if capa.get("visible", "1") == "0":
                continue
            datos = capa.find("data")
            if datos is None or datos.get("encoding") != "csv" or datos.get("compression"):
                raise ValueError("Guarda las capas con formato CSV en Tiled.")
            ancho, alto = int(capa.get("width")), int(capa.get("height"))
            gids = [int(n) for n in (datos.text or "").split(",") if n.strip()]
            if len(gids) != ancho * alto:
                raise ValueError("La cantidad de casillas no coincide con el tamaño de la capa.")
            ox = round(float(capa.get("offsetx", 0))) + int(capa.get("x", 0)) * tw
            oy = round(float(capa.get("offsety", 0))) + int(capa.get("y", 0)) * th
            superficie = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            for i, gid in enumerate(gids):
                if gid == 0:
                    continue
                if gid & 0xF0000000:
                    raise ValueError("No gires ni voltees los tiles en esta versión del cargador.")
                if gid not in tiles:
                    raise ValueError(f"El tile {gid} no existe en los tilesets.")
                dibujo, formas = tiles[gid]
                x, y = (i % ancho) * tw + ox, (i // ancho) * th + oy
                superficie.blit(dibujo, (x, y))
                for rx, ry, w, h in formas:
                    rectangulos.add((x + rx, y + ry, w, h))
            superficie.set_alpha(round(float(capa.get("opacity", 1)) * 255))
            self.imagen.blit(superficie, (0, 0))
        # Fusiona rectángulos contiguos por fila para evitar juntas y reducir colisiones.
        unidos = []
        for x, y, w, h in sorted(rectangulos, key=lambda r: (r[1], r[3], r[0])):
            if unidos and unidos[-1].y == y and unidos[-1].height == h and unidos[-1].right >= x:
                unidos[-1].width = max(unidos[-1].right, x + w) - unidos[-1].x
            else:
                unidos.append(pygame.Rect(x, y, w, h))
        self.colisiones = pygame.sprite.Group(*(Colision(r) for r in unidos))

    def superficie_en(self, rect):
        """Primera superficie bajo esta franja horizontal, en coordenadas del mapa."""
        superficies = [p.rect.top for p in self.colisiones
                       if p.rect.left < rect.right and rect.left < p.rect.right]
        if not superficies:
            raise ValueError(f"No hay suelo para aparecer en x={rect.x}.")
        return min(superficies)

    def dibujar(self, ventana, camara_x, camara_y):
        ventana.blit(self.imagen, (0, 0),
                     pygame.Rect(camara_x, camara_y, *ventana.get_size()))
