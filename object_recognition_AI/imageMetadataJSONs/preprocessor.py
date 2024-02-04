'''import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import pandas as pd

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def preprocess_data(data):
    df = pd.DataFrame(data)
    df['attribute_predictions_str'] = df['attribute_predictions'].apply(lambda x: ' '.join(x))
    df['objectsFound_str'] = df['objectsFound'].apply(lambda x: ' '.join([item for sublist in x for item in sublist]))
    df['backgroundSpace_str'] = df['backgroundSpace'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)

    attributes_vec = vectorizer.fit_transform(df['attribute_predictions_str']).toarray()
    objects_vec = vectorizer.fit_transform(df['objectsFound_str']).toarray()
    background_vec = encoder.fit_transform(df[['backgroundSpace_str']]).toarray()

    features = np.hstack((attributes_vec, objects_vec, background_vec))
    return features, df['class'].values

# Initialize vectorizer and encoder
vectorizer = CountVectorizer()
encoder = OneHotEncoder()

# Assuming all JSON files are in the 'data_directory' and have consistent naming
data_directory = '.' #'path_to_your_json_files_directory'
file_names = ['all_image_metadata_cars.json', 'all_image_metadata_fitness.json', 'all_image_metadata_food.json', 'all_image_metadata_gaming.json', 'all_image_metadata_houses.json', 'all_image_metadata_movies.json', 'all_image_metadata_nature.json', 'all_image_metadata_pets.json', 'all_image_metadata_sports.json']  # Add all your file names here

combined_features = []
combined_labels = []

for file_name in file_names:
    file_path = os.path.join(data_directory, file_name)
    data = load_json(file_path)
    features, labels = preprocess_data(data)
    combined_features.extend(features.tolist())  # Convert numpy array to list
    combined_labels.extend(labels)

# Prepare data for TensorFlow
combined_data_for_tensorflow = {
    "features": combined_features,
    "labels": combined_labels
}

# Save to new JSON file in a format suitable for TensorFlow
with open('preprocessed_data_for_tensorflow.json', 'w') as file:
    json.dump(combined_data_for_tensorflow, file)

print("Preprocessing complete. Data saved to 'preprocessed_data_for_tensorflow.json'")
'''



import numpy as np
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

def preprocess_data(data):
    df = pd.DataFrame(data)

    # Convert lists to strings for textual data
    df['attribute_predictions_str'] = df['attribute_predictions'].apply(lambda x: ' '.join(x))
    df['objectsFound_str'] = df['objectsFound'].apply(lambda x: ' '.join([' '.join(pair) for pair in x]))
    df['backgroundSpace_str'] = df['backgroundSpace'].apply(lambda x: ' '.join(x) if x else 'None')

    # Initialize vectorizer and encoder
    vectorizer = CountVectorizer()
    encoder = OneHotEncoder()
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(df['class'])


    # print(label_encoder.classes_)

    # Save the LabelEncoder
    joblib.dump(label_encoder, 'label_encoder.pkl')

    # Fit vectorizers and encoders
    vectorizer.fit(df['attribute_predictions_str'].tolist() + df['objectsFound_str'].tolist())
    encoder.fit(df[['backgroundSpace_str']])
    
    # Transform data using fitted vectorizers and encoders
    attributes_vec = vectorizer.transform(df['attribute_predictions_str']).toarray()
    objects_vec = vectorizer.transform(df['objectsFound_str']).toarray()
    background_vec = encoder.transform(df[['backgroundSpace_str']]).toarray()

    # Combine features
    features = np.hstack((attributes_vec, objects_vec, background_vec))

    # Encode labels
    encoded_labels = label_encoder.fit_transform(df['class'])

    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(encoder, 'encoder.pkl')
    return features, encoded_labels

# Load the combined data
with open('combined_data.json', 'r') as file:
    data = json.load(file)

# Preprocess data
features, encoded_labels = preprocess_data(data)

# Combine features and labels for TensorFlow
combined_data_for_tensorflow = {
    "features": features.tolist(),
    "labels": encoded_labels.tolist()
}

# Save to new JSON file
with open('preprocessed_data_for_tensorflow1.json', 'w') as file:
    json.dump(combined_data_for_tensorflow, file)



print("Preprocessing complete. Data saved to 'preprocessed_data_for_tensorflow.json'")
