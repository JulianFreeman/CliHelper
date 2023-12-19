# coding: utf8
from clihelper import CliHelper, request_input


def open_file():
    print("File Opened")


def new_folder(name):
    print(f"Folder [{name}] created")


def test_helper():
    ch = CliHelper({"right_padding": 20, "serial_marker": "->"})
    # ch = CliHelper()
    n = ch.add_option("New")
    n.add_return_option()
    n.add_option("New File")
    n.add_option("New Folder", new_folder, ("Temp", ))
    n.add_exit_option()

    ch.add_option("Open File", open_file)
    ch.add_option("Save")
    ch.add_exit_option()

    ch.start_loop()
    # n.start_loop()


def test_req():
    v = request_input("\nEnter a number", check_func=lambda x: x.isdigit() and 1 < int(x) < 10, ask_again=False,
                      has_default_val=True, default_val="4",
                      need_confirm=True)
    print(v)


if __name__ == '__main__':
    # test_req()
    test_helper()
