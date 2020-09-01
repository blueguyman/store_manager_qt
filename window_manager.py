import traceback

import treelib

from windows import sg
import misc


def window_manager(windows: treelib.Tree):
    """
    USAGE:

        windows = treelib.Tree()
        windows.create_node("Root Window", "root", data=window_funcs.root_window)
        windows.create_node("Window 1", "window_1", parent="root", data=window_funcs.window_1)
        window_manager(windows)

    The data arguments for each node must be a function that returns a tuple.

        def root_window():
            event = sg.popup("ROOT!")
            if event is sg.WIN_CLOSED:
                return (sg.WIN_CLOSED,)
            return ("window_1", "arg1", "arg2")

    where "window_1" is the nid of a child of Node
    "root" and "arg1" and "arg2" are the arguments passed to the function in the data
    argument of "window_1".

        def window_1(*text):
            while True:
                event = sg.popup_ok_cancel(*text)

                if event is sg.WIN_CLOSED:
                    return (sg.WIN_CLOSED,)

                if event == "Cancel":
                    return ("BACK",)

    """
    # pylint: disable=protected-access

    try:
        sg.theme("SystemDefault")
        misc.fix_theme()
        current_window = windows.root
        args = []
        while True:
            # The identifier is a function object
            window_data = windows.get_node(current_window).identifier(*args)
            if window_data is None:
                break
            if not isinstance(window_data, (tuple, list)):
                window_data = (window_data,)

            try:
                args = window_data[1:]
            except IndexError:
                args = []

            if isinstance(window_data[0], str):
                if window_data[0].upper() == "EXIT":
                    break
                if window_data[0].upper() == "BACK":
                    if current_window == windows.root:
                        break
                    current_window = windows.parent(current_window).identifier
                    continue

            allowed_windows = [
                child.identifier for child in windows.children(current_window)
            ]
            if window_data[0] not in allowed_windows:
                raise LookupError(
                    f"Node '{window_data[0]}' is not a child of '{current_window}'"
                )

            current_window = windows.get_node(window_data[0]).identifier
    except Exception:
        sg.Popup(traceback.format_exc())

    cnx = misc.CACHE.get("cnx", None)
    if cnx is not None:
        cnx.close()
