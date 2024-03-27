import zipfile
import os
import shutil


def move_files_to_dir(source_dir, target_dir):
    """Move all files from source_dir and its subdirectories to target_dir."""
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Move each file to the target_dir
            shutil.move(os.path.join(root, file), os.path.join(target_dir, file))


def extract_and_relocate_files(folder_path):
    # Step 1: Create a temporary folder within the current directory
    temp_dir = os.path.join(folder_path, 'Temporary')
    os.makedirs(temp_dir, exist_ok=True)

    # Step 2: Iterate through each zip file in the folder path
    for item in os.listdir(folder_path):
        if item.endswith('.zip') and os.path.isfile(os.path.join(folder_path, item)):
            zip_file_path = os.path.join(folder_path, item)
            # Step 3: Create a folder for each zip file
            dir_name = item[:-4]  # Remove .zip extension
            new_dir_path = os.path.join(folder_path, dir_name)
            os.makedirs(new_dir_path, exist_ok=True)

            # Step 3: Extract the contents of the zip file into the temporary folder
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Step 4: Go through all subfolders within the temporary folder
            move_files_to_dir(temp_dir, new_dir_path)

            # Clear the temporary directory for the next zip file
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

    # Delete the temporary folder after all zip files are processed
    shutil.rmtree(temp_dir)


# Replace 'path/to/your/folder' with the path to your folder containing the zip files
folder_path = '../IP_BGP/Post-Poisoning/30/'
extract_and_relocate_files(folder_path)

print('Files have been extracted and moved to their respective directories.')
