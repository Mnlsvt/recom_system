import json

def list_to_string(lst):
    if not lst:
        return "?"
    flat_list = [item for sublist in lst for item in sublist]  # Flattening the list of lists
    return ", ".join(flat_list)

def process_file(file_path, all_data):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            all_data.extend(data)
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")

# List of your JSON files
json_files = [
    'all_image_metadata_cars.json', 'all_image_metadata_fitness.json', 'all_image_metadata_food.json',
    'all_image_metadata_gaming.json', 'all_image_metadata_houses.json', 'all_image_metadata_movies.json',
    'all_image_metadata_nature.json', 'all_image_metadata_pets.json', 'all_image_metadata_sports.json']  # Add your file names here

all_data = []
for json_file in json_files:
    process_file(json_file, all_data)

# Preparing the ARFF file content
arff_content = "@RELATION your_data\n\n"
arff_content += "@ATTRIBUTE attribute_predictions STRING\n"
# The objectsScore NUMERIC line should be removed if you are not including it in the @DATA section.
arff_content += "@ATTRIBUTE backgroundSpace STRING\n"
arff_content += "@ATTRIBUTE objectsFound STRING\n"
arff_content += "@ATTRIBUTE class {fitness,cars,food,gaming,houses,movies,nature,pets,sports}\n\n"  # Update the classes as needed
arff_content += "@DATA\n"

for entry in all_data:
    attr_predictions = list_to_string(entry.get('attribute_predictions', []))
    background_space = list_to_string(entry.get('backgroundSpace', []))
    objects_found = list_to_string(entry.get('objectsFound', []))
    class_label = entry.get('class', '?')
    # Make sure the data rows match the header format
    arff_content += f"\"{attr_predictions}\",\"{background_space}\",\"{objects_found}\",{class_label}\n"


# Save the ARFF content to a file
try:
    with open('combined_output.arff', 'w') as file:
        file.write(arff_content)
    print("Combined ARFF file created successfully.")
except IOError as e:
    print(f"Error writing to file: {e}")