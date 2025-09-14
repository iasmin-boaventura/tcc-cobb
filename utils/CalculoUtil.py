import math

def centro_bbox(bbox):
    x1, y1, x2, y2 = map(int, bbox)
    return (x1 + x2) // 2, (y1 + y2) // 2

def coordenadas_linha_horizontal(x_center, y_center, angle_deg, length=500):
    x_start = x_center
    x_end = x_center + length
    y_start = y_center
    y_end = y_start - int((x_end - x_start) * math.tan(math.radians(angle_deg)))
    return x_start, y_start, x_end, y_end

def coordenadas_linha_perpendicular(x_fixed, x_start, y_start, x_end, y_end, comprimento, invert=False):
    if x_end != x_start:
        y_fixed = y_start + (y_end - y_start) * (x_fixed - x_start) / (x_end - x_start)
    else:
        y_fixed = y_start

    dx = x_end - x_start
    dy = y_end - y_start
    angle_horizontal = math.atan2(dy, dx)

    angle_perp = angle_horizontal + math.pi / 2
    if invert:
        angle_perp += math.pi

    dx_perp = comprimento * math.cos(angle_perp)
    dy_perp = comprimento * math.sin(angle_perp)

    return int(x_fixed), int(y_fixed), int(x_fixed + dx_perp), int(y_fixed + dy_perp)

def perpendiculares_dentro_do_angulo(hx_sup, hx_inf, angulos, idx_sup, idx_inf, offset=30):
    # define a direção da curvatura
    if angulos[idx_sup] == max(angulos):
        # curva ) → linhas perpendiculares “apontam para dentro do ângulo”
        direcao = -1
        invert_sup = True
        invert_inf = False
    else:
        # curva ( → lógica inversa
        direcao = 1
        invert_sup = False
        invert_inf = True

    # calcula X fixo da perpendicular
    if direcao == 1:
        x_perpendicular = max(hx_sup[0], hx_inf[0]) + offset
    else:
        x_perpendicular = min(hx_sup[0], hx_inf[0]) - offset

    # comprimento vertical aproximado entre horizontais
    comprimento = abs(hx_sup[1] - hx_inf[1])

    sup_perp = coordenadas_linha_perpendicular(x_perpendicular, *hx_sup, comprimento, invert=invert_sup)
    inf_perp = coordenadas_linha_perpendicular(x_perpendicular, *hx_inf, comprimento, invert=invert_inf)

    return sup_perp, inf_perp


def calcular_cobb(angulo_sup, angulo_inf):
    return abs(angulo_sup - angulo_inf)