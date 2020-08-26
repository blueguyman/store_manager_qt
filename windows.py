import mysql.connector
import PySimpleGUIQt as sg
import treelib

import misc
import mysql_funcs


_SIZE = (992, 558)
_TITLE = "Store Manager"


def generate_window_tree():
    windows = treelib.Tree()
    windows.create_node("CNX Setup", cnx_setup, None)  # ROOT NODE
    windows.create_node("Database Setup", db_setup, cnx_setup)
    windows.create_node("Main Menu", main_menu, db_setup)

    # Manager subtree
    windows.create_node("Manager", manager, main_menu)
    windows.create_node("Staff Management", staff_management, manager)
    windows.create_node("Profit and Loss", profit_and_loss, manager)

    # Customer Support subtree
    windows.create_node("Customer Support", customer_support, main_menu)
    windows.create_node("New Ticket", new_ticket, customer_support)
    windows.create_node("Manage Tickets", manage_tickets, customer_support)

    # Cashier subtree
    windows.create_node("Cashier", cashier, main_menu)
    windows.create_node("Start Transaction", start_transaction, cashier)
    windows.create_node("Checkout", checkout, start_transaction)

    # Stocker subtree
    windows.create_node("Stocker", stocker, main_menu)
    windows.create_node("Inventory Management", inventory_management, stocker)

    return windows


