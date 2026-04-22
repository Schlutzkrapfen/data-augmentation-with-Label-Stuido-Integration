import os 
import json

from PIL import Image, ImageEnhance

def add_labels(path_to_labels,id,file_name):
    copied_result = get_picture_label(path_to_labels,id)
    changed_result =change_labels(copied_result,file_name)
    with open(path_to_labels, 'r') as f:
        data = json.load(f)
        data.append(changed_result)
    with open(path_to_labels, 'w') as f:
        json.dump(data, f, indent=4)
        print("added the json to the file")

def get_picture_label(path_to_labels,id):
    with open(path_to_labels, "r") as f:
        data = json.load(f)
    return data[id]

def change_labels(data,filepath):
    old_path =  data["data"]["image"]
    old_dir = os.path.dirname(old_path)
    file    = os.path.join(old_dir, os.path.basename(filepath))
    data["data"]["image"] =file
    return data

def adjust_brightness(image_paths,path_to_label ,brightness_factor=1.5):
    '''Adjust the brightness of the picutre and saves it as {picutrename}-btightness.png'''
    for  i, filepath in enumerate(image_paths):
        try:
            with Image.open(filepath) as img:
                enhancer = ImageEnhance.Brightness(img)
                brightened = enhancer.enhance(brightness_factor)
                name, ext = os.path.splitext(filepath)
                filepath = f"{name}-brightness{ext}"
                add_labels(path_to_label,i,filepath) 
                brightened.save(filepath)
                print(f"  Brightness adjusted: {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"Skipping {os.path.basename(filepath)}: {e}")
        
