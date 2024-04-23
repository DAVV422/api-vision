import os

from flask import Flask, request, jsonify

import requests
from PIL import Image # pip install Pillow
from io import BytesIO

app = Flask(__name__)

# Variable global para almacenar los ids
credentials = {}
url = "https://us.adfi.karakurai.com/API/ap/api/apidata/"

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Verificar que se ha enviado un archivo
    if 'image' not in request.files:
        return 'No se ha enviado una imagen', 400

    upload_folder = 'uploads'

    # Verificar si la carpeta 'uploads' existe, si no, crearla
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Obtener el archivo de imagen
    image_file = request.files['image']

    image_file.save('./uploads/' + image_file.filename)

    image_path = os.path.join(upload_folder, image_file.filename)

    print(image_path)

    img = Image.open(image_path).convert("RGB")

    # Notice: Please make the image size smaller than 800 pix.
    MAX_SIZE = 800
    height = img.height
    width = img.width
    if img.height > MAX_SIZE:
        height = MAX_SIZE
    if img.width > MAX_SIZE:
        width = MAX_SIZE
    img = img.resize((width, height), Image.ANTIALIAS)
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()
    files = {"image_data": (image_path, img_bytes, "image/png")}
    data = {"apikey": credentials['apikey'], "aimodel_id": credentials['aimodel_id'], "model_type": credentials['model_type']}

    print(data)
    # Send a request.
    response = requests.post(url, files=files, data=data)

    # Retry if the request fails.
    if response.status_code != 200:
        response = requests.post(url, files=files, data=data)

    result_json = response.json()
    result_request = {
        "result": result_json.get("result"),
        "anomaly_score": result_json.get("anomaly_score")
    }
    print(result_json)
    return result_request, 200


@app.route('/store_credentials', methods=['POST'])
def store_ids():
    # Obtener los ids desde el cuerpo de la solicitud
    data = request.json

    # Guardar los ids en la variable global
    credentials['apikey'] = data.get('apikey')
    credentials['aimodel_id'] = data.get('aimodel_id')
    credentials['model_type'] = data.get('model_type')

    return 'Credenciales Actualizadas', 200


@app.route('/get_credentials', methods=['GET'])
def get_ids():
    # Devolver las credenciales almacenadas como un JSON
    return jsonify(credentials)


if __name__ == '__main__':
    app.run(port=5000)