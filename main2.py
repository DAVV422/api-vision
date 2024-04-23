import base64
import cv2 # pip install opencv-python
import json
import numpy as np # pip install numpy
import requests
from PIL import Image # pip install Pillow
from io import BytesIO

# Set your image file path
filename = "your_image_file_path.png"
apikey = "c4f08f5803494e638acd01e14d65a646"
aimodel_id = "4f67ca40-0a78-4571-9228-347cde0f7c85"
model_type = 2
url = "https://us.adfi.karakurai.com/API/ap/api/apidata/"

img = Image.open(filename).convert("RGB")

# Notice: Please make the image size smaller than 800 pix.
MAX_SIZE = 800
height = img.height
width = img.width
if (img.height > MAX_SIZE):
    height = MAX_SIZE
if (img.width > MAX_SIZE):
    width = MAX_SIZE
img = img.resize((width, height), Image.ANTIALIAS)
img_bytes = BytesIO()
img.save(img_bytes, format="PNG")
img_bytes = img_bytes.getvalue()
files = {"image_data": (filename, img_bytes, "image/png")}
data = {"apikey": apikey, "aimodel_id": aimodel_id, "model_type": model_type, "result_image": True}

# Send a request.
response = requests.post(url, files=files, data=data)

# Retry if the request fails.
if(response.status_code != 200):
    response = requests.post(url, files=files, data=data)

result_json = response.json()

# Convert a string to a result image
img_binary = base64.b64decode(result_json["result_image_base64_data"].encode("utf-8"))
img_array = np.frombuffer(img_binary, dtype=np.uint8)
result_image_np = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# Save the result image
cv2.imwrite("result_image.png", result_image_np)

print("result:", result_json["result"])
print("main_prediction_result:", result_json["main_prediction_result"])
print("sub_prediction_result:", result_json["sub_prediction_result"])
print("anomaly_score:", result_json["anomaly_score"])