import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from nicegui import ui
from downloader import load_setup_conf,connect_label_studio,fetch_tasks,save_tasks,download_images,load_picture_conf,get_local_json,get_local_picutrs
from ImageTransformer import  ImageTransformer
from gui import set_up_connection


def run_pipeline():
    conf = load_setup_conf()
    
    if not conf['local']:
        client = connect_label_studio(
            conf['url'], 
            conf['api_key'], 
            conf['project_id']
        )
        tasks = fetch_tasks(client, conf['project_id'], conf['only_completed'])

        if not tasks:
            print("No tasks to save. Exiting.")
            sys.exit(0)
        json_path = save_tasks(tasks, conf['output_dir'], conf['project_id'])
        images_paths= download_images(tasks,conf['api_key'],conf['url'],conf['output_dir'])
        print("\nDownload complete.")
    else:
        json_path = get_local_json(conf['json_path'])
        images_paths = get_local_picutrs(conf['picture_path'])
    conf = load_picture_conf()
        
    brightness_list = conf["picture_brightness"]
    brightness_combination = conf["brightness_combination"]
    changed_list = []
    transformer = ImageTransformer(images_paths,json_path,conf['json_output_path'])
    for brightness in brightness_list:
        changed_list +=  transformer.adjust_brightness(float(brightness))
    if conf["mirrored"]:
        transformer.mirror()
    for strength in conf["gauss_strength"]:
        transformer.add_gaussian_filter(strength)
    if brightness_combination and conf["gauss_combination"]:
        for strength in conf["gauss_strength"]:
            transformer.add_gaussian_filter(strength)
    #if brightness_combination and conf['']:
    #    pass

    

def main():
   set_up_connection(on_start=run_pipeline)  
   ui.run()
if __name__ in {"__main__", "__mp_main__"}:
    run_pipeline()
    #main()
