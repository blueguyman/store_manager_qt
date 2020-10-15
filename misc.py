import json

import PySimpleGUIQt as sg

import mysql_funcs


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


# FAHAD: CASHIER

_cartItems = [["", "", "", "", ""]]


def add_to_cart(cartData, newItem=None):
    if newItem is not None:
        itemExists = False
        for i in range(len(cartData)):
            if cartData[i][0] == newItem[0]:
                curQty = cartData[i][2]
                cartData[i][2] = str(int(curQty) + int(newItem[2]))
                cartData[i][4] = str(int(cartData[i][2]) * float(cartData[i][3]))
                itemExists = True
        if not itemExists:
            cartData.append(newItem)
        return cartData


def browse_products():
    _productsList = mysql_funcs.get_table_data("products")[0]
    tableData = []
    if not _productsList:
        tableData = [["", "", "", "", ""]]
    else:
        for product in _productsList:
            tableData.append(
                [
                    str(product[0]),
                    product[1],
                    product[4],
                    str(product[2]),
                ]
            )

    layout = [
        [sg.Text("Search"), sg.InputText(key="keyword", enable_events=True)],
        [
            sg.Table(
                values=tableData,
                headings=["ID", "Name", "Qty", "Price"],
                enable_events=True,
                select_mode=sg.TABLE_SELECT_MODE_NONE,
                key="prodTable",
            )
        ],
        [
            sg.Column(
                [[sg.Button("Select", size=(10, 1)), sg.Button("Close", size=(10, 1))]],
                element_justification="right",
            )
        ],
    ]

    return sg.Window("Browse", layout, size=(400, 400), use_default_focus=False)


def clear_fields(window):
    window["item_id"].Update("")
    window["item_name"].Update("")
    window["item_qty"].Update("")
    window["price"].Update("")
