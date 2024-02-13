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
    score_list = score_tensor.tolist()
    #labels_list = list(set(labels_list))
    labels_list_temp = []
    score_list_temp = []

    # removes duplicates from labels_list (the objects detected) and score_list (the percentage of certainty)
    for i in range(len(labels_list)):
        if labels_list[i] not in labels_list_temp:
            labels_list_temp.append(labels_list[i])
            score_list_temp.append(score_list[i])
    
    labels_list = labels_list_temp
    score_list = score_list_temp

    #print(object_prediction)
    label_dict = {}

    with open('object_classes.txt', 'r') as f:
        for line in f:
            items = line.strip().split('\t') # split by tab
            label_dict[int(items[0])] = items[1:] # convert the first item to integer and assign the rest as value

    final_objects = []
    score_counter = -1
    if labels_list != None:
        for item in labels_list:
            score_counter += 1
            test = 0
            for i in label_dict:
                if ((i == item) and (score_list[score_counter] > 0.55)):
                    #label_dict[i].append('%.3f'%score_list[score_counter])
                    # print(get_label_by_number(label_dict, i), '%.3f'%score_list[score_counter])  # Should print ['person', 'person', 'person', 'person']
                    final_objects.append(get_label_by_number(label_dict, i))
        print(final_objects)
        #print(len(final_objects),"\n\n")

        return final_objects
    else:
        return None


def perform_object_recognition(image_path):
    # Load the models
    current_dir = os.path.dirname(os.path.abspath(__file__))
    object_model_file1 = os.path.join(current_dir, '..', '..', '..', 'models', 'fasterrcnn_resnet50_fpn_coco-258fb6c6.pth')
    object_model_file2 = os.path.join(current_dir, '..', '..', '..', 'models', 'maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth')

    model1 = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)
    model1.load_state_dict(torch.load(object_model_file1))
    model1.eval()

    model2 = torchvision.models.detection.maskrcnn_resnet50_fpn(weights=None)
    model2.load_state_dict(torch.load(object_model_file2))
    model2.eval()

    # Load and transform the image
    img = Image.open(image_path)
    transform = T.ToTensor()
    img_transformed = transform(img)

    # Perform object detection
    with torch.no_grad():
        object_prediction1 = model1([img_transformed])
        object_prediction2 = model2([img_transformed])

    final_objects1 = identify_objects(object_prediction1)
    final_objects2 = identify_objects(object_prediction2)

    # Combine and process the results
    objects_count = final_objects1 + final_objects2
    counts = defaultdict(int)
    unique_objects_count_dict = {}

    for sublist in objects_count:
        counts[sublist[0]] += 1

    for sublist in objects_count:
        if counts[sublist[0]] > 1 and (sublist[0] not in unique_objects_count_dict):
            unique_objects_count_dict[sublist[0]] = sublist

    duplicate_objects_count = list(unique_objects_count_dict.values())
    return duplicate_objects_count