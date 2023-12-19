# coding: utf8

#######################################################
#   _____ _      _____ _    _      _                  #
#  / ____| |    |_   _| |  | |    | |                 #
# | |    | |      | | | |__| | ___| |_ __   ___ _ __  #
# | |    | |      | | |  __  |/ _ \ | '_ \ / _ \ '__| #
# | |____| |____ _| |_| |  | |  __/ | |_) |  __/ |    #
#  \_____|______|_____|_|  |_|\___|_| .__/ \___|_|    #
#                                   | |               #
#                                   |_|               #
#######################################################

from __future__ import annotations
from typing import Callable, TypedDict

version = (2, 0, 20231219)


def request_input(prompt_msg: str,
                  err_msg: str = "Invalid value.",
                  *,
                  has_default_val: bool = False,
                  default_val: str = "",
                  has_quit_val: bool = True,
                  quit_val: str = "q",
                  check_func: Callable[[str], bool] = None,
                  ask_again: bool = True,
                  need_confirm: bool = False) -> tuple[str, bool]:
    """
    请求用户输入

    :param prompt_msg: 向用户展示的提示信息（不需要加冒号）
    :param err_msg: 当用户输入不符合要求时展示的错误信息
    :param has_default_val: 当前请求是否有默认值
    :param default_val: 当用户没有输入内容时使用的默认值，若当前请求设定为无默认值，则此参数无效
    :param has_quit_val: 当前请求是否有退出值
    :param quit_val: 用户可以输入此值直接退出请求，若当前请求设定为无退出值，则此参数无效
    :param check_func: 用于检查用户输入的值是否符合要求的函数，若为 None 则不进行检查
    :param ask_again: 当用户输入的值不符合要求时是否再次请求输入
    :param need_confirm: 当用户输入后是否请求确认
    :return: 用户输入值和一个布尔值组成的元组，后者标记是否成功获取请求（非退出或者不符合要求）
    """
    while True:
        print(prompt_msg, end="")
        # 检查默认值
        if has_default_val:
            print(f" (Default [{default_val}]): ", end="")
            input_val = input() or default_val
        else:
            input_val = input(": ")
        # 检查退出值
        if has_quit_val and input_val == quit_val:
            print("Quit.")
            return "", False
        # 确认环节
        if need_confirm:
            # 这里是一个递归调用，所以 need_confirm 不能是 True，否则就会没玩没了地确认了
            result, state = request_input(
                f"Do you confirm the value [{input_val}] (yes/no)",
                has_default_val=False, has_quit_val=False,
                ask_again=True, need_confirm=False,
                check_func=lambda x: x.lower() in ("y", "yes", "n", "no")
            )
            # 确认没通过，重新开始
            if result in ("n", "no"):
                continue

        # 如果有检查函数，且当前输入不符合要求
        if check_func is not None and not check_func(input_val):
            print(err_msg, end=" ")
            if ask_again:
                print("Please enter again.")
                continue
            else:
                print()
                return "", False

        return input_val, True


class MenuConfig(TypedDict, total=False):
    left_padding: int
    right_padding: int
    top_padding: int
    bottom_padding: int
    edge_char: str
    wall_char: str
    serial_marker: str
    draw_menu_again: bool


DEFAULT_MENU_CONFIG: MenuConfig = {
    "left_padding": 2,
    "right_padding": 10,
    "top_padding": 1,
    "bottom_padding": 1,
    "edge_char": "#",
    "wall_char": " ",
    "serial_marker": ". ",
    "draw_menu_again": False,
}


