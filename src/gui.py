from nicegui import ui
def set_up_gui():
    i = ui.input(value='some text').props('clearable')
    ui.label().bind_text_from(i, 'value')