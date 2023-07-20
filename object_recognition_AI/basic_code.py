# PlacesCNN for scene classification
#
# by Bolei Zhou
# last modified by Bolei Zhou, Dec.27, 2017 with latest pytorch and torchvision (upgrade your torchvision please if there is trn.Resize error)

import torch
from torch.autograd import Variable as V
import torchvision.models as models
from torchvision import transforms as trn
from torch.nn import functional as F
import os
from PIL import Image

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))


# the architecture to use
arch = "alexnet"
images = "temp_img/zM4hNQ7bsH07jJk6QqW6.jpg"

# load the pre-trained weights
model_file = os.path.join(current_dir, '..', '..', 'models', '%s_places365.pth.tar' %arch)
#if not os.access(model_file, os.W_OK):
#    model_file = '%s_places365.pth.tar' %arch
#    weight_url = 'http://places2.csail.mit.edu/models_places365/' + model_file
#    os.system('wget ' + weight_url)

model = models.__dict__[arch](num_classes=365)
checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
model.load_state_dict(state_dict)
model.eval()


# load the image transformer
centre_crop = trn.Compose([
        trn.Resize((256,256)),
        trn.CenterCrop(224),
        trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# load the class label
file_name = 'categories_places365.txt'
if not os.access(file_name, os.W_OK):
    synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
    os.system('wget ' + synset_url)
classes = list()
with open(file_name) as class_file:
    for line in class_file:
        classes.append(line.strip().split(' ')[0][3:])
classes = tuple(classes)

# load the test image
#img_name = '../test_images/%s' %images
img_name = os.path.join(current_dir, '%s' %images)

img = Image.open(img_name)
input_img = V(centre_crop(img).unsqueeze(0))


# forward pass
logit = model.forward(input_img)
h_x = F.softmax(logit, 1).data.squeeze()
probs, idx = h_x.sort(0, True)

print('{} prediction on {}'.format(arch,img_name))
# output the prediction
for i in range(0, 3):
    print('{:.3f} -> {}'.format(probs[i], classes[idx[i]]))

















































































































































































































































































































































































