class _OptionNode(object):
    """选项节点"""

    # 返回上级菜单的执行函数的返回值
    _RETURN_CODE = 0xbabe
    # 进入下级菜单的执行函数的返回值
    _ENTER_CODE = 0xbeef
    # 退出整个工具的返回值
    _QUIT_CODE = 0xcafe

    def __init__(self,
                 title: str = "Untitled Option",
                 exec_func: Callable = None,
                 args: tuple = None,
                 kwargs: dict = None,
                 menu_config: MenuConfig = None,
                 _is_root: bool = False):
        """
        :param title: 选项标题
        :param exec_func: 选择该选项后要执行的函数；对于用户设定的节点，该执行函数必须返回 None
        :param args: 执行函数的位置参数
        :param kwargs: 执行函数的命名参数
        :param menu_config: 绘制子选项菜单的参数；只在根选项设置，子选项继承
        :param _is_root: 标记当前节点是否是根节点；内部使用
        """
        self.title = title
        self.exec_func = exec_func if exec_func is not None else self._default_func
        self.args = args if args is not None else ()
        self.kwargs = kwargs if kwargs is not None else {}
        self.menu_config = menu_config if menu_config is not None else DEFAULT_MENU_CONFIG
        self.children = []  # type: list[_OptionNode]
        self._is_root = _is_root

    @staticmethod
    def _default_func():
        """用户没有指定执行函数时执行的默认函数"""
        print("No function")

    def _get_max_length_of_option_titles(self) -> int:
        """
        获取菜单选项中最长的选项标题的长度

        :return: 菜单选项中最长的选项标题的长度
        """
        return max([len(c.title) for c in self.children])

    def _draw_menu(self):
        """
        绘制菜单选项

        :return: None
        """
        left = self.menu_config["left_padding"]
        right = self.menu_config["right_padding"]
        top = self.menu_config["top_padding"]
        bottom = self.menu_config["bottom_padding"]
        ec = self.menu_config["edge_char"]
        wc = self.menu_config["wall_char"]
        sm = self.menu_config["serial_marker"]

        max_len_option = self._get_max_length_of_option_titles()
        # 获取最大选项序号的位数
        max_len_serial = len(str(len(self.children)))
        # 一个选项的总宽度
        option_width = max_len_serial + len(sm) + max_len_option
        # 菜单的宽度（加上左右两边的空白，但不包括边界）
        menu_width = left + option_width + right
        # 上下边界字符
        top_bottom_edge = ec * (menu_width + len(ec) * 2)
        # 墙是包括边界和空白（单行）
        top_bottom_wall = f"{ec}{wc * menu_width}{ec}"
        left_wall = f"{ec}{wc * left}"
        right_wall = f"{wc * right}{ec}"

        print("\n".join([top_bottom_edge] + [top_bottom_wall] * top))
        for i, opt in enumerate(self.children):
            # 序号右对齐，选项标题左对齐
            print(f"{left_wall}{i + 1:>{max_len_serial}}{sm}{opt.title:<{max_len_option}}{right_wall}")
        print("\n".join([top_bottom_wall] * bottom + [top_bottom_edge]))

    def _request_option(self) -> _OptionNode | None:
        """
        请求用户输入选项序号

        :return: 用户选择的选项节点或 None
        """
        choice, state = request_input(
            "\nYour option", "No such option.",
            has_default_val=False, has_quit_val=False,
            check_func=lambda x: x.isdigit() and 1 <= int(x) <= len(self.children),
            ask_again=False, need_confirm=False
        )
        if state is False:
            return None

        return self.children[int(choice) - 1]

    def _enter_next_level(self) -> int:
        """
        进入下一级菜单（执行函数）

        :return: 状态码
        """
        state = self._ENTER_CODE

        while state not in (self._RETURN_CODE, self._QUIT_CODE):
            # 如果上次执行不是返回上级菜单或退出，就继续在当前菜单循环
            # 用户指定是否需要重新绘制菜单，
            # 或者如果上次执行是进入下级菜单，则一定要绘制菜单
            # 这里 state == self._ENTER_CODE 有两种情况，
            # 一种是第一次进入 while 循环的时候，此时表示用户选择进入下级菜单
            # 另一种是用户选择返回上级菜单，结束了 while 循环，
            # 此函数返回 self._ENTER_CODE，被上层的该函数的 while 循环捕获到
            if self.menu_config["draw_menu_again"] or state == self._ENTER_CODE:
                self._draw_menu()

            # 此处设置为 None，是为了防止用户输入不符合要求的序号时，
            # 重新循环 state 还是 self._ENTER_CODE 导致又绘制了一遍菜单
            state = None
            opt = self._request_option()
            if opt is None:
                continue

            state = opt.exec_func(*opt.args, **opt.kwargs)

        # 如果是退出信号，就一路退回到根节点
        if state == self._QUIT_CODE:
            return self._QUIT_CODE
        else:
            return self._ENTER_CODE

    def _return_previous_level(self) -> int:
        """
        返回上一级菜单（执行函数）

        :return: 状态码
        """
        return self._RETURN_CODE

    def _quiting_level(self) -> int:
        """
        退出该工具（执行函数）

        :return: 状态码
        """
        return self._QUIT_CODE

    def add_option(self,
                   title: str = "Untitled Option",
                   exec_func: Callable = None,
                   args: tuple = None,
                   kwargs: dict = None) -> _OptionNode:
        """
        添加选项

        :param title: 选项标题
        :param exec_func: 选择该选项后要执行的函数；对于用户设定的节点，该执行函数必须返回 None
        :param args: 执行函数的位置参数
        :param kwargs: 执行函数的命名参数
        :return: 选项节点对象
        """
        # 如果在此父选项下创建了新的选项，该父选项会成为下一级的菜单入口
        # 此处进行后缀标记
        if not self.title.endswith(" [d]"):
            self.title = f"{self.title} [d]"

        option = _OptionNode(title, exec_func, args, kwargs, self.menu_config, _is_root=False)
        self.children.append(option)

        # 父选项成为菜单入口之后，其执行函数只能为“进入下一级菜单”
        self.exec_func = self._enter_next_level
        return option

    def add_return_option(self):
        """
        添加返回上级菜单的选项

        :return: None
        """
        self.add_option(title="[Back]", exec_func=self._return_previous_level)

    def add_exit_option(self):
        """
        添加退出菜单选项

        :return: None
        """
        self.add_option(title="[Exit]", exec_func=self._quiting_level)

    def start_loop(self):
        """开启循环，只在根选项调用"""
        if self._is_root:
            self._enter_next_level()
            print("Exit CliHelper. Bye.")
        else:
            print("Current option is not the root option. Exit.")


class CliHelper(_OptionNode):
    """命令行辅助工具"""

    def __init__(self, menu_config: MenuConfig = None, show_version: bool = True):
        super().__init__("Main Menu", menu_config=menu_config, _is_root=True)

        if show_version:
            print(f"CliHelper v{version[0]}.{version[1]} ({version[-1]})\n")
