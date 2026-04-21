import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from downloader import load_conf,connect_label_studio,fetch_tasks,save_tasks,download_images
def main():
    conf = load_conf()
    
    client = connect_label_studio(
        conf['url'], 
        conf['api_key'], 
        conf['project_id']
    )
    tasks = fetch_tasks(client, conf['project_id'], conf['only_completed'])

    if not tasks:
        print("  No tasks to save. Exiting.")
        sys.exit(0)
    save_tasks(tasks, conf['output_dir'], conf['project_id'])
    download_images(tasks,conf['api_key'],conf['url'],conf['output_dir'])
    print("\n  Download complete.")

if __name__ == "__main__":
    main()