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
from openai import OpenAI
import json, re

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


def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print("Download complete!")
    else:
        print("Failed to download the file.")


def extract_json_from_response(response_obj):
    try:
        # Accessing the 'choices' attribute and then the 'content' of the 'message'
        message_content = response_obj.choices[0].message.content
        print(f"Original Message Content: {message_content}")  # Debugging print

        # Stripping the triple backticks and any additional whitespace from the content
        json_str = re.sub(r'^```json\n|\n```$', '', message_content).strip()
        print(f"JSON String after stripping: {json_str}")  # Debugging print

        # Checking if the JSON string is empty
        if not json_str:
            print("Extracted JSON string is empty.")
            return None

        # Parsing the JSON string into a Python dictionary
        json_data = json.loads(json_str)

        return json_data
    except (AttributeError, IndexError, json.JSONDecodeError) as e:
        print(f"Error while extracting JSON: {e}")
        return None




@celery.task(name='flask_local_with_class_gpt.process_image_task_gpt', ignore_result=False, soft_time_limit=30, time_limit=60, rate_limit='3/m')
def process_image_task_gpt(image_id):

    # Get the document from the database
    doc = db.collection(u'images').document(image_id).get()
    
    #doc_ref = db.collection(u'images').document(image_id)

    url = doc.to_dict()['url']

    gptText = '''Give me the metadata of this image. The format is {'image_id': '%s', 'attribute_predictions': [], 'backgroundSpace': [], 'objectsFound': [], 'predicted_class': '', 'gpt': '%s'}
    
    where 'image_id' is the id of the image, 'attribute_predictions' is a list of of 1-2 word strings with information about how the predection happened 
    (e.g. natural-light etc), 'backgroundSpace' is a list of strings that tells what is the bg of the image (e.g. coffee shop), 'objectsFound' is a list of the detected objects, and 'predicted_class' is a the final classification.
    Classify the image in one of these classes: cars, fitness, food, gaming, houses, movies, nature, pets, sports, unknown.
    
    Return only this json and nothing else.
    '''
    


    gptText = gptText % (image_id, "yes")

    print(url)

    api_key = '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'
    client = OpenAI(api_key=api_key)

    response_data = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": gptText},
            {
            "type": "image_url",
            "image_url": {
                "url": url,
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    print(type(response_data))

    extracted_json = extract_json_from_response(response_data)

    #os.remove(filename2)


    print("responsedata", response_data)
    print('\n\n',extracted_json)
    # Return the response data so that it can be accessed when the task is complete
    #return response_data

    proxy_url = "https://MnLsVt.pythonanywhere.com/update_data"  # Replace with your proxy URL


    # Send the data to the proxy
    try:
        requests.post(proxy_url, json=extracted_json)
        print("metadata sent")
    except Exception as e:
        print("error sending the metadata")

@app.route('/predict', methods=['POST'])
def predict():
    if 'image_id' not in request.form:
        return jsonify({"error": "No image_id provided"}), 400

    image_id = request.form['image_id']
    task = process_image_task_gpt.delay(image_id)

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
