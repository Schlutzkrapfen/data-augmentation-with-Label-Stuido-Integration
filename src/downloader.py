
import yaml
import sys
import json
import requests
from pathlib import Path
from label_studio_sdk import LabelStudio
from label_studio_sdk.core import ApiError

def load_config(file_path="config.yml"):
    """Loads and returns the full config dict."""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file: {e}")
        sys.exit(1)

def load_picture_conf(file_path="config.yml"):
    """Loads picture settings with brightness and gauss."""
    config = load_config(file_path)
    brightness = config.get('brightness', {})
    gauss = config.get('gauss', {})  # also a typo: 'guass' → 'gauss'
    return {
        "picture_brightness":     brightness.get('brightness_list'),
        "brightness_combination": brightness.get('brightness_combination'),
        "gauss_strength":         gauss.get('gauss_list'),
        "gauss_combination":      gauss.get('gauss_combination'),
    }

def is_valid_json(path):
    try:
        with open(path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False


def load_setup_conf(file_path="config.yml"):
    '''loads config with url,api key,project id, output dir, only completed'''
   
    config = load_config(file_path)
    lo_section = config.get('local',{})
    ls_section = config.get('label_studio', {})
    dl_section = config.get('download', {})

    return {
        "local": lo_section.get('local',False),
        "json_path": lo_section.get('json_path'),
        "picture_path": lo_section.get('picture_path'),

        "url": ls_section.get('url'),
        "api_key": ls_section.get('api_key'),
        "project_id": ls_section.get('project_id'),
        "output_dir": dl_section.get('output_dir', 'downloads'),
        "only_completed": dl_section.get('only_completed', True)
    }
  



def connect_label_studio(base_url, api_key, project_id):
    '''Checks if it can connect to label studio'''
    if not base_url or not api_key or api_key == "YOUR_API_KEY":
         
        print(" Error: URL or API Key is missing in the config file.")
        return None
    try:
        client = LabelStudio(base_url=base_url, api_key=api_key)
        
        project = client.projects.get(id=project_id)
        print(f" Success! Connected to project: '{project.title}' (ID: {project_id})")
        return client

    except ApiError as e:
        print(f" Label Studio API Error (Status {e.status_code}): {e.body}")
    except Exception as e:
        print(f" Unexpected Connection Error: {e}")
    
    return None

def fetch_tasks(client, project_id, only_completed=True):
    """Fetch all tasks from the project, optionally filtering for completed ones only."""
    print(f"\n  Fetching tasks (only_completed={only_completed})...")
    try:
        all_tasks = []
        for task in client.tasks.list(project=project_id):
            if only_completed and not task.is_labeled:
                continue
            all_tasks.append(task)

        print(f"  Found {len(all_tasks)} task(s).")
        return all_tasks
    except ApiError as e:
        print(f"  API Error while fetching tasks (Status {e.status_code}): {e.body}")
        return []
    except Exception as e:
        print(f"  Unexpected error while fetching tasks: {e}")
        return []

def save_tasks(tasks, output_dir, project_id):
    """Save fetched tasks to a JSON file inside output_dir. reuterns path"""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    output_file = out_path / f"project_{project_id}_annotations.json"

    # Convert SDK objects to plain dicts
    serializable = []
    for task in tasks:
        if hasattr(task, "dict"):
            serializable.append(task.dict())
        elif hasattr(task, "__dict__"):
            serializable.append(vars(task))
        else:
            serializable.append(task)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, default=str)

    print(f"  Saved {len(serializable)} task(s) to '{output_file}'")
    return output_file

def download_images(tasks,api_key,url,output_dir)-> str:
    '''Downloads all the Images and returns their path'''
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    download,skipped = 0,0
    images_paths = []
    
    for task in tasks:
        image_path = task.data.get("image")
        if not image_path:
            continue
        
        filename = image_path.split("/")[-1].split("?d=")[-1].split("/")[-1]
        
        response = requests.get(
            f"{url}{image_path}",
            headers={"Authorization": f"Token {api_key}"}
        )
        if response.status_code == 200:
            save_path = out_path / filename
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Saved: {save_path}")
            download +=1
            images_paths.append(save_path)
        else:
            print(f"Error when Saving")
            skipped +=1
    print(f"downloaded: {download}, skipped: {skipped}")
    return images_paths


def get_local_picutrs(path):
    extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    images_paths= [p for p in Path(path).iterdir() if p.suffix.lower() in extensions]
    if not images_paths:
        print(f"no Imagesfound in folder {path}")
        sys.exit(0)
    return images_paths

def get_local_json(path):
    if is_valid_json(path):
        return path
    else:
        print(f"not a Valid Path to Json {path}")
        sys.exit(0)
        return None