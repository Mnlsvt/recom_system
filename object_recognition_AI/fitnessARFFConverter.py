import json

def list_to_string(lst):
    return ", ".join(lst) if lst else "?"

# Read JSON data from a file
with open('/home/mnlsvt/Desktop/ptuxiakh/recom_system/object_recognition_AI/all_image_metadata_fitness.json', 'r') as file:
    data = json.load(file)

# Preparing the ARFF file content
arff_content = "@RELATION fitness\n\n"
arff_content += "@ATTRIBUTE attribute_predictions STRING\n"
arff_content += "@ATTRIBUTE objectsFound STRING\n"
arff_content += "@ATTRIBUTE class {fitness}\n\n"
arff_content += "@DATA\n"

for entry in data:
    attr_predictions = list_to_string(entry['attribute_predictions'])
    objects_found = list_to_string(entry['objectsFound'])
    class_label = entry['class']
    arff_content += f"\"{attr_predictions}\",\"{objects_found}\",{class_label}\n"

# Save the ARFF content to a file
with open('output.arff', 'w') as file:
    file.write(arff_content)

print("ARFF file created successfully.")
