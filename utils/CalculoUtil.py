import math

def centro_bbox(bbox):
    """
    Retorna o centro de uma bounding box.
    bbox: (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = map(int, bbox)
    return (x1 + x2) // 2, (y1 + y2) // 2

def coordenadas_linha_horizontal(x_center, y_center, angle_deg, length=500):
    """
    Calcula coordenadas de uma linha horizontal inclinada a partir do centro.
    Retorna: x_start, y_start, x_end, y_end
    """
    x_start = x_center
    x_end = x_center + length
    y_start = y_center
    y_end = y_start - int((x_end - x_start) * math.tan(math.radians(angle_deg)))
    return x_start, y_start, x_end, y_end

def coordenadas_linha_perpendicular(x_fixed, x_start, y_start, x_end, y_end, comprimento, invert=False):
    """
    Calcula coordenadas de uma linha perpendicular a uma linha existente.
    invert=True para inverter direção.
    """
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
    """
    Calcula as linhas perpendiculares dentro do ângulo de Cobb,
    ajustando direção e posição de acordo com a curvatura.
    """
    # Define a direção da curvatura
    if angulos[idx_sup] == max(angulos):
        # Curva ) → linhas apontam para dentro
        direcao = -1
        invert_sup = True
        invert_inf = False
    else:
        # Curva ( → lógica inversa
        direcao = 1
        invert_sup = False
        invert_inf = True

    # Posição X da perpendicular com offset
    if direcao == 1:
        x_perpendicular = max(hx_sup[0], hx_inf[0]) + offset
    else:
        x_perpendicular = min(hx_sup[0], hx_inf[0]) - offset

    # Comprimento aproximado vertical entre horizontais
    comprimento = abs(hx_sup[1] - hx_inf[1])

    sup_perp = coordenadas_linha_perpendicular(x_perpendicular, *hx_sup, comprimento, invert=invert_sup)
    inf_perp = coordenadas_linha_perpendicular(x_perpendicular, *hx_inf, comprimento, invert=invert_inf)

    return sup_perp, inf_perp


def calcular_cobb(angulo_sup, angulo_inf):
    """
    Calcula o ângulo de Cobb como diferença absoluta entre ângulos superior e inferior.
    """
    return abs(angulo_sup - angulo_inf)