# ****************************************
# Parent: None                           *
# ****************************************
def cnx_setup():

    title_column = [
        [sg.Stretch(), sg.Text("STORE", font=(None, 32), justification="r")],
        [sg.Text("MANAGER", font=(None, 32), justification="r")],
        [sg.Text("Fahad Mohammed Sajid", justification="r")],
        [sg.Text("Midhun Pradeep", justification="r")],
        [sg.Text("Najeeb Saiyed", justification="r")],
    ]

    login_column = [
        [sg.Text("MySQL", font=(None, 20), justification="c")],
        [sg.Text()],
        [
            sg.Text("Host"),
            sg.Input(misc.load_data("host", "localhost", "mysql"), key="-HOST-"),
        ],
        [
            sg.Text("Username"),
            sg.Input(misc.load_data("user", "root", "mysql"), key="-USER-"),
        ],
        [
            sg.Text("Password"),
            sg.Input(
                password_char="*", do_not_clear=False, key="-PASSWORD-", focus=True
            ),
        ],
        [sg.Text()],
        [sg.Button("Login", bind_return_key=True), sg.Exit()],
    ]

    layout = [
        [sg.Column(title_column), sg.VSeperator(), sg.Column(login_column)],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(_TITLE, layout, size=_SIZE, use_default_focus=False)
    next_window = "EXIT"

    while True:
        event, values = window.read()

        if event in ("Exit", sg.WIN_CLOSED):
            break

        if event == "Login":
            try:
                mysql_funcs.connect_to_mysql(
                    values["-HOST-"], values["-USER-"], values["-PASSWORD-"],
                )
                misc.log(window, "Access granted")
                misc.log(window, "Estabilished connection to MySQL Server")
                next_window = db_setup
                break
            except mysql.connector.Error as err:
                misc.log(window, err)

    misc.log(window)
    window.close()
    return next_window


# ****************************************
# Parent: cnx_setup                      *
# ****************************************
def db_setup():
    title_column = [
        [sg.Stretch(), sg.Text("STORE", font=(None, 32), justification="r")],
        [sg.Text("MANAGER", font=(None, 32), justification="r")],
        [sg.Text("MES Indian School", justification="r")],
        [sg.Text("12-C", justification="r")],
    ]

    db_column = [
        [sg.Text("Database", font=(None, 20), justification="c")],
        [sg.Text()],
        [
            sg.Text("Database"),
            sg.Combo(
                mysql_funcs.get_valid_dbs(),
                default_value=misc.load_data("database", category="mysql"),
                key="-DB-",
            ),
        ],
        [sg.Button("Use",), sg.Button("Delete")],
        [sg.HSeperator()],
        [sg.Text("\nCreate New Database")],
        [sg.Input(do_not_clear=False, key="-NEW_DB-")],
        [sg.Button("Create")],
    ]

    layout = [
        [sg.HSeperator()],
        [sg.Column(title_column), sg.VSeperator(), sg.Column(db_column)],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(
        _TITLE, layout, size=_SIZE, use_default_focus=False, finalize=True
    )
    next_window = "EXIT"

    while True:
        valid_dbs = mysql_funcs.get_valid_dbs()
        if valid_dbs == [""]:
            # Default value for convenience
            window["-NEW_DB-"].update("store_manager")
        window["-DB-"].update(values=valid_dbs)
        window["-DB-"].update(
            misc.load_data("database", category="mysql")
        )  # Display last used db by default

        event, values = window.read()

        if event is sg.WIN_CLOSED:
            break

        try:
            if event == "Use" and values["-DB-"] in valid_dbs:
                cursor = mysql_funcs.new_cursor()
                cursor.execute(f"USE {values['-DB-']}")
                cursor.close()
                misc.log(window, f"Using database {values['-DB-']}")
                misc.save_data("database", values["-DB-"], "mysql")
                next_window = main_menu
                break

            if event == "Delete" and values["-DB-"] in valid_dbs:
                cursor = mysql_funcs.new_cursor()

                cursor.execute(f"DROP DATABASE {values['-DB-']}")
                misc.log(window, f"Dropped database {values['-DB-']}")

                mysql_funcs.commit()
                cursor.close()

            if event == "Create" and values["-NEW_DB-"] != "":
                if mysql_funcs.create_new_db(values["-NEW_DB-"], window):
                    misc.log(window, f"Created database {values['-NEW_DB-']}")

        except mysql.connector.Error as err:
            misc.log(window, err)

    misc.log(window)
    window.close()
    return next_window


# ****************************************
# Parent: db_setup                       *
# ****************************************
def main_menu():
    # TODO: main_menu

    manager_column = [
        [sg.Text("MANAGER", justification="c")],
        [sg.Stretch()],
    ]

    cashier_column = [
        [sg.Text("TODO: CASHIER")],
        [sg.Stretch()],
    ]

    cs_column = [
        [sg.Text("TODO: CSUPPORT")],
        [sg.Stretch()],
    ]

    stocker_column = [
        [sg.Text("TODO: STOCKER")],
        [sg.Stretch()],
    ]

    empty_column = [
        [sg.Text("Please Login to view available options")],
        [sg.Stretch()],
    ]

    mode_columns = [
        sg.Column(manager_column, key="-MANAGER-COL", visible=False),
        sg.Column(cashier_column, key="-CASHIER-COL", visible=False),
        sg.Column(cs_column, key="-CSUPPORT-COL", visible=False),
        sg.Column(stocker_column, key="-STOCKER-COL", visible=False),
        sg.Column(empty_column, key="-EMPTY-COL"),
    ]

    login_mode_column = [
        [
            sg.Radio(
                "Manager", "[MODE]", default=True, key="-MANAGER-", enable_events=True
            ),
            sg.Input(password_char="*", do_not_clear=False, key="-PASSWORD-"),
        ],
        [
            sg.Text(
                "Note: Default password is '0000'",
                font=(None, 8),
                justification="r",
                key="-DP_HINT-",
            ),
        ],
        [sg.Radio("Cashier", "[MODE]", key="-CASHIER-")],
        [sg.Radio("Customer Support", "[MODE]", key="-CSUPPORT-")],
        [sg.Radio("Stocker", "[MODE]", key="-STOCKER-")],
    ]

    login_column = [
        [
            sg.Text("Name:"),
            sg.Input(misc.load_data("name", ""), focus=True, key="-NAME-"),
        ],
        [sg.Text(),],
        [sg.Text("Login Mode")],
        [sg.Column(login_mode_column)],
        [sg.Button("Login", bind_return_key=True), sg.Exit()],
    ]

    layout = [
        [sg.Text(_TITLE.upper(), font=(None, 32, "underline"), justification="c")],
        [sg.HSeperator()],
        [sg.Text()],
        [sg.Column(login_column), sg.VSeperator(), *mode_columns,],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(_TITLE, layout, size=_SIZE, use_default_focus=False)
    next_window = "EXIT"
    current_mode = "-EMPTY-"

    while True:
        event, values = window.read()

        if event in ("Exit", sg.WIN_CLOSED):
            break

        if event == "-MANAGER-":
            if not values["-MANAGER-"]:
                window["-PASSWORD-"].update(disabled=True, background_color="grey")
                window["-DP_HINT-"].update(visible=False)
            else:
                window["-PASSWORD-"].update(disabled=False, background_color="white")
                window["-DP_HINT-"].update(visible=True)

        if event == "Login":
            if values["-NAME-"] == "":
                misc.log(window, "Field 'Name' is empty")
                continue
            misc.save_data("name", values["-NAME-"])

            new_mode = misc.get_selected_radio(
                values, ["-MANAGER-", "-CASHIER-", "-CSUPPORT-", "-STOCKER-"]
            )

            if new_mode == "-MANAGER-":
                if not mysql_funcs.validate_password(0, values["-PASSWORD-"]):
                    misc.log(window, f"Incorrect password for {new_mode[1:-1]}")
                    continue

            window[current_mode + "COL"].update(visible=False)

            current_mode = new_mode
            misc.CACHE["name"] = values["-NAME-"]
            misc.log(window, f"Logged into {new_mode[1:-1]} as {misc.CACHE['name']}")

            window[current_mode + "COL"].update(visible=True)

    misc.log(window)
    window.close()
    return next_window


# ****************************************
# Parent: main_menu
# ****************************************
def manager():
    # TODO: manager
    pass


# ****************************************
# Parent: manager
# ****************************************
def staff_management():
    # TODO: staff_management
    pass


# ****************************************
# Parent: manager
# ****************************************
def profit_and_loss():
    # TODO: profit_and_loss
    pass


# ****************************************
# Parent: main_menu
# ****************************************
def customer_support():
    # TODO: customer_support
    pass


# ****************************************
# Parent: customer_support
# ****************************************
def new_ticket():
    # TODO: new_ticket
    pass


# ****************************************
# Parent: customer_support
# ****************************************
def manage_tickets():
    # TODO: manage_tickets
    pass


# ****************************************
# Parent: main_menu
# ****************************************
def cashier():
    # TODO: cashier
    pass


# ****************************************
# Parent: cashier
# ****************************************
def start_transaction():
    # TODO: start_transaction
    pass


# ****************************************
# Parent: start_transaction
# ****************************************
def checkout():
    # TODO: checkout
    pass


# ****************************************
# Parent: main_menu
# ****************************************
def stocker():
    # TODO: stocker
    pass


# ****************************************
# Parent: stocker
# ****************************************
def inventory_management():
    # TODO: inventory_management
    pass
