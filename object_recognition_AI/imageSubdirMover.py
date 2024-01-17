import os
import shutil
import uuid

def move_and_rename_items_to_target(parent_dir, target_dir):
    """
    Move all files from subdirectories of parent_dir to target_dir.
    Each file is renamed with a UUID to avoid name conflicts.
    """
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Walk through all subdirectories in parent_dir
    for root, dirs, files in os.walk(parent_dir):
        for name in files:
            # Generate a unique UUID
            unique_id = uuid.uuid4()
            # Extract file extension
            extension = os.path.splitext(name)[1]
            # Construct new file name with UUID
            new_name = f"{unique_id}{extension}"
            # Construct the full old and new file paths
            old_file_path = os.path.join(root, name)
            new_file_path = os.path.join(target_dir, new_name)
            # Move and rename the file to the target directory
            shutil.move(old_file_path, new_file_path)


# Usage example:
parent_dir = '/home/mnlsvt/Desktop/ptuxiakh/class_model_train_images/downloads/sports/train'
target_dir = '/home/mnlsvt/Desktop/ptuxiakh/class_model_train_images/downloads/sports/sports'
move_and_rename_items_to_target(parent_dir, target_dir)
