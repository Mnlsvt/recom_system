import json
import os

data_directory = '.'
file_names = ['all_image_metadata_cars.json', 'all_image_metadata_fitness.json', 'all_image_metadata_food.json', 'all_image_metadata_gaming.json', 'all_image_metadata_houses.json', 'all_image_metadata_movies.json', 'all_image_metadata_nature.json', 'all_image_metadata_pets.json', 'all_image_metadata_sports.json']  # Add all your file names here
combined_data = []

for file_name in file_names:
    file_path = os.path.join(data_directory, file_name)
    with open(file_path, 'r') as file:
        data = json.load(file)
        combined_data.extend(data)

# Save the combined data to a new JSON file
with open('combined_data.json', 'w') as file:
    json.dump(combined_data, file)

print("All JSON files have been combined into 'combined_data.json'")
