from PIL import Image, ImageDraw
import numpy as np
import os

def redimensionar_com_padding(img: Image.Image, target_size=(640, 640)):
    # Redimensionar mantendo proporção
    img.thumbnail(target_size, Image.Resampling.LANCZOS)

    # Criar imagem preta
    if img.mode == 'RGB':
        new_img = Image.new("RGB", target_size, (0, 0, 0))
    else:  # 'L' ou outros modos
        new_img = Image.new(img.mode, target_size, 0)

    # Calcular offsets para centralizar a imagem
    left = (target_size[0] - img.width) // 2
    top = (target_size[1] - img.height) // 2
    new_img.paste(img, (left, top))
    return new_img

def pil_to_tensor(img: Image.Image):
    arr = np.array(img, dtype=np.float32) / 255.0
    if len(arr.shape) == 2:  # grayscale
        arr = np.expand_dims(arr, axis=0)
    elif len(arr.shape) == 3:  # RGB
        arr = arr.transpose(2, 0, 1)  # C,H,W
    return arr

def salvar_imagem(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

def desenhar_bounding_boxes(img, bboxes, color="blue", width=2):
    draw = ImageDraw.Draw(img)
    for bbox in bboxes:
        x1, y1, x2, y2 = map(int, bbox)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)

def desenhar_linha(img, coords, color="red", width=2):
    draw = ImageDraw.Draw(img)
    draw.line(coords, fill=color, width=width)

def desenhar_texto(img, texto, pos=(50, 50), color="white"):
    draw = ImageDraw.Draw(img)
    draw.text(pos, texto, fill=color)