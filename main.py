import os
import sys
from nicegui import ui
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from downloader import load_conf,connect_label_studio,fetch_tasks,save_tasks,download_images,load_picture_conf
from converter import  adjust_brightness,add_guasianfilter
from gui import set_up_gui
def main():

    set_up_gui()
    ui.run()
    conf = load_conf()
    
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
    conf = load_picture_conf()
    brightness_list = conf["picture_brightness"]
    brightness_combination = conf["brightness_combination"]
    changed_list = []
    for brightness in brightness_list:
        changed_list += adjust_brightness(images_paths,json_path,float(brightness))
    for strength in conf["guass_strength"]:
        add_guasianfilter(images_paths,json_path,strength)
    if brightness_combination and conf["guass_combination"]:
        for strength in conf["guass_strength"]:
            add_guasianfilter(changed_list,json_path,strength)


if __name__ == "__main__":
    main()
