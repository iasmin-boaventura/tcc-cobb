import numpy as np
import torch

from utils.ImagemUtil import redimensionar_com_padding


def extrair_angulo(modelo, img_crop, device, preprocess_fn, input_size=(64, 64)):
    """
    Extrai o ângulo de uma vértebra usando o modelo CNN.
    img_crop: imagem da vértebra (PIL)
    Retorna: ângulo estimado (float)
    """
    # Garante o tamanho esperado pelo modelo
    img_resized = redimensionar_com_padding(img_crop, input_size)
    tensor = torch.tensor(preprocess_fn(img_resized), dtype=torch.float32).unsqueeze(0).to(device)  # (1, C, H, W)

    with torch.no_grad():
        out = modelo(tensor)

    return out.item() # Retorna escalar

def obter_centros_e_angulos(bboxes, img_norm, modelo_angulo, device, preprocess_fn, input_size=(64,64)):
    """
    Para cada bounding box, retorna:
    - centros: coordenadas do centro da vértebra
    - angulos: ângulo estimado pela CNN
    """
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
    """
    Identifica vértebra superior e inferior para cálculo do ângulo de Cobb.
    Baseia-se em:
    - ângulos máximo e mínimo
    - posição vertical (Y) dos centros
    Retorna: (índice, centro) da vértebra superior, (índice, centro) da inferior
    """
    idx_max = int(np.argmax(angulos))
    idx_min = int(np.argmin(angulos))

    x_max, y_max = centro_bbox(bboxes[idx_max])
    x_min, y_min = centro_bbox(bboxes[idx_min])

    # Decide superior/inferior pela posição Y
    if y_max < y_min:
        return (idx_max, (x_max, y_max)), (idx_min, (x_min, y_min))
    else:
        return (idx_min, (x_min, y_min)), (idx_max, (x_max, y_max))
