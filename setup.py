import os
import shutil
import requests
import subprocess

def generate_model_folder():
    # Create "models/" directory
    os.makedirs("models/", exist_ok=True)

    # URLs for each model
    model_urls: dict = {
        'yolov7x.pt':'https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7x.pt',
        'yolov8x.pt':'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt',
        'yolov8x-pose-p6.pt':'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x-pose-p6.pt',
        'yolov8x-seg.pt':"https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x-seg.pt"
                        }

    # Iterate through name, URL and then downloads it to the "models/" directory
    for model_name, model_url in model_urls.items():
        file_path = os.path.join("models", model_name)
        if os.path.exists(file_path):
            print(f"{model_name} already exists. Skipping download.")
            continue

        print(f"Downloading {model_name}...")
        response = requests.get(model_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"{model_name} downloaded successfully.")
        else:
            print(f"Failed to download {model_name}. Status code: {response.status_code}")


def clone_git_repo(repo_name, repo_url, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    repo_folder = os.path.join(destination_folder, repo_name)
    
    if os.path.exists(repo_folder):
        print(f"Repository '{repo_name}' already exists. Skipping clone.")
    else:
        print(f"Cloning '{repo_name}' repository...")
        subprocess.run(["git", "clone", repo_url, repo_folder])
        print(f"Repository '{repo_name}' cloned successfully.")

def move_files(source_folder, dest_folder, file_extensions):
    for root, _, files in os.walk(source_folder):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, source_folder)
            dest_path = os.path.join(dest_folder, relative_path)
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            if file.endswith(file_extensions):
                shutil.move(source_path, dest_path)
                print(f"Moved: {file}")
            
            if '_gpu' in file:
                shutil.move(source_path, os.getcwd())
                print(f"Moved: {file}")

    # After moving the files, delete the "source_folder"
    shutil.rmtree(source_folder)
    print(f"Deleted: {source_folder}")

def generate_yolov7_folder():
    github_repo_urls = {
        'yolov7': 'https://github.com/WongKinYiu/yolov7.git',
        'yolov7_tracking': 'https://github.com/haroonshakeel/yolov7-object-tracking.git'
    }

    # Clone repositories
    for repo_name, repo_url in github_repo_urls.items():
        clone_git_repo(repo_name, repo_url, os.getcwd())

    # Move .py and .txt files from 'yolov7_tracking' to 'yolov7'
    source_folder = "yolov7_tracking/"
    dest_folder = "yolov7/"
    file_extensions = ('.py')
    move_files(source_folder, dest_folder, file_extensions)


if __name__ == "__main__":
    generate_model_folder()
    generate_yolov7_folder()