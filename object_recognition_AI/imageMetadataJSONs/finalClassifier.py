import tensorflow as tf
import joblib
import numpy as np
import pandas as pd

# Load saved model, vectorizer, and encoder
model = tf.keras.models.load_model('../classModel.keras')
vectorizer = joblib.load('../vectorizer.pkl')
encoder = joblib.load('../encoder.pkl')
label_encoder = joblib.load('../label_encoder.pkl')

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

# Example usage
test_input = {
    "attribute_predictions": ["natural light", "man-made", "open area", "driving", "transporting", "asphalt", "sunny", "biking", "pavement"],
    "backgroundSpace": ["auto_showroom"],
    "objectsFound": [["car", "vehicle"], ["car", "vehicle"], ["truck", "vehicle"], ["car", "vehicle"]]
}
# print(label_encoder.classes_)

predicted_class = make_prediction(test_input)
predicted_class_name = label_encoder.inverse_transform(predicted_class)[0]
print("Predicted Class:", predicted_class_name)
