import base64
import io

import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO

from pipeline.CobbPipeline import CobbPipeline

# Dispositivo de processamento (GPU se disponível, senão CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

path_modelo_vertebra = "modelos/vertebra.pt"
path_modelo_angulo_cnn = "modelos/angulo.pt"
modelo_vertebra = YOLO(path_modelo_vertebra)

# Carregar modelos
pipeline = CobbPipeline(
    modelo_vertebra=modelo_vertebra,
    path_angulo_cnn=path_modelo_angulo_cnn,
    device=device
)

app = FastAPI(title="API OrthoAI")

@app.post("/process_image/")
async def process_image(file: UploadFile = File(...)):
    """
    Recebe uma imagem de raio-X, processa na pipeline Cobb,
    e retorna:
        - cobb_angle: valor do ângulo de Cobb
        - image_base64: imagem processada em Base64
    """
    try:
        img = Image.open(file.file).convert("L")  # grayscale

        cobb_angle, img_cobb = pipeline.process_image(img)

        # Converte imagem processada em base64
        buffer = io.BytesIO()
        img_cobb.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        return JSONResponse(content={
            "cobb_angle": cobb_angle,
            "image_base64": img_base64
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)