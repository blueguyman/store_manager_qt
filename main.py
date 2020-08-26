from window_manager import window_manager
from windows import generate_window_tree


def main():

    windows = generate_window_tree()
    window_manager(windows)


if __name__ == "__main__":
    main()
