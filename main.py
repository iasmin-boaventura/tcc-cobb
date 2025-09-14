import os
from PIL import Image
import torch
from pipeline.CobbPipeline import CobbPipeline
from ultralytics import YOLO

# ----------------- CONFIGURAÇÃO -----------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Caminhos para os modelos
path_modelo_vertebra = "modelos/vertebra.pt"   # YOLOv8 para detectar vértebras
path_modelo_angulo_cnn = "modelos/angulo.pt"   # CNN para calcular ângulo

# Carregar modelo de vértebras (YOLOv8)
modelo_vertebra = YOLO(path_modelo_vertebra)

# ----------------- INICIALIZAR PIPELINE -----------------
pipeline = CobbPipeline(
    modelo_vertebra=modelo_vertebra,
    path_angulo_cnn=path_modelo_angulo_cnn,
    device=device,
    output_dir="outputs"
)

# ----------------- PROCESSAR IMAGEM -----------------
img_path = "teste2.jpg"
img = Image.open(img_path).convert("L")  # manter grayscale

# Executar pipeline
angulos, cobb_angle, v_sup_angle, v_inf_angle = pipeline.process_image(img, nome_base="paciente2")

# ----------------- RESULTADOS -----------------
print("Ângulos das vértebras:", angulos)
print("Ângulo de Cobb:", cobb_angle)
print("Ângulos Superior: " + str(v_sup_angle))
print("Ângulos Inferior: " + str(v_inf_angle))
print("Arquivos salvos em:", os.path.abspath("outputs"))
