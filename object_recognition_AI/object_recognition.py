import torch
import torchvision
from PIL import Image
import torchvision.transforms as T
import os
from collections import defaultdict

def get_label_by_number(label_dict1, number):
    return label_dict1[number]

def identify_objects(object_prediction):
    # Extracting the 'labels' part of the dictionary output
    # labels_tensor = object_prediction2['labels']
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
    # print(labels_list2)


    label_dict = {}

    with open('object_classes.txt', 'r') as f:
        for line in f:
            items = line.strip().split('\t') # split by tab
            label_dict[int(items[0])] = items[1:] # convert the first item to integer and assign the rest as value

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
    print(len(final_objects),"\n\n")

    return final_objects



# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

images = "temp_img/zM4hNQ7bsH07jJk6QqW6.jpg"


#images_obj_path = '/home/mnlsvt/Desktop/ptuxiakh/test_images/' + images
images_obj_path = os.path.join(current_dir, '%s' %images)
images_obj = Image.open(images_obj_path)

current_dir = os.path.dirname(os.path.abspath(__file__))
object_model_file1 = os.path.join(current_dir, '..', '..', 'models', 'fasterrcnn_resnet50_fpn_coco-258fb6c6.pth')
object_model_file2 = os.path.join(current_dir, '..', '..', 'models', 'maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth')

# model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=False) # Do not download weights
model1 = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)

#model.load_state_dict(torch.load(current_dir, '..', 'models', 'fasterrcnn_resnet50_fpn.pth'))
model1.load_state_dict(torch.load(object_model_file1))
model1.eval() # Make sure to call model.eval() to set dropout and batch normalization layers to evaluation mode

# Load an image and convert it to a PyTorch tensor
transform = T.Compose([T.ToTensor()])
images_obj_transformed = transform(images_obj)

# Get predictions
with torch.no_grad():
    object_prediction1 = model1([images_obj_transformed])

final_objects1 = identify_objects(object_prediction1)




model2 = torchvision.models.detection.maskrcnn_resnet50_fpn(weights=None) # Do not download weights
model2.load_state_dict(torch.load(object_model_file2))
model2.eval() # Make sure to call model.eval() to set dropout and batch normalization layers to evaluation mode


# Load an image
transform = torchvision.transforms.ToTensor()
images_obj_transformed = transform(images_obj)

# Perform prediction
with torch.no_grad():
    object_prediction2 = model2([images_obj_transformed])

final_objects2 = identify_objects(object_prediction2)


objects_count = final_objects1 + final_objects2 # combined_predictions is an array of the common predictions that the models had
counts = defaultdict(int)
unique_objects_count_dict = {}

for sublist in objects_count:
    counts[sublist[0]] += 1

for sublist in objects_count:
    if counts[sublist[0]] > 1 and (sublist[0] not in unique_objects_count_dict or sublist[2] > unique_objects_count_dict[sublist[0]][2]):
        unique_objects_count_dict[sublist[0]] = sublist

duplicate_objects_count = list(unique_objects_count_dict.values())
print(duplicate_objects_count)
