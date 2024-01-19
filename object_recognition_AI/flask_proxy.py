from firebase_admin import firestore, credentials
from flask import Flask, request, jsonify
import requests
import firebase_admin
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(script_dir, "ptuxiakhmanwlhs-firebase-adminsdk.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ptuxiakhmanwlhs.appspot.com'
})

db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['POST'])
def predict():
    # Get the form data from the request
    form_data = request.form

    # Forward the request to the local server
    local_server_url = "http://manolisvt.com:5000/predict"  # Replace with your local server URL
    response = requests.post(local_server_url, data=form_data, timeout=120)

    # Parse the response from the local server
    response_data = response.json()
    print("geia", response_data)

    # Get the document reference from the form data
    doc_ref = db.collection('images').document(form_data['image_id'])

   # Convert the attribute predictions to a list of strings
    attribute_predictions = [str(attr) for attr in response_data['attribute_predictions']]

   # Convert the objectsFound to a list of strings
    objectsFound = [str(attr) for attr in response_data['objectsFound']]

   # Convert the objectsFound to a list of strings
    objectsScore = [str(attr) for attr in response_data['objectsScore']]

    # Update the document with the metadata
    doc_ref.set({
        'metadata': {
            'attribute_predictions': attribute_predictions,
            'backgroundSpace': response_data['backgroundSpace'],
            'objectsFound': objectsFound,
            'objectsScore': objectsScore
        }
    }, merge=True)

    # Return the response from the local server
    return jsonify({
        'attribute_predictions': attribute_predictions,
        'backgroundSpace': response_data['backgroundSpace'],
        'objectsFound': objectsFound,
        'objectsScore': objectsScore
    })


if __name__ == "__main__":
    app.run()