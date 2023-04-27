import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
images = "tzallias.jpg"

arch = "densenet161"

# Define the path to the saved model
model_file = os.path.join(current_dir, '..', 'models', '%s_places365.pth.tar' %arch)

# Load the model
model = models.__dict__[arch](num_classes=365)
checkpoint = torch.load(model_file, map_location=lambda storage, loc: storage)
state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
model.load_state_dict(state_dict)
model.eval()

# Define the image transforms
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

img_path = os.path.join(current_dir, '..', 'test_images', '%s' %images)
image = Image.open(img_path)

# Define the function to make predictions
def predict(image_path):
    # Load the image
    

    # Apply the transforms to the image
    image_tensor = transform(image).unsqueeze(0)

    # Make a prediction
    with torch.no_grad():
        output = model(image_tensor)

    # Get the predicted class
    _, predicted = torch.max(output.data, 1)

    return predicted.item()

# Test the function
predicted_class = predict(img_path)
print(predicted_class)






'''import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
images = "tzallias.jpg"

# Load the GoogLeNet model trained on the Places 365 dataset
model = torch.hub.load('pytorch/vision:v0.10.0', 'googlenet', weights=True)
model.eval()

# Load the image and apply the necessary preprocessing
img_path = os.path.join(current_dir, '..', 'test_images', '%s' %images)
image = Image.open(img_path)
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
image_tensor = preprocess(image)
image_tensor = image_tensor.unsqueeze(0)

# Run the image through the model and get the predicted class
with torch.no_grad():
    output = model(image_tensor)
    predicted_class = torch.argmax(output)

# Print out the predicted class label
print(predicted_class.item())
'''