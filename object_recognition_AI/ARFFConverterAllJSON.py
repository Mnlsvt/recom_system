import json
import os

def list_to_string(lst):
    return ", ".join(lst) if lst else "?"

def process_file(file_path, all_data):
    with open(file_path, 'r') as file:
        data = json.load(file)
        all_data.extend(data)

# List of your JSON files
json_files = [
    'all_image_metadata_cars.json', 'all_image_metadata_fitness.json', 'all_image_metadata_food.json',
    'all_image_metadata_gaming.json', 'all_image_metadata_house.json', 'all_image_metadata_movies.json',
    'all_image_metadata_nature.json', 'all_image_metadata_pets.json', 'all_image_metadata_sports.json']  # Add your file names here

all_data = []
for json_file in json_files:
    process_file(json_file, all_data)

# Preparing the ARFF file content
arff_content = "@RELATION your_data\n\n"
arff_content += "@ATTRIBUTE attribute_predictions STRING\n"
arff_content += "@ATTRIBUTE objectsFound STRING\n"
arff_content += "@ATTRIBUTE class {fitness,cars,food,gaming,house,movies,nature,pets,sports}\n\n"  # Update the classes as needed
arff_content += "@DATA\n"

for entry in all_data:
    attr_predictions = list_to_string(entry['attribute_predictions'])
    objects_found = list_to_string(entry['objectsFound'])
    class_label = entry['class']
    arff_content += f"\"{attr_predictions}\",\"{objects_found}\",{class_label}\n"

# Save the ARFF content to a file
with open('combined_output.arff', 'w') as file:
    file.write(arff_content)

print("Combined ARFF file created successfully.")
