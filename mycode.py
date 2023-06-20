
import subprocess
import re
import torch
import torchvision
from PIL import Image
import torchvision.transforms as T
import os


# Code that runs resnet18, resnet50 and alexnet models and gets their outputs in a 3d array called predictions

predictions = [[['' for k in range(3)] for j in range(3)] for i in range(4)]

images = "street3.jpg"

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
combined_predictions = []

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

images_obj_path = '/home/mnlsvt/Desktop/ptuxiakh/test_images/' + images
images_obj = Image.open(images_obj_path)

current_dir = os.path.dirname(os.path.abspath(__file__))
# object_model_file = os.path.join(current_dir, '..', '..', 'models', 'fasterrcnn_resnet50_fpn_coco-258fb6c6.pth')
object_model_file = '/home/mnlsvt/Desktop/ptuxiakh/models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth'

# model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False) # Do not download weights
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)

#model.load_state_dict(torch.load(current_dir, '..', 'models', 'fasterrcnn_resnet50_fpn.pth'))
model.load_state_dict(torch.load(object_model_file))
model.eval() # Make sure to call model.eval() to set dropout and batch normalization layers to evaluation mode

# Load an image and convert it to a PyTorch tensor
transform = T.Compose([T.ToTensor()])
images_obj = transform(images_obj)

# Get predictions
with torch.no_grad():
    object_prediction = model([images_obj])


# Extracting the 'labels' part of the dictionary output
# labels_tensor = object_prediction['labels']
for item in object_prediction:
    if 'labels' in item:
        labels_tensor = item['labels']

for item in object_prediction:
    if 'scores' in item:
        score_tensor = item['scores']
# Converting the tensor to a list
labels_list = labels_tensor.tolist()
labels_list = list(set(labels_list))
score_list = score_tensor.tolist()
# print(labels_list)

# Read the object classes file
label_dict = {}

with open('object_classes.txt', 'r') as f:
    for line in f:
        items = line.strip().split('\t') # split by tab
        label_dict[int(items[0])] = items[1:] # convert the first item to integer and assign the rest as value

# print(label_dict)

def get_label_by_number(label_dict, number):
    return label_dict[number]

final_objects = []
score_counter = 0
for item in labels_list:
    score_counter += 1
    for i in label_dict:
        if ((i == item) and (score_list[score_counter] > 0.55)):
            label_dict[i].append('%.3f'%score_list[score_counter])
            # print(get_label_by_number(label_dict, i), '%.3f'%score_list[score_counter])  # Should print ['person', 'person', 'person', 'person']
            final_objects.append(get_label_by_number(label_dict, i))
print(final_objects)