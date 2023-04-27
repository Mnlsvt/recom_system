import tensorflow as tf
import os
import numpy as np
import json
from PIL import Image

# Set the paths to the COCO dataset
dataDir = '/path/to/COCO_dataset'
dataType = 'train2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
imgDir = '{}/{}'.format(dataDir, dataType)

# Load the annotations
with open(annFile, 'r') as f:
    annotations = json.load(f)

# Load the categories
categories = annotations['categories']
category_dict = {}
for category in categories:
    category_dict[category['id']] = category['name']

# Create the list of images and their corresponding labels
image_paths = []
labels = []
for annotation in annotations['annotations']:
    image_id = annotation['image_id']
    category_id = annotation['category_id']
    image_path = '{}/{}.jpg'.format(imgDir, str(image_id).zfill(12))
    if os.path.exists(image_path):
        image_paths.append(image_path)
        labels.append(category_id)

# Create a TensorFlow dataset from the list of image paths and labels
dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))

# Define the preprocessing function for the images
def preprocess_image(image_path, label):
    # Load the image and resize it to (224, 224)
    img = Image.open(image_path)
    img = img.resize((224, 224))
    # Convert the image to a NumPy array
    img = np.array(img)
    # Normalize the pixel values to be in the range [0, 1]
    img = img / 255.0
    # Convert the label to a one-hot encoded vector
    label = tf.one_hot(label, len(categories))
    return img, label

# Apply the preprocessing function to each image in the dataset
dataset = dataset.map(preprocess_image)

# Shuffle and batch the dataset
batch_size = 32
dataset = dataset.shuffle(buffer_size=len(image_paths))
dataset = dataset.batch(batch_size)

# Define the model architecture
model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(categories), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
epochs = 10
history = model.fit(dataset, epochs=epochs)
