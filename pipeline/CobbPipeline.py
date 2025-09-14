import os
import torch
import pandas as pd
from PIL import Image
from modelos.AngleCNN import AngleCNN
from utils.ImagemUtil import salvar_imagem, desenhar_bounding_boxes, desenhar_linha, desenhar_texto
from utils.CalculoUtil import centro_bbox, coordenadas_linha_horizontal, coordenadas_linha_perpendicular, \
    calcular_cobb, perpendiculares_dentro_do_angulo
from utils.InferenciaUtil import obter_centros_e_angulos, escolher_extremas
from utils.ImagemUtil import redimensionar_com_padding, pil_to_tensor

class CobbPipeline:

    def __init__(self, modelo_vertebra, path_angulo_cnn, device='cpu', output_dir='outputs'):
        self.modelo_vertebra = modelo_vertebra
        self.device = device
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.modelo_angulo = AngleCNN().to(device)
        self.modelo_angulo.load_state_dict(torch.load(path_angulo_cnn, map_location=device))
        self.modelo_angulo.eval()

    def process_image(self, img: Image.Image, nome_base="paciente"):
        img_norm = redimensionar_com_padding(img, (640, 640))
        salvar_imagem(img_norm, os.path.join(self.output_dir, f"{nome_base}_redimensionada.png"))

        results = self.modelo_vertebra(img_norm)
        bboxes = results[0].boxes.xyxy.tolist()

        img_vertebras = img_norm.copy()
        desenhar_bounding_boxes(img_vertebras, bboxes, color="blue", width=2)
        salvar_imagem(img_vertebras, os.path.join(self.output_dir, f"{nome_base}_vertebras.png"))

        angulos, centros = obter_centros_e_angulos(
            bboxes, img_norm, self.modelo_angulo, self.device, pil_to_tensor, input_size=(64, 64)
        )

        df_angulos = pd.DataFrame({'vertebra': range(1, len(angulos) + 1), 'angulo': angulos})
        df_angulos.to_csv(os.path.join(self.output_dir, f"{nome_base}_angulos.csv"), index=False)

        cobb_angle = None
        if angulos:
            # depois de calcular ângulos
            angulos, centros = obter_centros_e_angulos(bboxes, img_norm, self.modelo_angulo, self.device, pil_to_tensor)

            (idx_sup, (x_sup, y_sup)), (idx_inf, (x_inf, y_inf)) = escolher_extremas(angulos, bboxes, centro_bbox)

            img_cobb = img_norm.convert("RGB")

            # decide a direção: -1 (esquerda) ou +1 (direita)
            if angulos[idx_sup] == max(angulos):
                direcao = -1  # curvatura ")" → linhas para esquerda
            else:
                direcao = 1  # curvatura "(" → linhas para direita

            # linhas horizontais
            hx_sup = coordenadas_linha_horizontal(x_sup, y_sup, angulos[idx_sup], 200 * direcao)
            hx_inf = coordenadas_linha_horizontal(x_inf, y_inf, angulos[idx_inf], 200 * direcao)

            desenhar_linha(img_cobb, hx_sup, color="blue", width=3)
            desenhar_linha(img_cobb, hx_inf, color="blue", width=3)

            cobb_angle = calcular_cobb(angulos[idx_sup], angulos[idx_inf])

            if cobb_angle >= 5:
                sup_perp, inf_perp = perpendiculares_dentro_do_angulo(hx_sup, hx_inf, angulos, idx_sup, idx_inf)
                desenhar_linha(img_cobb, sup_perp, color="red", width=2)
                desenhar_linha(img_cobb, inf_perp, color="red", width=2)

            df_extremas = pd.DataFrame({'superior': [idx_sup + 1], 'inferior': [idx_inf + 1], 'cobb_angle': [cobb_angle]})
            df_extremas.to_csv(os.path.join(self.output_dir, f"{nome_base}_vertebras_extremas.csv"), index=False)

            desenhar_texto(img_cobb, f"Cobb: {cobb_angle:.1f}°")
            salvar_imagem(img_cobb, os.path.join(self.output_dir, f"{nome_base}_cobb.png"))

        return angulos, cobb_angle, angulos[idx_sup], angulos[idx_inf]
