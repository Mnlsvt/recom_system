from flask import Flask, request, jsonify
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load saved model, vectorizer, encoder, and label encoder
model = tf.keras.models.load_model('classModel.keras')
vectorizer = joblib.load('vectorizer.pkl')
encoder = joblib.load('encoder.pkl')
label_encoder = joblib.load('label_encoder.pkl')

def preprocess_input(input_data, vectorizer, encoder):
    df = pd.DataFrame([input_data])
    df['attribute_predictions_str'] = df['attribute_predictions'].apply(lambda x: ' '.join(x))
    df['objectsFound_str'] = df['objectsFound'].apply(lambda x: ' '.join([' '.join(pair) for pair in x]))
    df['backgroundSpace_str'] = df['backgroundSpace'].apply(lambda x: ' '.join(x) if x else 'None')

    attributes_vec = vectorizer.transform(df['attribute_predictions_str']).toarray()
    objects_vec = vectorizer.transform(df['objectsFound_str']).toarray()
    background_vec = encoder.transform(df[['backgroundSpace_str']]).toarray()

    return np.hstack((attributes_vec, objects_vec, background_vec))

def make_prediction(input_data):
    input_features = preprocess_input(input_data, vectorizer, encoder)
    prediction = model.predict(input_features)
    predicted_class = np.argmax(prediction, axis=1)
    return predicted_class

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.json
        predicted_class = make_prediction(input_data)
        predicted_class_name = label_encoder.inverse_transform(predicted_class)[0]
        return jsonify({'predicted_class': predicted_class_name})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
