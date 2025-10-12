# Cobb API 🩻

API para processar imagens de raio-X e calcular o ângulo de Cobb.  
Retorna o valor do ângulo e a imagem processada em Base64.

## Diagrama de Classes

```mermaid
---
config:
  layout: elk
  theme: redux
---
%%{init: {"themeVariables": { "fontSize": "15px", "classTextSize": "20px" }}}%%

classDiagram
    direction LR

    class CobbPipeline {
        - modelo_vertebra: YOLO //Ultralytics
        - modelo_angulo: AngleCNN
        - dispositivo: Device
        + processar_imagem(img): (float, Image)
    }

    class AngleCNN {
        // herda nn.Module [PyTorch]
        - camadas_conv: nn.Sequential
        - camadas_fc: nn.Sequential
        + forward(x)
    }

       class CalculoUtil {
        + centro_bbox(bbox)
        + coordenadas_linha_horizontal(x_center, y_center, angle_deg, length)
        + coordenadas_linha_perpendicular(x_fixed, x_start, y_start, x_end, y_end, comprimento, invert)
        + perpendiculares_dentro_do_angulo(hx_sup, hx_inf, angulos, idx_sup, idx_inf, offset)
        + calcular_cobb(angulo_sup, angulo_inf)
    }

    class ImagemUtil {
        + redimensionar_com_padding(img, target_size)
        + pil_to_tensor(img)
        + desenhar_linha(img, coords, color, width)
        + desenhar_texto(img, texto, pos, color)
    }

    class InferenciaUtil {
        + extrair_angulo(modelo, img_crop, device, preprocess_fn, input_size)
        + obter_centros_e_angulos(bboxes, img_norm, modelo_angulo, device, preprocess_fn, input_size)
        + escolher_extremas(angulos, bboxes, centro_bbox)
    }

    CobbPipeline --> AngleCNN
    CobbPipeline ..> CalculoUtil
    CobbPipeline ..> ImagemUtil
    CobbPipeline ..> InferenciaUtil
```

---

## Diagrama de Sequência

```mermaid
---
config:
  theme: redux
  look: handDrawn
---
sequenceDiagram
  participant Main as main.py <<script>>
  participant Pipeline as CobbPipeline <<core>>
  participant YOLO as YOLO <<external>>
  participant AngleCNN as AngleCNN <<core>>
  participant Calculo as CalculoUtil <<utility>>
  participant Imagem as ImagemUtil <<utility>>
  participant Inferencia as InferenciaUtil <<utility>>
  autonumber
  Main ->> Pipeline: instancia CobbPipeline(modelo_vertebra, path_angulo_cnn, device)
  Main ->> Pipeline: process_image(img)
  Pipeline ->> Imagem: redimensionar_com_padding(img)
  Pipeline ->> YOLO: detectar vértebras
  Pipeline ->> AngleCNN: inferir ângulo de cada vértebra
  Pipeline ->> Inferencia: obter_centros_e_angulos(bboxes, img_norm, modelo_angulo)
  Pipeline ->> Inferencia: escolher_extremas(angulos, bboxes, centro_bbox)
  Pipeline ->> Calculo: coordenadas_linha_horizontal(x_center, y_center, angle_deg)
  Pipeline ->> Imagem: desenhar_linha(img, coords, color, width)
  Pipeline ->> Calculo: calcular_cobb(angulo_sup, angulo_inf)
  Pipeline ->> Imagem: desenhar_texto(img, texto, pos, color)
  Pipeline -->> Main: retorna (cobb_angle, img_cobb)
```

---

## 🚀 Requisitos

- Python 3.10+
- pip

---

## ⚙️ Configuração do ambiente

1. **Clonar o repositório**

```bash
git clone https://github.com/iasmin-boaventura/tcc-cobb/
cd cobb
````

2. **Criar e ativar o virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Instalar as dependências**

```powershell
pip install -r requirements.txt
```

---

## 🏃 Rodando o servidor FastAPI

```powershell
uvicorn main:app --reload
```

* O servidor estará disponível em: `http://127.0.0.1:8000`
* Documentação interativa: `http://127.0.0.1:8000/docs`

---

## 📤 Testando a API com `curl`

Supondo que você tenha uma imagem `teste9.jpg` na pasta do projeto:

```powershell
curl -X POST "http://127.0.0.1:8000/process_image/" `
  -F "file=@teste9.jpg" `
  --output resposta.json
```

* O comando envia a imagem para a API e salva a resposta em `resposta.json`.
* Estrutura do JSON retornado:

```json
{
  "cobb_angle": 32.5,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

## ⚡ Usando no React

Exemplo simples de upload de imagem e exibição do resultado:

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("http://127.0.0.1:8000/process_image/", {
  method: "POST",
  body: formData
});

const data = await response.json();

console.log("Cobb Angle:", data.cobb_angle);
document.getElementById("imagem").src = `data:image/png;base64,${data.image_base64}`;
```

```html
<img id="imagem" alt="Raio-X Processado" />
```

---

## ⚠️ Observações

* A API processa imagens em **grayscale** (tons de cinza).
* Certifique-se de enviar arquivos `.jpg` ou `.png`.
* Ideal para uso local ou integração com frontend React/JS.
