# Start with:
# celery -A flask_local_with_class.celery worker --pool=threads --loglevel=info --concurrency=1 & python flask_local_with_class.py

# Import statements
import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
from PIL import Image
import os
import requests
import ast
import numpy as np
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import tensorflow as tf
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from celery import Celery
from firebase_admin import storage, firestore, credentials
import firebase_admin
import subprocess
from sklearn.preprocessing import OneHotEncoder
from functions.unified_code_funcs import recursion_change_bn, load_labels, hook_feature, returnCAM, returnTF, load_model, features_blobs
from functions.object_detection_funcs import perform_object_recognition
import torchvision
from PIL import Image
import torchvision.transforms as T
from collections import defaultdict
import time

# Flask and Celery configuration
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'  # RabbitMQ
app.config['result_backend'] = 'rpc://'

current_dir = os.path.dirname(os.path.abspath(__file__))

def make_celery(app):
    celery = Celery(app.import_name, backend='redis://localhost', broker='pyamqp://')
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Firebase and model initialization
script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, "../../ptuxiakhmanwlhs-firebase-adminsdk.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {'storageBucket': 'ptuxiakhmanwlhs.appspot.com'})
db = firestore.client()

# Initialize the model and utilities at the start of the script or within a function
def initialize_model():
    global model, vectorizer, encoder, label_encoder
    model = tf.keras.models.load_model('classModel.keras')
    vectorizer = joblib.load('vectorizer.pkl')
    encoder = joblib.load('encoder.pkl')
    label_encoder = joblib.load('label_encoder.pkl')

initialize_model()


def configure_gpu():
    # List and set up TensorFlow to use available GPUs
    gpus = tf.config.list_physical_devices('GPU')

    if gpus:
        try:
            # Loop through GPUs and configure each one
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                print(f"Configuring GPU: {gpu}")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(f"Failed to configure GPU: {e}")
    else:
        print("No GPU found. Using CPU.")

def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print("Download complete!")
    else:
        print("Failed to download the file.")

def preprocess_input(input_data, vectorizer, encoder):
    df = pd.DataFrame([input_data])
    df['attribute_predictions_str'] = df['attribute_predictions'].apply(lambda x: ' '.join(x))
    df['objectsFound_str'] = df['objectsFound'].apply(lambda x: ' '.join([' '.join(pair) for pair in x]))
    df['backgroundSpace_str'] = df['backgroundSpace'].apply(lambda x: ' '.join(x) if x else 'None')
    attributes_vec = vectorizer.transform(df['attribute_predictions_str']).toarray()
    objects_vec = vectorizer.transform(df['objectsFound_str']).toarray()
    background_vec = encoder.transform(df[['backgroundSpace_str']]).toarray()
    return np.hstack((attributes_vec, objects_vec, background_vec))

def make_prediction(input_features):
    input_features = preprocess_input(input_features, vectorizer, encoder)
    prediction = model.predict(input_features)
    predicted_class = np.argmax(prediction, axis=1)
    return predicted_class

def process_unified_code(image_path, arch):
        # Load labels, model, transformer, etc. (your subprocess code)
        classes, labels_IO, labels_attribute, W_attribute = load_labels()
        global features_blobs
        model = load_model(arch, current_dir)
        tf = returnTF()
        params = list(model.parameters())
        weight_softmax = np.array(params[-2].data)
        weight_softmax[weight_softmax < 0] = 0

        # Load and process the image
        img = Image.open(image_path)
        input_img = V(tf(img).unsqueeze(0))

        # Forward pass
        logit = model.forward(input_img)
        h_x = F.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)
        probs = probs.numpy()
        idx = idx.numpy()

        # Process and return results
        io_image = np.mean(labels_IO[idx[:10]])
        scene_categories = [(probs[i], classes[idx[i]]) for i in range(5)]
        responses_attribute = W_attribute.dot(features_blobs[1])
        idx_a = np.argsort(responses_attribute)
        scene_attributes = [labels_attribute[idx_a[i]] for i in range(-1, -10, -1)]

        # Here you can format the output as needed
        return {
            "io_image": io_image,
            "scene_categories": scene_categories,
            "scene_attributes": scene_attributes
        }

