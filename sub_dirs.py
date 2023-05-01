'''
import json
import os
from shutil import copyfile
from os import remove

Data = os.path.abspath("/home/mnlsvt/Desktop/COCO_Dataset")
annotations_path = os.path.join(Data, "annotations")
# Load annotations file
with open(os.path.join(annotations_path, 'instances_train2017.json'), 'r') as f:
    annotations = json.load(f)

# Create subdirectories for each category
for category in annotations['categories']:
    os.makedirs(os.path.join('Data', category['name']), exist_ok=True)

# Move each image to its corresponding subdirectory and delete the original image
for image in annotations['images']:
    category = annotations['categories'][image['category_id']-1]['name']
    #src_path = os.path.join('Data', image['file_name'])
    src_path = os.path.join(Data, "images", "train")
    dst_path = os.path.join('Data', category, image['file_name'])
    copyfile(src_path, dst_path)
    remove(src_path)
'''

import json
import os
from shutil import copyfile
from os import remove

Data = os.path.abspath("/home/mnlsvt/Desktop/COCO_Dataset")
annotations_path = os.path.join(Data, "annotations")
# Load annotations file
with open(os.path.join(annotations_path, 'instances_train2017.json'), 'r') as f:
    annotations = json.load(f)

# Create subdirectories for each category
for category in annotations['categories']:
    os.makedirs(os.path.join('Data', category['name']), exist_ok=True)

# Move each image to its corresponding subdirectory and delete the original image
for image in annotations['images']:
    if 'category_id' not in image:
        print(f"Error: 'category_id' not found for image {image}")
        continue
    category = annotations['categories'][image['category_id']-1]['name']
    src_path = os.path.join(Data, "images", "train", image['file_name'])
    dst_path = os.path.join('Data', category, image['file_name'])
    copyfile(src_path, dst_path)
    remove(src_path)
