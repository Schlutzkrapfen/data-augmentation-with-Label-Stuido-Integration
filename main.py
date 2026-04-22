import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from downloader import load_conf,connect_label_studio,fetch_tasks,save_tasks,download_images
from converter import  adjust_brightness, add_labels
def main():
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
    adjust_brightness(images_paths,json_path,0.5)

if __name__ == "__main__":
    main()