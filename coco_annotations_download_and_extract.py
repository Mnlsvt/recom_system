import json
import os
import requests
from pycocotools.coco import COCO

# Define paths
data_dir = os.path.abspath("/home/mnlsvt/Desktop/COCO_Dataset")
annotations_path = os.path.join(data_dir, "annotations")
images_path = os.path.join(data_dir, "images")

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(annotations_path, exist_ok=True)
os.makedirs(images_path, exist_ok=True)

# Download annotations file
annotations_url = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
annotations_file = os.path.join(annotations_path, "annotations_trainval2017.zip")
if not os.path.exists(annotations_file):
    print("Downloading annotations file...")
    response = requests.get(annotations_url)
    with open(annotations_file, "wb") as f:
        f.write(response.content)
else:
    print("Annotations file already exists.")

# Extract annotations file
annotations_zip_path = os.path.join(annotations_path, "annotations_trainval2017")
if not os.path.exists(annotations_zip_path):
    print("Extracting annotations file...")
    import zipfile
    with zipfile.ZipFile(annotations_file, "r") as zip_ref:
        zip_ref.extractall(annotations_path)
else:
    print("Annotations file already extracted.")

# Initialize COCO api for annotations
annotations_file_path = os.path.join(annotations_zip_path, "instances_train2017.json")
coco = COCO(annotations_file_path)

# Get image ids
image_ids = coco.getImgIds()

# Loop over image ids and save images locally
'''
for image_id in image_ids:
    image_info = coco.loadImgs(image_id)[0]
    image_url = image_info["coco_url"]
    image_name = f"{image_id}.jpg"
    image_path = os.path.join(images_path, image_name)
    if not os.path.exists(image_path):
        print(f"Downloading {image_name}...")
        response = requests.get(image_url)
        with open(image_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"{image_name} already exists.")
'''
