import numpy as np
from PIL import Image, ImageDraw


def redimensionar_com_padding(img: Image.Image, target_size=(640, 640)):
    """
    Redimensiona a imagem mantendo proporção e adiciona padding
    para preencher o tamanho alvo.
    """
    img.thumbnail(target_size, Image.Resampling.LANCZOS)

    # Cria imagem de fundo (preta)
    if img.mode == 'RGB':
        new_img = Image.new("RGB", target_size, (0, 0, 0))
    else:  # 'L' ou outros modos
        new_img = Image.new(img.mode, target_size, 0)

    # Centraliza a imagem
    left = (target_size[0] - img.width) // 2
    top = (target_size[1] - img.height) // 2
    new_img.paste(img, (left, top))
    return new_img

def pil_to_tensor(img: Image.Image):
    """
    Converte imagem PIL para tensor numpy (C,H,W) normalizado [0,1].
    """
    arr = np.array(img, dtype=np.float32) / 255.0
    if len(arr.shape) == 2:  # grayscale
        arr = np.expand_dims(arr, axis=0)
    elif len(arr.shape) == 3:  # RGB
        arr = arr.transpose(2, 0, 1)  # C,H,W
    return arr

def desenhar_linha(img, coords, color="red", width=2):
    """
    Desenha uma linha na imagem PIL.
    coords: lista de tuplas [(x1,y1),(x2,y2)]
    """
    draw = ImageDraw.Draw(img)
    draw.line(coords, fill=color, width=width)

def desenhar_texto(img, texto, pos=(50, 50), color="white"):
    """
    Desenha texto na imagem PIL.
    pos: posição (x, y) do texto
    """
    draw = ImageDraw.Draw(img)
    draw.text(pos, texto, fill=color)