def process_basic_code(arch, images):
    # Get the current directory
    
    # Load the pre-trained weights
    model_file = os.path.join(current_dir, '..', '..', 'models', '%s_places365.pth.tar' % arch)
    model = models.__dict__[arch](num_classes=365)
    checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()

    # Load the image transformer
    centre_crop = trn.Compose([
        trn.Resize((256, 256)),
        trn.CenterCrop(224),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load the class label
    file_name = 'categories_places365.txt'
    if not os.access(file_name, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
        os.system('wget ' + synset_url)
    classes = list()
    with open(file_name) as class_file:
        for line in class_file:
            classes.append(line.strip().split(' ')[0][3:])
    classes = tuple(classes)

    # Load the test image
    img_name = os.path.join(current_dir, images)

    img = Image.open(img_name)
    input_img = V(centre_crop(img).unsqueeze(0))

    # Forward pass
    logit = model.forward(input_img)
    h_x = F.softmax(logit, 1).data.squeeze()
    probs, idx = h_x.sort(0, True)

    output_predictions = []
    # Output the prediction
    for i in range(0, 3):
        output_predictions.append(('{:.3f} -> {}'.format(probs[i], classes[idx[i]])))
    return output_predictions

def classification_process(test_input):
    predicted_class = make_prediction(test_input)
    predicted_class_name = label_encoder.inverse_transform(predicted_class)[0]
    print("Predicted Class:", predicted_class_name)
    return predicted_class_name


@celery.task(name='flask_local_with_class.process_image_task', ignore_result=False, soft_time_limit=30, time_limit=60, rate_limit='3/m')
def process_image_task(image_id):
    # Configure GPU to use memory growth
    configure_gpu()

    doc = db.collection(u'images').document(image_id).get()
    
    doc_ref = db.collection(u'images').document(image_id)

    # Retrieve the file extension from the document
    extension = doc.to_dict()['extension']
    
    url = doc.to_dict()['url']
    
    destination = "../../temp_img/"
    destination += image_id
    destination += "."
    destination += extension
    download_file(url, destination)

    
    # Download the image file from Firebase
    bucket = storage.bucket()
    blob = bucket.blob(image_id)
    print(blob.name)
    filename = os.path.join("../../temp_img", blob.name)
    filename2 = filename
    filename2 += "."
    filename2 += extension

    predictions = [[['' for k in range(3)] for j in range(3)] for i in range(4)]

    images = filename2

 
    # predictions = []
    attribute_predictions = []

    for k in range(3):
        if k == 0:
            arch = "resnet18"
        elif k == 1:
            arch = "resnet50"
        else:
            arch = "alexnet"

        result = process_basic_code(arch, images)
        predictions.append(result)
        print(result)

    # Iterate over each set of predictions
    for i, result in enumerate(predictions):
        if i == 0:
            arch = "resnet18"
        elif i == 1:
            arch = "resnet50"
        else:
            arch = "alexnet"

        for j, pred in enumerate(result):
            # Check if 'pred' is a string and contains the '->' pattern
            if isinstance(pred, str) and '->' in pred:
                pred_acc = float(pred.split(' -> ')[0])  # Extract accuracy from prediction
                pred_label = pred.split(' -> ')[1]  # Extract predicted label from prediction

                # Check if accuracy is greater than or equal to 0.2
                if pred_acc >= 0.2:
                    predictions[i][j] = [arch, pred_acc, pred_label]  # Replace prediction with [arch, accuracy, label]
                else:
                    predictions[i][j] = ["none", "none", "none"]  # Replace prediction with "none"
            else:
                # Handle non-standard 'pred' values (e.g., empty strings or lists)
                predictions[i][j] = ["none", "none", "none"]  # Replace with "none"

    
    result = process_unified_code(images, arch)

    # get the output of script1.py as input
    #input_data = result.stdout.decode('utf-8').strip()
    arch = "widerestnet"

    # do something with the input data

    scene_categories = result['scene_categories']  # Assuming this key exists in the dictionary

    for i, category in enumerate(scene_categories[:3]):  # Limit to first 3 categories
        pred_acc = category[0]  # Confidence or accuracy
        pred_name = category[1]  # Category name

        if pred_acc >= 0.2:  # Adjust this threshold as per your accuracy scale
            predictions[3][i][0] = arch
            predictions[3][i][1] = str(pred_acc)
            predictions[3][i][2] = pred_name
        else:
            predictions[3][i][0] = "none"
            predictions[3][i][1] = "none"
            predictions[3][i][2] = "none"
        #print(pred_acc, pred1)
    
    
    scene_attributes = result['scene_attributes']

    # No need for splitting and parsing as in the original code
    # Directly use the list of attributes
    attribute_predictions = scene_attributes

    # If you need to process the attributes further, you can iterate over 'attribute_predictions'
    # For example, to trim spaces or perform other operations
    processed_attributes = []
    for attr in attribute_predictions:
        # Example processing, like trimming leading/trailing spaces
        processed_attr = attr.strip()
        processed_attributes.append(processed_attr)

    predictions = [[cell for cell in row if 'none' not in cell] for row in predictions if any('none' not in cell for cell in row)]
    predictions = [[cell for cell in row if '' not in cell] for row in predictions if any('' not in cell for cell in row)]

    print(processed_attributes)

    # combined_predictions is an array of the common predictions that the models had
    combined_predictions = []

    # We count how many times each prediction appear
    word_count = {}

    for sublist in predictions:
        for item in sublist:
            word = item[2]
            if word not in word_count:
                word_count[word] = 1
            else:
                word_count[word] += 1

    # If not enough models voted on the same predictions, we remove them
    for word_temp, value in list(word_count.items()):
        if (value < 2):
            word_count.pop(word_temp)

    background_space = list(word_count.keys())
    print(background_space)


    # object recognition

 
    #result = subprocess.run(['python3', 'object_recognition.py'], stdout=subprocess.PIPE)
    object_rec_data = perform_object_recognition(images)
    print(object_rec_data)
    #object_rec_data = object_rec_data.split('\n')
    #print(object_rec_data[8])
    #result_objects = object_rec_data[8]

    # Function to convert string representations to lists
    def convert_to_list(str_representation):
        return ast.literal_eval(str_representation)

    # Function to extract object names
    def extract_object_names(data):
        object_names = set()
        for item in data:
            # Directly use the item if it's already a list (or other iterable)
            for obj in item:
                object_names.add(obj)  # Assuming each item is a list with object names
        return object_names
    
    # Extract object names
    extracted_objects = extract_object_names(object_rec_data)

    #result_objectsList = ast.literal_eval(result_objects)
    final_objectsList = list(extracted_objects)

    #final_objectsList = []
    #final_objectsScore = []

    # For the objects:
    #for item in result_objectsList:
    #    final_objectsList.append(item[0])

    print(final_objectsList)

    os.remove(filename2)
    
    # Get the document reference

    # Prepare input data for TensorFlow model
    input_data_for_tf_model = {
        'attribute_predictions': attribute_predictions,
        'backgroundSpace': background_space,
        'objectsFound': list(final_objectsList)
    }
    
    print(input_data_for_tf_model)

    print("Classification process starting...")
    # Process input and make prediction
    try:
        class_result = classification_process(input_data_for_tf_model)
        response_data = {
            'image_id': image_id,
            'attribute_predictions': attribute_predictions,
            'backgroundSpace': background_space,
            'objectsFound': list(final_objectsList),
            'predicted_class': class_result,  # Include the predicted class,
            'gpt': 'no'
        }

    except ValueError as e:
        if 'Found unknown categories' in str(e):
            response_data = {
                'image_id': image_id,
                'attribute_predictions': attribute_predictions,
                'backgroundSpace': processed_attributes,
                'objectsFound': list(final_objectsList),
                'predicted_class': 'unknown',  # Default class in case of error
                'gpt': 'no'
            }

    print("responsedata", response_data)
    # Return the response data so that it can be accessed when the task is complete
    #return response_data

    proxy_url = "https://MnLsVt.pythonanywhere.com/update_data"  # Replace with your proxy URL


    # Send the data to the proxy
    try:
        requests.post(proxy_url, json=response_data)
        print("metadata sent")
    except Exception as e:
        print("error sending the metadata")

@app.route('/predict', methods=['POST'])
def predict():
    if 'image_id' not in request.form:
        return jsonify({"error": "No image_id provided"}), 400

    image_id = request.form['image_id']
    task = process_image_task.delay(image_id)

    # Return a response with the task ID
    return jsonify({"task_id": task.id}), 202

'''
@app.route('/status/<task_id>')
def task_status(task_id):
    task = process_image_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result,
            'status': task.status
        }
        if task.state == 'SUCCESS':
            # Here you can handle the successful task result,
            # e.g., insert the result into the database if needed.
            pass
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
'''
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
