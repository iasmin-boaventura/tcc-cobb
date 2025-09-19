import base64, json

with open("resultadocobb3.json", "r") as f:
    data = json.load(f)

img_bytes = base64.b64decode(data["image_base64"])
with open("resultado.png", "wb") as f:
    f.write(img_bytes)