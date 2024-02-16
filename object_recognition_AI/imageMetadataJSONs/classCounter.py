import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Load the data
with open('/home/mnlsvt/Desktop/ptuxiakh/recom_system/object_recognition_AI/imageMetadataJSONs/combined_data.json', 'r') as file:
    data = json.load(file)

# Analyze class distribution
class_counts = Counter(item['class'] for item in data)

# Plot class distribution
plt.figure(figsize=(10, 6))
sns.barplot(x=list(class_counts.keys()), y=list(class_counts.values()))
plt.title('Class Distribution')
plt.xlabel('Class')
plt.ylabel('Count')
plt.show()

# Repeat similar steps for analyzing attribute predictions
