import tensorflow as tf
from keras import layers
from keras.preprocessing.image import ImageDataGenerator
import os


data_dir = os.path.abspath("/home/mnlsvt/Desktop/COCO_Dataset")
annotations_file_path = os.path.join(data_dir, "annotations", "instances_train2017.json")
#coco = COCO(annotations_file_path)


# Define hyperparameters
batch_size = 2 # was 32
epochs = 10
num_classes = 2 # was 80
input_shape = (224, 224, 3)

# Define data directories
train_dir = os.path.join(data_dir, 'images/train')
val_dir = os.path.join(data_dir, 'images/val')

# Define data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(
    rescale=1./255
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    class_mode="categorical"
)

val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    class_mode="categorical"
)

# Define model
model = tf.keras.Sequential([
    layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dense(num_classes, activation="softmax")
])

# Compile model
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Train model
model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator
)

# Save model
model.save("object_detection_model.h5")
