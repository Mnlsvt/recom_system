import tensorflow as tf
import numpy as np
import os
import cv2
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format

from object_detection.utils import config_util
from object_detection.builders import model_builder
from object_detection.builders import dataset_builder
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.core import losses



# Set up paths and configuration files
#pipeline_config = os.path.abspath("/home/mnlsvt/models/research/object_detection/samples/configs/ssd_mobilenet_v2_coco.config")
# Load the pipeline configuration file
'''
pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
with tf.io.gfile.GFile(os.path.abspath("/home/mnlsvt/models/research/object_detection/samples/configs/ssd_mobilenet_v2_coco.config"), 'r') as f:
    text_format.Merge(f.read(), pipeline_config)
'''

pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()

#with tf.io.gfile.GFile("/home/mnlsvt/models/research/object_detection/samples/configs/ssd_mobilenet_v2_coco.config", mode='rb') as f:
with open(os.path.abspath("/home/mnlsvt/models/research/object_detection/samples/configs/ssd_mobilenet_v2_coco.config"), 'rb') as f:
    text_format.Merge(f.read().decode('utf-8'), pipeline_config)




# model_dir = os.path.abspath("/home/mnlsvt/Desktop/object_model")
model_dir = os.path.abspath("/home/mnlsvt/Desktop/object_model")
num_steps = 100000

# Load the model config
configs = tf.config.list_physical_devices('GPU')
if configs:
  for config in configs:
    tf.config.experimental.set_memory_growth(config, True)

tf.keras.backend.clear_session()
model_config = tf.compat.v1.ConfigProto()
model_config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=model_config)
with tf.io.gfile.GFile(pipeline_config, 'r') as f:
  text_format.Merge(f.read(), pipeline_config)
configs = config_util.get_configs_from_pipeline_file(pipeline_config)
model_config = configs['model']
train_config = configs['train_config']
input_config = configs['train_input_config']

# Build the model
model = model_builder.build(
    model_config=model_config,
    is_training=True,
    add_summaries=True)

# Define the loss function
def detection_loss_evaluator():
  with tf.name_scope('DetectionsLoss'):
    return losses.WeightedSigmoidClassificationLoss(alpha=0.25, gamma=2.0)

# Load the data
dataset = dataset_builder.build_input_pipeline(input_config)

# Set up the training loop
optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=train_config.optimizer.learning_rate)
global_step = tf.Variable(0, trainable=False, name='global_step', dtype=tf.int64)
checkpoint = tf.train.Checkpoint(optimizer=optimizer, model=model, global_step=global_step,)

# Define the training function
@tf.function(experimental_relax_shapes=True)
def train_step_fn(image_tensors, groundtruth_boxes_list, groundtruth_classes_list):
  model.provide_groundtruth(
      groundtruth_boxes_list,
      groundtruth_classes_list)
  with tf.GradientTape() as tape:
    prediction_dict = model.predict(image_tensors)
    losses_dict = model.loss(prediction_dict, true_image_shapes)
    total_loss = tf.add_n([losses_dict[l] for l in losses_dict])
    gradients = tape.gradient(total_loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    global_step.assign_add(1)
    tf.print('Step:', global_step, 'Loss:', total_loss)
    return total_loss

# Train the model
for _ in range(num_steps):
  image_tensors, groundtruth_boxes_list, groundtruth_classes_list = dataset.__iter__().get_next()
  groundtruth_boxes_list = [tf.squeeze(box, axis=0) for box in tf.nest.flatten(groundtruth_boxes_list)]
  groundtruth_classes_list = [tf.squeeze(classes, axis=0) for classes in tf.nest.flatten(groundtruth_classes_list)]
  true_image_shapes = tf.constant([[600, 600, 3]], dtype=tf.int32)
  loss = train_step_fn(image_tensors, groundtruth_boxes_list, groundtruth_classes_list)

  # Save the model every 100
  if int(global_step) % 100 == 0:
        print('Saving checkpoint to:', os.path.join(model_dir, 'ckpt-' + str(int(global_step))))
        checkpoint.write(os.path.join(model_dir, 'ckpt-' + str(int(global_step))))

# Export the model
model.save(os.path.join(model_dir, 'final_model'))

