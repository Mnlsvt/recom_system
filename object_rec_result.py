import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from PIL import Image
import numpy as np
import os


# Define the label names
path = os.path.abspath("/home/mnlsvt/Desktop/COCO_Dataset")
labels = ["people","car"]


# Load the pre-trained model
model = load_model(os.path.abspath("/home/mnlsvt/Desktop/ptuxiakh/recom_system/object_detection_model.h5"))

file_path = os.path.join(path, "tzallias.jpg")
# Load the image and resize it
img = Image.open(file_path)
img = img.convert("RGB")
img = img.resize((224, 224))

# Convert the image to a numpy array
#den exoume testarei an h eikona einai sta swsta dimensions

img = np.array(img)
img = np.expand_dims(img, axis=0)

# Make a prediction
prediction = model.predict(img)

# Print the predicted class
print("Predicted class:", labels[np.argmax(prediction)])

