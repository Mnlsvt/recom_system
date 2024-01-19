import subprocess
from PIL import Image
import torchvision.transforms as T
import os
import ast
import json
import numpy as np
import ast

# Function to determine if a file is an image
def is_image_file(filename):
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        if filename.lower().endswith(ext):
            return True
    return False

# Function to extract class name from directory name
def extract_class_name(image_path):
    return os.path.basename(os.path.dirname(image_path))

def parse_objects_found(data):
    parsed_data = []
    for element in data:
        try:
            # Parse the string as a list
            parsed_element = ast.literal_eval(element)
            if isinstance(parsed_element, list):
                # Extend the main list with elements of the parsed list
                parsed_data.extend(parsed_element)
            else:
                # Directly append non-list elements
                parsed_data.append(element)
        except (ValueError, SyntaxError) as e:
            print("Error parsing element:", element, "Error:", e)
            # Append the original element if it can't be parsed
            parsed_data.append(element)
    return parsed_data

# Directory containing images
directory = input("what is the path of the images?\n")

# List to hold data for all images
all_image_data = []
images_count = 0

# Loop through all files in the directory
for filename in os.listdir(directory):
    if is_image_file(filename):
        images = os.path.join(directory, filename)
        images_count += 1
        print("image number:", images_count, "\n")

        predictions = [[['' for _ in range(3)] for _ in range(3)] for _ in range(4)]

        with open('unified_code.py', 'r+') as unifiedf:
            content_unifiedf = unifiedf.readlines()
            for i, line in enumerate(content_unifiedf):
                if 'images =' in line:
                    content_unifiedf[i] = 'images = "{}"\n'.format(images)  # Modify the line with the new value
                    break  # Stop searching for the line once found
            unifiedf.seek(0)  # Go back to the beginning of the file
            unifiedf.writelines(content_unifiedf)  # Write the modified content back to the file
            unifiedf.truncate()

        for k in range(3):
            if k == 0:
                arch = "resnet18"
            elif k == 1:
                arch = "resnet50"
            else:
                arch = "alexnet"
            with open('basic_code.py', 'r+') as file:
                content = file.readlines()
                for i, line in enumerate(content):
                    if 'arch =' in line:
                        content[i] = 'arch = "{}"\n'.format(arch)  # Modify the line with the new value
                    elif 'images =' in line:
                        content[i] = 'images = "{}"\n'.format(images)  # Modify the line with the new value
                        break  # Stop searching for the line once found
                file.seek(0)  # Go back to the beginning of the file
                file.writelines(content)  # Write the modified content back to the file

            # Image preprocessing
            transform = T.Compose([
                T.Resize(256),
                T.CenterCrop(224),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            # Load and preprocess the image
            try:
                img = Image.open(images)
                img = img.convert("RGB")  # Ensure that the image has 3 channels (RGB)
                img = transform(img)

                # Convert PyTorch tensor to NumPy array and then to bytes
                img_bytes = img.numpy().tobytes()

                # run basic_code.py and capture its output
                result = subprocess.run(['python3', 'basic_code.py'], stdout=subprocess.PIPE, input=img_bytes)

                # get the output of script1.py as input
                input_data = result.stdout.decode('utf-8').strip()

                # do something with the input data
                if input_data.count('\n') >= 3:
                    for i in range(3):
                        pred_lines = input_data.split('\n')[i + 1]
                        # find the accuracy of each possible prediction
                        if len(pred_lines) >= 5:
                            pred_acc = pred_lines[2:5]

                    # keep a string of the possible prediction's name
                    pred1 = ""
                    space_count = 0
                    for j in pred_lines:
                        if (space_count == 1):
                            if (j != " "):
                                pred1 += j
                        if (j == ">"):
                            space_count = 1
                    space_count = 0
                    if (int(pred_acc) >= 200):
                        predictions[k][i][0] = arch
                        predictions[k][i][1] = pred_acc
                        predictions[k][i][2] = pred1
                    else:
                        predictions[k][i][0] = "none"
                        predictions[k][i][1] = "none"
                        predictions[k][i][2] = "none"
                    #print(pred_acc, pred1)
                #print(predictions)

                '''
                predictions is a 3d array in which the values are assigned like this:

                [
                    3x arches
                    [
                        3x predictions
                        [arch1, acc1, prediction_name1]
                        [arch1, acc2, prediction_name2]
                        [arch1, acc3, prediction_name3]
                        .
                        .
                        .
                    ]
                    .
                    .
                    .
                ]
                '''

                # Code that runs the wideresnet model and gets the image attributes as well

                # Attributes that the widerestnet model extracts from the image
                attribute_predictions = []

                # run basic_code.py and capture its output
                result = subprocess.run(['python3', 'unified_code.py'], stdout=subprocess.PIPE)

                # get the output of script1.py as input
                input_data = result.stdout.decode('utf-8').strip()
                arch = "widerestnet"

                # do something with the input data

                for i in range(3):
                    pred_lines = input_data.split('\n')[i+2]
                    
                    # find the accuracy of each possible prediction
                    pred_acc = pred_lines[2:5]

                    # keep a string of the possible prediction's name
                    pred1 = ""
                    space_count = 0
                    for j in pred_lines:
                        if (space_count == 1):
                            if (j != " "):
                                pred1 += j
                        if (j == ">"):
                            space_count = 1
                    space_count = 0
                    if (int(pred_acc) >= 200):
                        predictions[3][i][0] = arch
                        predictions[3][i][1] = pred_acc
                        predictions[3][i][2] = pred1
                    else:
                        predictions[k][i][0] = "none"
                        predictions[k][i][1] = "none"
                        predictions[k][i][2] = "none"
                    #print(pred_acc, pred1)
                pred_lines_attr = input_data.split('\n')
                pred_attr = pred_lines_attr[-2]
                pred_attr += ","

                #for j in range(9): # 9 is the number of the attributes that we take from the widerestnet model
                temp_word = ""
                word_counter = 0
                for n in (pred_attr):
                    if (n != ","):
                        temp_word += n
                    else:
                        if (temp_word[0] == " "):
                            temp_word = temp_word[1:]
                        attribute_predictions.append(temp_word)
                        temp_word = ""
                        word_counter += 1

                predictions = [[cell for cell in row if 'none' not in cell] for row in predictions if any('none' not in cell for cell in row)]
                predictions = [[cell for cell in row if '' not in cell] for row in predictions if any('' not in cell for cell in row)]

                print("Scene recognition:\n\n")

                if len(predictions) > 0:
                    print(predictions[0],"\n")
                if len(predictions) > 1:
                    print(predictions[1],"\n")
                if len(predictions) > 2:
                    print(predictions[2],"\n")
                if len(predictions) > 3:
                    print(predictions[3],"\n")

                print(attribute_predictions)

                # combined_predictions is an array of the common predictions that the models had

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

                print(word_count)

                                                #Object Recognition code bellow


                with open('object_recognition.py', 'r+') as object:
                        content_object = object.readlines()
                        for i, line in enumerate(content_object):
                            if 'images =' in line:
                                content_object[i] = 'images = "%s"\n' %images  # Modify the line with the new value
                                break  # Stop searching for the line once found
                        object.seek(0)  # Go back to the beginning of the file
                        object.writelines(content_object)  # Write the modified content back to the file
                        object.truncate()

                print("\n\nObject recognition:\n\n")

                result_obj = subprocess.run(['python3', 'object_recognition.py'], stdout=subprocess.PIPE)
                object_rec_data = result_obj.stdout.decode('utf-8').strip()
                print(object_rec_data,"\n\n")
                object_rec_data = object_rec_data.split('\n')


                # Extract class name from directory
                class_name = extract_class_name(images)

                parsed_data = parse_objects_found(object_rec_data)

                # Combine metadata and class name into a single entry
                data_entry = {
                    "attribute_predictions": attribute_predictions,
                    "objectsScore": [cell[1] for row in predictions for cell in row],
                    "backgroundSpace": [cell[2] for row in predictions for cell in row],  # Populate this if you have the data
                    "objectsFound": parsed_data,
                    "class": class_name
                }

                # Append the data entry to the list for all images
                all_image_data.append(data_entry)

                # Open the JSON file, append it with the new data, and close it
                with open('all_image_metadata_house.json', 'a') as outfile:
                    json.dump(data_entry, outfile, indent=4)
                    outfile.write(',\n')  # Add a newline to separate JSON objects

                # Clear the attribute_predictions list for the next image
                attribute_predictions = []
            except Exception as e:
                # Handle the exception (e.g., print an error message)
                print(f"Error processing image {images}: {e}")
                continue  # Skip to the next image


result_obj = subprocess.run(['python3', 'object_recognition.py'], stdout=subprocess.PIPE)
object_rec_data = result_obj.stdout.decode('utf-8').strip()
print(object_rec_data, "\n\n")
object_rec_data = object_rec_data.split('\n')
'''print(object_rec_data[8])
result_objects = object_rec_data[8]

result_objectsList = ast.literal_eval(result_objects)

#test
print(result_objectsList)

final_objectsList = []

for item in result_objectsList:
    final_objectsList.append(item[0])

print(final_objectsList)'''
