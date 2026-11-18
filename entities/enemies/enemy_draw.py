"""Cría provisional dibujada con pygame.draw, sin archivos de imagen."""
import math
import pygame

TAMANO = (80, 64)
BORDE = (28, 22, 33)
PIEL = (147, 146, 132)
LUZ = (198, 189, 163)
SOMBRA = (83, 77, 87)
HERIDA = (112, 45, 56)


def dibujar_cria(imagen, accion, fase, progreso, derecha):
    imagen.fill((0, 0, 0, 0))
    paso = math.sin(fase)
    carrera = accion == "CORRER"
    moviendo = accion in ("CAMINAR", "CORRER")
    amplitud = (9 if carrera else 5) if moviendo else 0
    balanceo = round(abs(paso) * (2 if carrera else 1)) if moviendo else 0
    sacudida = round(math.sin(progreso * math.pi * 5) * 3) if accion == "HERIDO" else 0
    inclinar = 3 if carrera else 0
    cadera = (38 + sacudida, 43 + balanceo)
    hombro = (43 + inclinar + sacudida, 29 + balanceo)
    cabeza = (48 + inclinar + sacudida, 22 + balanceo)
    pie_a = (34 + round(paso * amplitud), 62)
    pie_b = (44 - round(paso * amplitud), 62)
    if moviendo:
        pie_a = (pie_a[0], 62 - round(max(0, paso) * 5))
        pie_b = (pie_b[0], 62 - round(max(0, -paso) * 5))
    if accion == "SALTAR":
        pie_a, pie_b = (27, 53), (49, 54)
    mano = (53 + round(paso * 3 if moviendo else 0), 49 + balanceo)
    codo = (49, 39 + balanceo)
    if accion == "PREPARAR":
        codo, mano = (32, 26), (34, 14)
    elif accion == "GOLPEAR":
        codo, mano = (60, 33), (72, 38)
    elif accion == "RECUPERAR":
        codo, mano = (55, 38), (60, 48)
    elif accion == "HERIDO":
        cabeza = (cabeza[0] - 5, cabeza[1] - 2)
        codo, mano = (30, 35), (23, 42)

    def miembro(puntos, color, grosor=4):
        pygame.draw.lines(imagen, BORDE, False, puntos, grosor + 2)
        pygame.draw.lines(imagen, color, False, puntos, grosor)
        for punto in puntos[1:-1]:
            pygame.draw.circle(imagen, color, punto, grosor // 2)

    # Pierna y brazo posteriores, largos y delgados.
    miembro([cadera, (pie_b[0] + 2, 52), pie_b], SOMBRA)
    miembro([(hombro[0] - 5, hombro[1] + 2), (29, 39 + balanceo), (27, 52)], SOMBRA, 3)
    miembro([cadera, (pie_a[0] - 3, 53), pie_a], PIEL)
    for pie in (pie_a, pie_b):
        pygame.draw.line(imagen, BORDE, (pie[0] - 2, pie[1]), (pie[0] + 5, pie[1]), 3)
        pygame.draw.line(imagen, LUZ, pie, (pie[0] + 4, pie[1]), 1)
    # Columna curvada, caja torácica estrecha y costillas expuestas.
    torso = [(hombro[0] - 7, hombro[1] - 2), (hombro[0] + 4, hombro[1]),
             (cadera[0] + 3, cadera[1]), (cadera[0] - 5, cadera[1] + 1),
             (hombro[0] - 10, hombro[1] + 7)]
    pygame.draw.polygon(imagen, BORDE, torso)
    pygame.draw.lines(imagen, PIEL, False, [cadera, (hombro[0] - 6, hombro[1] + 8), hombro], 7)
    pygame.draw.line(imagen, LUZ, (hombro[0] - 7, hombro[1] + 2), (cadera[0] - 2, cadera[1] - 2), 2)
    for i in range(3):
        y = hombro[1] + 4 + i * 3
        pygame.draw.line(imagen, SOMBRA, (hombro[0] - 3, y), (hombro[0] + 2 - i, y + 1), 1)
    pygame.draw.line(imagen, HERIDA, (cadera[0], cadera[1] - 4), (cadera[0] + 2, cadera[1]), 2)
    miembro([hombro, codo, mano], PIEL, 3)
    for i in range(3):
        fin = (mano[0] + (5 if accion == "GOLPEAR" else 2), mano[1] + i * 2 + 2)
        pygame.draw.line(imagen, LUZ, (mano[0], mano[1] + i), fin, 1)
    miembro([hombro, (cabeza[0] - 2, cabeza[1] + 5)], SOMBRA, 4)
    pygame.draw.ellipse(imagen, BORDE, (cabeza[0] - 7, cabeza[1] - 8, 14, 17))
    pygame.draw.ellipse(imagen, PIEL, (cabeza[0] - 5, cabeza[1] - 6, 11, 14))
    pygame.draw.line(imagen, LUZ, (cabeza[0] - 3, cabeza[1] - 5), (cabeza[0] + 2, cabeza[1] - 5), 2)
    pygame.draw.line(imagen, BORDE, (cabeza[0], cabeza[1]), (cabeza[0] + 5, cabeza[1] + 1), 2)
    ojo = (255, 182, 77) if accion == "PREPARAR" else (208, 78, 66)
    pygame.draw.rect(imagen, ojo, (cabeza[0] + 3, cabeza[1], 2, 2))
    pygame.draw.lines(imagen, SOMBRA, False, [(cabeza[0], cabeza[1] + 6),
                      (cabeza[0] + 2, cabeza[1] + 4), (cabeza[0] + 4, cabeza[1] + 6)], 1)
    if accion == "PREPARAR":
        # Aviso visible incluso con varios enemigos juntos.
        pygame.draw.line(imagen, (255, 188, 82), (48, 2), (48, 7), 2)
        pygame.draw.rect(imagen, (255, 188, 82), (47, 10, 2, 2))
    elif accion == "GOLPEAR":
        for i in range(3):
            pygame.draw.line(imagen, (223, 172, 144), (65, 30 + i * 4), (77, 38 + i * 3), 1)
    if not derecha:
        espejo = pygame.transform.flip(imagen, True, False)
        imagen.fill((0, 0, 0, 0))
        imagen.blit(espejo, (0, 0))
