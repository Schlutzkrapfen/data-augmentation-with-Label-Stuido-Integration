import yaml
from nicegui import ui
from downloader import load_setup_conf,load_picture_conf,load_config

def set_up_gui(on_start=None):
    setup_conf = load_setup_conf()
    i = ui.input(value=setup_conf['url']).props('clearable')
    d = ui.input(value=setup_conf['api_key'],password=True).props('clearable')
    ui.label().bind_text_from(i, 'value')
    def handle_start():
        conf = load_config()
        setup_conf['url'] = i.value
        save_setup_conf(conf)
        if on_start:
            on_start()
    ui.button("Start", on_click=handle_start)

def save_setup_conf(conf: dict, path: str = "config.yml"):
    try:
        with open(path, 'w') as f:
            yaml.dump(conf, f, default_flow_style=False)
        print("worked")
    except Exception as e:
        print(f"Save failed: {e}")