import json

import PySimpleGUIQt as sg


CACHE = {"log": "STORE MANAGER\n\n"}


def save_data(key, value, category="misc"):
    file = "./data.json"
    try:
        with open(file) as fp:
            data = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    category_dict = data.get(category, None)
    if category_dict is None:
        category_dict = {}
    category_dict[key] = value
    data[category] = category_dict

    with open(file, "w") as fp:
        json.dump(data, fp)


def load_data(key, default=None, category="misc"):
    try:
        with open("data.json") as fp:
            data = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    category_dict = data.get(category, None)
    if category_dict is None:
        category_dict = {}

    return category_dict.get(key, default)


def layout_bottom():

    log_tab = [
        [
            sg.MultilineOutput(
                CACHE["log"],
                autoscroll=True,
                text_color="green",
                background_color="black",
                key="-LOG-",
            )
        ],
    ]

    bottom = [
        sg.TabGroup(
            [
                [sg.Tab("Log", log_tab, background_color="light grey")],
            ]
        )
    ]

    return bottom


def log(window, *values, sep=" ", end="\n"):
    CACHE["log"] += sep.join([str(value) for value in values]) + end

    if window is not None:
        window["-LOG-"].update(CACHE["log"])
        window.refresh()


def get_selected_radio(values, key_list):
    for key in key_list:
        if values[key]:
            return key
    return None


def fix_theme():
    sg.theme_button_color((None, None))
