import subprocess
from PIL import Image
import tensorflow as tf
import torchvision.transforms as T
import os
import ast
from collections import defaultdict


def configure_gpu():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Restrict TensorFlow to only allocate a fraction of the total memory
            # Replace 0.5 with the fraction of memory to allocate
            tf.config.experimental.set_memory_growth(gpus[0], True)
            tf.config.experimental.set_virtual_device_configuration(
                gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=512 * 1)])  # Set limit here
        except RuntimeError as e:
            print(e)


# Configure GPU to use memory growth
configure_gpu()

# Code that runs resnet18, resnet50 and alexnet models and gets their outputs in a 3d array called predictions

predictions = [[['' for k in range(3)] for j in range(3)] for i in range(4)]

images = "../../test_images/street2.jpeg"

with open('unified_code.py', 'r+') as unifiedf:
        content_unifiedf = unifiedf.readlines()
        for i, line in enumerate(content_unifiedf):
            if 'images =' in line:
                content_unifiedf[i] = 'images = "%s"\n' %images  # Modify the line with the new value
                break  # Stop searching for the line once found
        unifiedf.seek(0)  # Go back to the beginning of the file
        unifiedf.writelines(content_unifiedf)  # Write the modified content back to the file
        unifiedf.truncate()

for k in range(3):
    if (k == 0):
        arch = "resnet18"
    elif (k == 1):
        arch = "resnet50"
    else:
        arch = "alexnet"
    with open('basic_code.py', 'r+') as file:
        content = file.readlines()
        for i, line in enumerate(content):
            if 'arch =' in line:
                content[i] = 'arch = "%s"\n' %arch  # Modify the line with the new value
            elif 'images =' in line:
                content[i] = 'images = "%s"\n' %images  # Modify the line with the new value
                break  # Stop searching for the line once found
        file.seek(0)  # Go back to the beginning of the file
        file.writelines(content)  # Write the modified content back to the file



    # run basic_code.py and capture its output
    result = subprocess.run(['python3', 'basic_code.py'], stdout=subprocess.PIPE)

    # get the output of script1.py as input
    input_data = result.stdout.decode('utf-8').strip()

    # do something with the input data
    #predictions = [['',''],['',''],['','']]
    print("\n\n\ninputdata",input_data)
    print("\n\n\npredictions",predictions)
    for i in range(3):
        pred_lines = input_data.split('\n')[i+1]
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
            predictions[k][i][0] = arch
            predictions[k][i][1] = pred_acc
            predictions[k][i][2] = pred1
        else:
            predictions[k][i][0] = "none"
            predictions[k][i][1] = "none"
            predictions[k][i][2] = "none"
        #print(pred_acc, pred1)
#print(predictions)

print("\n\n\n",predictions)

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
'''print(object_rec_data[8])
result_objects = object_rec_data[8]

result_objectsList = ast.literal_eval(result_objects)

#test
print(result_objectsList)

final_objectsList = []

for item in result_objectsList:
    final_objectsList.append(item[0])

print(final_objectsList)'''
