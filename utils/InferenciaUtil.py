import numpy as np
from utils.ImagemUtil import redimensionar_com_padding
import torch

def extrair_angulo(modelo, img_crop, device, preprocess_fn, input_size=(64, 64)):
    # garante o tamanho esperado pelo modelo
    img_resized = redimensionar_com_padding(img_crop, input_size)
    tensor = torch.tensor(preprocess_fn(img_resized), dtype=torch.float32).unsqueeze(0).to(device)  # (1, C, H, W)

    with torch.no_grad():
        out = modelo(tensor)

    # assume que o modelo retorna um escalar por amostra
    return out.item()

def obter_centros_e_angulos(bboxes, img_norm, modelo_angulo, device, preprocess_fn, input_size=(64,64)):
    angulos = []
    centros = []
    for bbox in bboxes:
        x1, y1, x2, y2 = map(int, bbox)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        centros.append((cx, cy))

        crop = img_norm.crop((x1, y1, x2, y2))
        angulo = extrair_angulo(modelo_angulo, crop, device, preprocess_fn, input_size=input_size)
        angulos.append(angulo)

    return angulos, centros

def escolher_extremas(angulos, bboxes, centro_bbox):
    # índices do ângulo máximo e mínimo
    idx_max = int(np.argmax(angulos))
    idx_min = int(np.argmin(angulos))

    # centros correspondentes
    x_max, y_max = centro_bbox(bboxes[idx_max])
    x_min, y_min = centro_bbox(bboxes[idx_min])

    # decide superior/inferior pela posição em Y
    if y_max < y_min:
        return (idx_max, (x_max, y_max)), (idx_min, (x_min, y_min))
    else:
        return (idx_min, (x_min, y_min)), (idx_max, (x_max, y_max))
