import os 
import json
from PIL import Image, ImageEnhance,ImageFilter

def add_labels(path_to_labels,id,file_name):
    copied_result = get_picture_label(path_to_labels,id)
    changed_result =change_labels(copied_result,file_name)
    with open(path_to_labels, 'r') as f:
        data = json.load(f)
        data.append(changed_result)
    with open(path_to_labels, 'w') as f:
        json.dump(data, f, indent=4)
        print("   added the json to the file")

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
    saved_paths = []
    for  i, filepath in enumerate(image_paths):
        try:
            with Image.open(filepath) as img:
                enhancer = ImageEnhance.Brightness(img)
                brightened = enhancer.enhance(brightness_factor)
                name, ext = os.path.splitext(filepath)
                filepath = f"{name}-brit-{brightness_factor}{ext}"
                brightened.save(filepath)
                saved_paths.append(filepath)
                print(f"  Brightness adjusted: {os.path.basename(filepath)}")
                add_labels(path_to_label,i,filepath) 
        except Exception as e:
            print(f"Skipping {os.path.basename(filepath)}: {e}")
        
    return saved_paths

def add_guasianfilter(image_paths,path_to_label,guas_strength=1 ):
    saved_paths = []
    for  i, filepath in enumerate(image_paths):
        try:
            name, ext = os.path.splitext(filepath)
            new_filepath = f"{name}-gaus-{guas_strength}{ext}"
            with Image.open(filepath) as img:
                result = img.filter(ImageFilter.GaussianBlur(radius=guas_strength))
                result.save(new_filepath)
                saved_paths.append(new_filepath)
                print(f"  Gausfilter Added: {os.path.basename(new_filepath)}")
                add_labels(path_to_label,i,new_filepath) 
        except Exception as e:
            print(f"Skipping {os.path.basename(filepath)}: {e}")
    return saved_paths