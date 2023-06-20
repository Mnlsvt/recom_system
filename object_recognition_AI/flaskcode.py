from firebase_admin import storage, firestore
from flask import Flask, request
import os
import subprocess
import re
import firebase_admin
from firebase_admin import credentials
from flask import jsonify
import requests

cred = credentials.Certificate("ptuxiakhmanwlhs-firebase-adminsdk-a3vdi-130cba8a2e.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ptuxiakhmanwlhs.appspot.com'
})

# Initialize Firestore DB
db = firestore.client()

app = Flask(__name__)

def download_file(url, destination):
    response = requests.get(url)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print("Download complete!")
    else:
        print("Failed to download the file.")


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files or 'image_id' not in request.form:
        return 'No file or image_id provided', 400

    # Get the file and image_id from the request
    file = request.files['file']
    image_id = request.form['image_id']

    
    # Get the document from Firestore
    doc = db.collection(u'images').document(image_id).get()
    
    doc_ref = db.collection(u'images').document(image_id)

    # Retrieve the file extension from the document
    extension = doc.to_dict()['extension']
    
    url = doc.to_dict()['url']
    
    destination = "/workspace/firstContainer/temp_img/"
    destination += image_id
    destination += "."
    destination += extension
    download_file(url, destination)

    
    # Download the image file from Firebase
    bucket = storage.bucket()
    blob = bucket.blob(image_id)
    print(blob.name)
    filename = os.path.join("/workspace/firstContainer/temp_img", blob.name)
    filename2 = filename
    filename2 += "."
    filename2 += extension
    #blob.download_to_filename(filename)
    
#    temp = r"workspace/firstContainer/temp_img"
#    temp += (blob.name())
#    temp.append(extension)
#    old = r"workspace/firstContainer/temp_img/"
#    old.append(image_id)
#    os.rename(old, temp)

    # Replace 'images = "hair_salon.jpeg"' with 'images = "{filename}"'
    # Similarly for the other scripts and rest of your script

    # mycode:

    # Code that runs resnet18, resnet50 and alexnet models and gets their outputs in a 3d array called predictions

    predictions = [[['' for k in range(3)] for j in range(3)] for i in range(4)]

    images = filename2

    with open('/workspace/firstContainer/recom_system/unified_code.py', 'r+') as unifiedf:
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
        with open('/workspace/firstContainer/recom_system/basic_code.py', 'r+') as file:
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
        result = subprocess.run(['python3', '/workspace/firstContainer/recom_system/basic_code.py'], stdout=subprocess.PIPE)

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


    # Code that runs the wideresnet model and gets the image attributes as well

    # Attributes that the widerestnet model extracts from the image
    attribute_predictions = []

    # run basic_code.py and capture its output
    result = subprocess.run(['python3', '/workspace/firstContainer/recom_system/unified_code.py'], stdout=subprocess.PIPE)

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

    desired_output = list(word_count.keys())
    print(desired_output)

    os.remove(filename2)
    
    # Get the document reference
    
    
    # Create or update the document with the metadata
    doc_ref.set({
        'metadata': {
            'attribute_predictions': attribute_predictions,
            'backgroundSpace': desired_output
        }
    }, merge=True)
    
    # Return the results
    return jsonify({
        "attribute_predictions": attribute_predictions,
        "backgroundSpace": desired_output
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)