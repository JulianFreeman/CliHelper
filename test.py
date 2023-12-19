# coding: utf8
from clihelper import CliHelper, request_input


def open_file():
    print("File Opened")


def new_folder(name):
    print(f"Folder [{name}] created")


def test_helper():
    c = CliHelper(right_padding=20, draw_menu_again=False)
    n = c.add_option(title="New")
    c.add_option(title="Open File", exec_func=open_file)
    c.add_option(title="Save")
    c.add_exit_option()

    c.add_return_option(n)
    c.add_option(n, "New File")
    c.add_option(n, "New Folder", new_folder, ("Temp",))
    c.add_exit_option(n)

    c.start_loop()


def test_req():
    v = request_input("\nEnter a number", check_func=lambda x: x.isdigit() and 1 < int(x) < 10, ask_again=False,
                      has_default_val=True, default_val="4",
                      need_confirm=True)
    print(v)


if __name__ == '__main__':
    # test_req()
    test_helper()
