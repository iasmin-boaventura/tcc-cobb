import torch
from PIL import Image

from modelos.AngleCNN import AngleCNN
from utils.CalculoUtil import centro_bbox, coordenadas_linha_horizontal, calcular_cobb, perpendiculares_dentro_do_angulo
from utils.ImagemUtil import desenhar_linha, desenhar_texto
from utils.ImagemUtil import redimensionar_com_padding, pil_to_tensor
from utils.InferenciaUtil import obter_centros_e_angulos, escolher_extremas


class CobbPipeline:
    """
    Pipeline para processar imagens de raio-X, detectar vértebras,
    calcular o ângulo de cada vértebra e retornar a imagem com o
    ângulo de Cobb desenhado.
    """

    def __init__(self, modelo_vertebra, path_angulo_cnn, device):
        self.modelo_vertebra = modelo_vertebra
        self.device = device

        self.modelo_angulo = AngleCNN().to(device)
        self.modelo_angulo.load_state_dict(torch.load(path_angulo_cnn, map_location=device))
        self.modelo_angulo.eval()

    def process_image(self, img: Image.Image):
        """
        Processa a imagem:
        - Redimensiona com padding
        - Detecta vértebras com YOLO
        - Calcula ângulos das vértebras
        - Identifica vértebra superior e inferior para o ângulo de Cobb
        - Desenha linhas e texto na imagem

        Retorna:
            - cobb_angle: valor do ângulo de Cobb (float)
            - img_cobb: imagem PIL com linhas e ângulo desenhados
        """
        img_norm = redimensionar_com_padding(img, (640, 640))

        # Detectar vértebras
        results = self.modelo_vertebra(img_norm)
        bboxes = results[0].boxes.xyxy.tolist()

        # Calcular ângulos das vértebras
        angulos, centros = obter_centros_e_angulos(
            bboxes, img_norm, self.modelo_angulo, self.device, pil_to_tensor, input_size=(64, 64)
        )

        cobb_angle = None
        img_cobb = img_norm.convert("RGB")

        if angulos:
            # Identificar vértebras extremas para o cálculo do Cobb
            (idx_sup, (x_sup, y_sup)), (idx_inf, (x_inf, y_inf)) = escolher_extremas(angulos, bboxes, centro_bbox)

            # Identificar vértebras extremas para o cálculo do Cobb
            direcao = -1 if angulos[idx_sup] == max(angulos) else 1

            # Desenhar linhas horizontais
            hx_sup = coordenadas_linha_horizontal(x_sup, y_sup, angulos[idx_sup], 200 * direcao)
            hx_inf = coordenadas_linha_horizontal(x_inf, y_inf, angulos[idx_inf], 200 * direcao)
            desenhar_linha(img_cobb, hx_sup, color="blue", width=3)
            desenhar_linha(img_cobb, hx_inf, color="blue", width=3)

            # Desenhar linhas perpendiculares dentro do ângulo
            sup_perp, inf_perp = perpendiculares_dentro_do_angulo(hx_sup, hx_inf, angulos, idx_sup, idx_inf)
            desenhar_linha(img_cobb, sup_perp, color="red", width=1)
            desenhar_linha(img_cobb, inf_perp, color="red", width=1)

            # Calcular ângulo de Cobb
            cobb_angle = calcular_cobb(angulos[idx_sup], angulos[idx_inf])

            # Adicionar texto com valor do ângulo
            desenhar_texto(img_cobb, f"Cobb: {cobb_angle:.1f}°")

        return cobb_angle, img_cobb
