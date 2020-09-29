import random
import webbrowser
from decimal import Decimal

import mysql.connector
import PySimpleGUIQt as sg
import treelib

import demo_db
import misc
import mysql_funcs


_SIZE = (1024, 576)
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
        [sg.HSeperator()],
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
                    values["-HOST-"],
                    values["-USER-"],
                    values["-PASSWORD-"],
                )
                misc.log(window, "Access granted")
                misc.log(window, "Estabilishesort_by_columnMySQL Server")
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
        [sg.Text("Create New Database")],
        [sg.Input(do_not_clear=False, key="-NEW_DB-")],
        [sg.Check("Insert sample data (Demo Mode)", key="-DEMO_MODE-")],
        [sg.Button("Create")],
        [sg.HSeperator()],
        [sg.Text()],
        [
            sg.Text("Database"),
            sg.Combo(
                mysql_funcs.get_valid_dbs(),
                default_value=misc.load_data("database", category="mysql"),
                key="-DB-",
            ),
        ],
        [
            sg.Button(
                "Use",
            ),
            sg.Button("Delete"),
        ],
        [
            sg.Text(
                "Note: Only use databases created using this program",
                font=(None, 8),
                key="-DP_HINT-",
            ),
        ],
    ]

    layout = [
        [sg.HSeperator()],
        [sg.Column(title_column), sg.VSeperator(), sg.Column(db_column)],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(_TITLE, layout, size=_SIZE, finalize=True)
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
                if values["-DEMO_MODE-"]:
                    demo_db.fill_database(values["-NEW_DB-"])

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
        [sg.Text("MANAGER", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Text(key="-MANAGER-NAME")],
        [sg.Text()],
        [sg.Button("Manage Staff")],
        [sg.Button("View Expenses")],
        [sg.Text()],
        [sg.Button("Change Password")],
        [sg.Text()],
        [sg.Button("Logout")],
        [sg.Stretch()],
    ]

    cashier_column = [
        [sg.Text("CASHIER", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Text(key="-CASHIER-NAME")],
        [sg.Text("TODO")],
        [sg.Button("Logout")],
        [sg.Stretch()],
    ]

    cs_column = [
        [sg.Text("CUSTOMER SUPPORT", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Text(key="-CSUPPORT-NAME")],
        [sg.Text()],
        [sg.Button("Manage Tickets")],
        [sg.Text()],
        [sg.Button("Logout")],
        [sg.Stretch()],
    ]

    stocker_column = [
        [sg.Text("STOCKER", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Text(key="-STOCKER-NAME")],
        [sg.Text("TODO")],
        [sg.Button("Logout")],
        [sg.Stretch()],
    ]

    main_column = [
        [sg.Text("MAIN MENU", font=(None, 20, "underline"), justification="c")],
        [sg.Text("\nLogin to view more options\n", justification="c")],
        [sg.Button("Github")],
        [sg.Text()],
        [sg.Button("Feedback")],
        [sg.Stretch()],
    ]

    mode_columns = [
        sg.Column(manager_column, key="-MANAGER-COL", visible=False),
        sg.Column(cashier_column, key="-CASHIER-COL", visible=False),
        sg.Column(cs_column, key="-CSUPPORT-COL", visible=False),
        sg.Column(stocker_column, key="-STOCKER-COL", visible=False),
        sg.Column(main_column, key="-MAIN-COL"),
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
        [
            sg.Text(),
        ],
        [sg.Text("Login Mode")],
        [sg.Column(login_mode_column)],
        [sg.Button("Login", bind_return_key=True), sg.Exit()],
    ]

    layout = [
        [sg.Text(_TITLE.upper(), font=(None, 32, "underline"), justification="c")],
        [sg.HSeperator()],
        [sg.Text()],
        [
            sg.Column(login_column),
            sg.VSeperator(),
            *mode_columns,
        ],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(
        _TITLE, layout, size=_SIZE, use_default_focus=False, finalize=True
    )
    next_window = "EXIT"
    current_mode = "-MAIN-"
    if window["-NAME-"].get() != "":
        window["-PASSWORD-"].set_focus()

    while True:
        event, values = window.read()

        # LOGIN COLUMN

        if event in ("Exit", sg.WIN_CLOSED):
            break

        if event == "-MANAGER-":  # Click on Manager Radio Element
            if not values["-MANAGER-"]:
                # If Radio is selected
                window["-PASSWORD-"].update(disabled=True, background_color="grey")
                window["-DP_HINT-"].update(visible=False)
            else:
                window["-PASSWORD-"].update(disabled=False, background_color="white")
                window["-DP_HINT-"].update(visible=True)
                window["-PASSWORD-"].set_focus()

        # MAIN MENU

        if event == "Login":
            if values["-NAME-"] == "":
                misc.log(window, "Field 'Name' is empty")
                continue
            misc.save_data("name", values["-NAME-"])

            new_mode = misc.get_selected_radio(
                values, ["-MANAGER-", "-CASHIER-", "-CSUPPORT-", "-STOCKER-"]
            )

            if new_mode == "-MANAGER-":
                if not mysql_funcs.validate_password("manager", values["-PASSWORD-"]):
                    misc.log(window, f"Incorrect password for {new_mode[1:-1]}")
                    continue

            window[current_mode + "COL"].update(visible=False)
            if current_mode != "-MAIN-":
                misc.log(window, f"Logged out of {current_mode[1:-1]}")

            current_mode = new_mode
            misc.CACHE["name"] = values["-NAME-"].strip()
            misc.log(window, f"Logged into {new_mode[1:-1]} as {misc.CACHE['name']}")
            if current_mode != "-MAIN-":
                window[current_mode + "NAME"].update(f"Name: {misc.CACHE['name']}")

            window[current_mode + "COL"].update(visible=True)

        if event == "Github":
            webbrowser.open("https://github.com/blueguyman/store_manager_qt")

        if event == "Feedback":
            sg.popup(
                "Please send any feedback to midhun128@gmail.com", title="Feedback"
            )

        # MANAGER COLUMN

        if event == "Manage Staff":
            next_window = (manager, staff_management)
            break

        if event == "Change Password":
            new_pass = sg.popup_get_text(
                "New Password",
                "Change Password",
                password_char="*",
                size=(_SIZE[0] // 2, None),
            )
            if new_pass is not None:
                try:
                    mysql_funcs.set_password("manager", new_pass)
                    misc.log(window, "Password changed")
                    event = "Logout"  # Kinda hacky. Might want to change it
                except mysql.connector.Error as err:
                    misc.log(window, err)

        # CSUPPORT COLUMN

        if event == "Manage Tickets":
            next_window = (customer_support, manage_tickets)
            break

        # MODE COLUMNS

        if event.startswith("Logout"):
            window[current_mode + "COL"].update(visible=False)
            misc.log(window, f"Logged out of {current_mode[1:-1]}")
            current_mode = "-MAIN-"
            window[current_mode + "COL"].update(visible=True)

    misc.log(window)
    window.close()
    return next_window


# ****************************************
# Parent: main_menu
# ****************************************
def manager(child=None):
    # Decided to not make a separate window. Basically just here to stay organised
    return child if child else "BACK"


# ****************************************
# Parent: manager
# ****************************************
def staff_management():
    # TODO: staff_management

    staff_table_column = [
        [
            sg.Table(
                *mysql_funcs.get_table_data(
                    "staff", ("department", "asc"), ("emp_id", "asc")
                ),
                enable_events=True,
                key="-STAFF-",
            )
        ]
    ]

    staff_modify_column = [
        [sg.Text("Staff Management", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Button("Add New Staff")],
        [sg.Text()],
        [
            sg.Text(
                "Click on the row numbers on the left to modify values", font=(None, 8)
            ),
        ],
        [sg.Button("Edit Details", disabled=True)],
        [sg.Button("Remove Staff", disabled=True)],
        [sg.Text()],
        [sg.Button("Back")],
        [sg.Stretch()],
    ]

    layout = [
        [
            sg.Column(staff_table_column),
            sg.VSeperator(),
            sg.Column(staff_modify_column),
        ],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(_TITLE, layout, size=_SIZE)
    next_window = "EXIT"

    while True:
        event, values = window.read()

        if event is sg.WIN_CLOSED:
            break

        if event == "Back":
            next_window = "BACK"
            break

        if len(values["-STAFF-"]) > 0 and window["-STAFF-"].get()[0][0] != "":
            if len(values["-STAFF-"]) == 1:
                window["Edit Details"].update(disabled=False)
            else:
                window["Edit Details"].update(disabled=True)
            window["Remove Staff"].update(disabled=False)
        else:
            window["Edit Details"].update(disabled=True)
            window["Remove Staff"].update(disabled=True)

        if event == "Add New Staff":
            staff_data = new_staff()
            if staff_data is not None:
                cursor = mysql_funcs.new_cursor()
                try:
                    cursor.execute(
                        "INSERT INTO staff VALUES (%s, %s, %s, %s)", staff_data
                    )
                    misc.log(window, "Employee added to table")
                except mysql.connector.Error as err:
                    misc.log(window, err)
                cursor.close()
                mysql_funcs.commit()

        if event == "Edit Details":
            employee_data = window["-STAFF-"].get()[values["-STAFF-"][0]]
            modified_data = edit_staff(employee_data)
            if modified_data is not None:
                cursor = mysql_funcs.new_cursor()
                try:
                    cursor.execute(
                        "UPDATE staff SET emp_id=%s, name=%s, salary=%s, department=%s "
                        "WHERE emp_id=%s",
                        (*modified_data, employee_data[0]),
                    )
                    misc.log(window, "Employee modified")
                except mysql.connector.Error as err:
                    misc.log(window, err)
                cursor.close()
                mysql_funcs.commit()

        if event == "Remove Staff":
            ids_to_delete = [
                (int(window["-STAFF-"].get()[i][0]),) for i in values["-STAFF-"]
            ]
            cursor = mysql_funcs.new_cursor()
            try:
                cursor.executemany("DELETE FROM staff WHERE emp_id = %s", ids_to_delete)
                misc.log(window, f"Removed {len(ids_to_delete)} employee(s)")
            except mysql.connector.Error as err:
                misc.log(window, err)
            cursor.close()
            mysql_funcs.commit()

        updated_data = mysql_funcs.get_table_data(
            "staff", ("department", "asc"), ("emp_id", "asc")
        )[0]
        if updated_data != window["-STAFF-"].get():
            window["-STAFF-"].update(updated_data)

    misc.log(window)
    window.close()
    return next_window


# POPUP: Staff Manager
def new_staff():
    layout = [
        [
            sg.Text("Employee Id"),
            sg.Input(enable_events=True, key="-ID-"),
            sg.Button("Random"),
        ],
        [sg.Text("Employee Name"), sg.Input(key="-NAME-")],
        [sg.Text("Salary"), sg.Input(enable_events=True, key="-SALARY-")],
        [sg.Text("Department"), sg.Input(key="-DEPARTMENT-")],
        [sg.Button("Add", bind_return_key=True), sg.Cancel()],
    ]

    window = sg.Window("New Staff", layout)
    staff_data = None

    while True:
        event, values = window.read()

        if event in ("Cancel", sg.WIN_CLOSED):
            break

        if event == "Random":
            id_ = str(random.randint(1000, 9999))
            window["-ID-"].update(id_)

        if event == "Add" and values["-ID-"] != "" and values["-NAME-"] != "":
            id_ = values["-ID-"]
            name = values["-NAME-"]
            salary = values["-SALARY-"]
            if salary == "":
                salary = 0
            dept = values["-DEPARTMENT-"]
            staff_data = (id_, name, salary, dept)
            break

        if event == "Add" and values["-ID-"] == "":
            window["-ID-"].update(str(random.randint(1000, 9999)))

        # Filter Input
        if (
            event == "-ID-"
            and values["-ID-"]
            and values["-ID-"][-1] not in ("0123456789")
        ):
            window["-ID-"].update(values["-ID-"][:-1])

        if (
            event == "-SALARY-"
            and values["-SALARY-"]
            and values["-SALARY-"][-1] not in ("0123456789.")
        ):
            window["-SALARY-"].update(values["-SALARY-"][:-1])

    window.close()
    return staff_data


# POPUP: Staff Manager
def edit_staff(employee_data):
    layout = [
        [
            sg.Text("Employee Id"),
            sg.Input(employee_data[0], enable_events=True, key="-ID-"),
            sg.Button("Random"),
        ],
        [sg.Text("Employee Name"), sg.Input(employee_data[1], key="-NAME-")],
        [
            sg.Text("Salary"),
            sg.Input(employee_data[2], enable_events=True, key="-SALARY-"),
        ],
        [sg.Text("Department"), sg.Input(employee_data[3], key="-DEPARTMENT-")],
        [sg.Button("Change", bind_return_key=True), sg.Cancel()],
    ]

    window = sg.Window("Edit Staff", layout)
    modified_data = None

    while True:
        event, values = window.read()

        if event in ("Cancel", sg.WIN_CLOSED):
            break

        if event == "Random":
            id_ = str(random.randint(1000, 9999))
            window["-ID-"].update(id_)

        if event == "Change" and values["-ID-"] != "" and values["-NAME-"] != "":
            id_ = values["-ID-"]
            name = values["-NAME-"]
            salary = values["-SALARY-"]
            if salary == "":
                salary = 0
            dept = values["-DEPARTMENT-"]
            modified_data = (id_, name, salary, dept)
            break

        if event == "Change" and values["-ID-"] == "":
            window["-ID-"].update(str(random.randint(1000, 9999)))

        # Filter Input
        if (
            event == "-ID-"
            and values["-ID-"]
            and values["-ID-"][-1] not in ("0123456789")
        ):
            window["-ID-"].update(values["-ID-"][:-1])

        if (
            event == "-SALARY-"
            and values["-SALARY-"]
            and values["-SALARY-"][-1] not in ("0123456789.")
        ):
            window["-SALARY-"].update(values["-SALARY-"][:-1])

    window.close()
    return modified_data


# ****************************************
# Parent: manager
# ****************************************
def profit_and_loss():
    # TODO: profit_and_loss
    pass


# ****************************************
# Parent: main_menu
# ****************************************
def customer_support(child=None):
    return child if child else "BACK"


# ****************************************
# Parent: customer_support
# ****************************************
def manage_tickets():
    ticket_table_column = [
        [
            sg.Table(
                *mysql_funcs.get_table_data(
                    "ticket", ("status", "desc"), ("ticket_id", "asc")
                ),
                enable_events=True,
                key="-TICKET-",
            )
        ]
    ]

    ticket_modify_column = [
        [sg.Text("Customer Support", font=(None, 20, "underline"), justification="c")],
        [sg.Text()],
        [sg.Button("Create New Ticket")],
        [sg.Text()],
        [
            sg.Text(
                "Click on the row numbers on the left to modify values", font=(None, 8)
            ),
        ],
        [sg.Button("Manage Ticket", disabled=True)],
        [sg.Button("Delete Tickets", disabled=True)],
        [sg.Text()],
        [sg.Button("Back")],
        [sg.Stretch()],
    ]

    layout = [
        [
            sg.Column(ticket_table_column),
            sg.VSeperator(),
            sg.Column(ticket_modify_column),
        ],
        [sg.Text()],
        [sg.HSeperator()],
        misc.layout_bottom(),
    ]

    window = sg.Window(
        _TITLE, layout, size=_SIZE, use_default_focus=False, finalize=True
    )
    next_window = "EXIT"

    while True:
        event, values = window.read()

        if event is sg.WIN_CLOSED:
            break

        if event == "Back":
            next_window = "BACK"
            break

        if len(values["-TICKET-"]) > 0 and window["-TICKET-"].get()[0][0] != "":
            if len(values["-TICKET-"]) == 1:
                window["Manage Ticket"].update(disabled=False)
            else:
                window["Manage Ticket"].update(disabled=True)
            window["Delete Tickets"].update(disabled=False)
        else:
            window["Manage Ticket"].update(disabled=True)
            window["Delete Tickets"].update(disabled=True)

        if event == "Create New Ticket":
            ticket_data = new_ticket()
            if ticket_data is not None:
                cursor = mysql_funcs.new_cursor()
                try:
                    cursor.execute(
                        "INSERT INTO ticket VALUES (%s, %s, %s, %s, %s)", ticket_data
                    )
                    misc.log(window, "Ticket Created")
                except mysql.connector.Error as err:
                    misc.log(window, err)
                cursor.close()
                mysql_funcs.commit()

        if event == "Manage Ticket":
            ticket_data = window["-TICKET-"].get()[values["-TICKET-"][0]]
            new_status = edit_ticket(ticket_data)
            if new_status is not None:
                cursor = mysql_funcs.new_cursor()
                try:
                    cursor.execute(
                        "UPDATE ticket SET status=%s WHERE ticket_id=%s",
                        (new_status, ticket_data[0]),
                    )
                    misc.log(window, "Status Updated")
                except mysql.connector.Error as err:
                    misc.log(window, err)
                cursor.close()
                mysql_funcs.commit()

        if event == "Delete Tickets":
            ids_to_delete = [
                (int(window["-TICKET-"].get()[i][0]),) for i in values["-TICKET-"]
            ]
            cursor = mysql_funcs.new_cursor()
            try:
                cursor.executemany(
                    "DELETE FROM ticket WHERE ticket_id = %s", ids_to_delete
                )
                misc.log(window, f"Removed {len(ids_to_delete)} ticket(s)")
            except mysql.connector.Error as err:
                misc.log(window, err)
            cursor.close()
            mysql_funcs.commit()

        updated_data = mysql_funcs.get_table_data(
            "ticket", ("status", "desc"), ("ticket_id", "asc")
        )[0]
        if updated_data != window["-TICKET-"].get():
            window["-TICKET-"].update(updated_data)

    misc.log(window)
    window.close()
    return next_window


def new_ticket():
    layout = [
        [
            sg.Text("Ticket Number"),
            sg.Input(enable_events=True, key="-ID-"),
            sg.Button("Random"),
        ],
        [sg.Text("Author"), sg.Input(key="-AUTHOR-")],
        [sg.Text("E-mail ID"), sg.Input(key="-EMAIL-")],
        [sg.Text("Message")],
        [sg.Multiline(key="-MESSAGE-")],
        [sg.Button("Create", bind_return_key=True), sg.Cancel()],
    ]

    window = sg.Window("New Ticket", layout)
    ticket_data = None

    while True:
        event, values = window.read()

        if event in ("Cancel", sg.WIN_CLOSED):
            break

        if event == "Random":
            id_ = str(random.randint(1000, 9999))
            window["-ID-"].update(id_)

        if event == "Create" and values["-ID-"] != "" and values["-AUTHOR-"] != "":
            id_ = values["-ID-"]
            author = values["-AUTHOR-"]
            email = values["-EMAIL-"]
            message = values["-MESSAGE-"]
            ticket_data = (id_, author, email, message, "unresolved")
            break

        if event == "Create" and values["-ID-"] == "":
            window["-ID-"].update(str(random.randint(1000, 9999)))

        # Filter Input
        if (
            event == "-ID-"
            and values["-ID-"]
            and values["-ID-"][-1] not in ("0123456789")
        ):
            window["-ID-"].update(values["-ID-"][:-1])

    window.close()
    return ticket_data


def edit_ticket(ticket_data):
    layout = [
        [sg.Text(f"Ticket ID: {ticket_data[0]}")],
        [sg.Text(f"Author: {ticket_data[1]}")],
        [sg.Text(f"Email: {ticket_data[2]}")],
        [sg.Text("Message:")],
        [sg.MultilineOutput(ticket_data[3])],
        [
            sg.Text("Status:"),
            sg.Radio("Unresolved", "status", key="unresolved"),
            sg.Radio("Resolved", "status", key="resolved"),
        ],
        [sg.Button("Save", bind_return_key=True), sg.Cancel()],
    ]

    window = sg.Window(f"Ticket #{ticket_data[0]}", layout, finalize=True)
    new_status = None

    window[ticket_data[-1]].update(True)

    while True:
        event, values = window.read()

        if event in ("Cancel", sg.WIN_CLOSED):
            break

        if event == "Save":
            new_status = misc.get_selected_radio(values, ["unresolved", "resolved"])
            break

    window.close()
    return new_status


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
