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
from typing import Callable

version = (1, 3, 20230705)


def request_input(prompt_msg: str,
                  err_msg: str = "Invalid value.",
                  *,
                  has_default_val: bool = False,
                  default_val: str = "",
                  has_quit_val: bool = True,
                  quit_val: str = "q",
                  check_func: Callable[[str], bool] | None = None,
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


class CliHelper(object):
    """命令行辅助工具"""

    class _OptionNode(object):
        """选项节点"""

        def __init__(self,
                     title: str = "Untitled Option",
                     exec_func: Callable = None,
                     args: tuple | None = None,
                     kwargs: dict | None = None):
            """
            :param title: 选项标题
            :param exec_func: 选择该选项后要执行的函数；对于用户设定的节点，该执行函数必须返回 None
            :param args: 执行函数的位置参数
            :param kwargs: 执行函数的命名参数
            """
            self.title = title
            self.exec_func = exec_func if exec_func is not None else self._default_func
            self.args = args if args is not None else ()
            self.kwargs = kwargs if kwargs is not None else {}
            self.children = []  # type: list[CliHelper._OptionNode]

        @staticmethod
        def _default_func():
            """用户没有指定执行函数时执行的默认函数"""
            print("No function")

    # 返回上级菜单的执行函数的返回值
    _RETURN_CODE = 0xbabe
    # 进入下级菜单的执行函数的返回值
    _ENTER_CODE = 0xbeef

    def __init__(self, *,
                 left_padding: int = 2,
                 right_padding: int = 10,
                 top_padding: int = 1,
                 bottom_padding: int = 1,
                 border_char: str = "#",
                 wall_char: str = " ",
                 serial_marker: str = ". ",
                 draw_menu_again: bool = False,
                 show_version: bool = True):

        self._root = self._OptionNode("Main Menu")

        self._left_padding = left_padding
        self._right_padding = right_padding
        self._top_padding = top_padding
        self._bottom_padding = bottom_padding
        self._border_char = border_char
        self._wall_char = wall_char
        self._serial_marker = serial_marker
        self._draw_menu_again = draw_menu_again

        if show_version:
            print(f"CliHelper v{version[0]}.{version[1]} ({version[-1]})\n")

    @staticmethod
    def _get_max_length_of_option_titles(p_option: _OptionNode) -> int:
        """
        获取菜单选项中最长的选项标题的长度

        :param p_option: 菜单选项的父选项节点
        :return: 菜单选项中最长的选项标题的长度
        """
        return max([len(c.title) for c in p_option.children])

    def _draw_menu(self, p_option: _OptionNode):
        """
        绘制菜单选项

        :param p_option: 要绘制的菜单选项的父选项节点
        :return: None
        """
        left = self._left_padding
        right = self._right_padding
        top = self._top_padding
        bottom = self._bottom_padding
        bc = self._border_char
        wc = self._wall_char
        sm = self._serial_marker

        max_len_option = self._get_max_length_of_option_titles(p_option)
        # 获取最大选项序号的位数
        max_len_serial = len(str(len(p_option.children)))
        # 一个选项的总宽度
        option_width = max_len_serial + len(sm) + max_len_option
        # 菜单的宽度（加上左右两边的空白，但不包括边界）
        menu_width = left + option_width + right
        # 上下边界
        top_bottom_border = bc * (menu_width + len(bc) * 2)
        # 墙是包括边界和空白
        top_bottom_wall = f"{bc}{wc * menu_width}{bc}"
        left_wall = f"{bc}{wc * left}"
        right_wall = f"{wc * right}{bc}"

        print("\n".join([top_bottom_border] + [top_bottom_wall] * top))
        for i, opt in enumerate(p_option.children):
            # 序号右对齐，选项标题左对齐
            print(f"{left_wall}{i + 1:>{max_len_serial}}{sm}{opt.title:<{max_len_option}}{right_wall}")
        print("\n".join([top_bottom_wall] * bottom + [top_bottom_border]))

    @staticmethod
    def _request_option(p_option: _OptionNode) -> _OptionNode | None:
        """
        请求用户输入选项序号

        :param p_option: 当前菜单选项的父选项节点
        :return: 用户选择的选项节点或 None
        """
        choice, state = request_input(
            "\nYour option", "No such option.",
            has_default_val=False, has_quit_val=False,
            check_func=lambda x: x.isdigit() and 1 <= int(x) <= len(p_option.children),
            ask_again=False, need_confirm=False
        )
        if state is False:
            return None

        return p_option.children[int(choice) - 1]

    def _enter_next_level(self, p_option: _OptionNode) -> int:
        """
        进入下一级菜单（执行函数）

        :param p_option: 下一级菜单的入口选项节点
        :return: 状态码
        """
        state = self._ENTER_CODE

        while state != self._RETURN_CODE:
            # 如果上次执行不是返回上级菜单，就继续在当前菜单循环
            # 用户指定是否需要重新绘制菜单，
            # 或者如果上次执行是进入下级菜单，则一定要绘制菜单
            # 这里 state == self._ENTER_CODE 有两种情况，
            # 一种是第一次进入 while 循环的时候，此时表示用户选择进入下级菜单
            # 另一种是用户选择返回上级菜单，结束了 while 循环，
            # 此函数返回 self._ENTER_CODE，被上层的该函数的 while 循环捕获到
            if self._draw_menu_again or state == self._ENTER_CODE:
                self._draw_menu(p_option)

            # 此处设置为 None，是为了防止用户输入不符合要求的序号时，
            # 重新循环 state 还是 self._ENTER_CODE 导致又绘制了一遍菜单
            state = None
            opt = self._request_option(p_option)
            if opt is None:
                continue

            state = opt.exec_func(*opt.args, **opt.kwargs)

        return self._ENTER_CODE

    def _return_previous_level(self) -> int:
        """
        返回上一级菜单（执行函数）

        :return: 状态码
        """
        return self._RETURN_CODE

    def add_option(self,
                   parent: _OptionNode | None = None,
                   title: str = "Untitled Option",
                   exec_func: Callable = None,
                   args: tuple = None,
                   kwargs: dict = None) -> _OptionNode:
        """
        添加选项

        :param parent: 要添加的选项的父选项节点，若为 None 则为根节点（显示在主菜单）
        :param title: 选项标题
        :param exec_func: 选择该选项后要执行的函数；对于用户设定的节点，该执行函数必须返回 None
        :param args: 执行函数的位置参数
        :param kwargs: 执行函数的命名参数
        :return: 选项节点对象
        """
        if parent is None:
            parent = self._root
        # 如果在此父选项下创建了新的选项，该父选项会成为下一级的菜单入口
        # 此处进行后缀标记
        if not parent.title.endswith(" [d]"):
            parent.title = f"{parent.title} [d]"

        option = self._OptionNode(title, exec_func, args, kwargs)
        parent.children.append(option)

        # 父选项成为菜单入口之后，其执行函数只能为“进入下一级菜单”
        parent.exec_func = self._enter_next_level
        # “进入下一级菜单”这个执行函数的参数就是其选项本身
        parent.args = (parent, )

        return option

    def add_return_option(self, p_option: _OptionNode):
        """
        添加返回上级菜单的选项

        :param p_option: 要添加该选项的父选项节点
        :return: None
        """
        self.add_option(p_option, title="[Back]", exec_func=self._return_previous_level)

    def add_exit_option(self, p_option: _OptionNode | None = None):
        """
        添加退出菜单选项

        :param p_option: 要添加该选项的父选项节点
        :return: None
        """
        if p_option is None:
            p_option = self._root
        self.add_option(p_option, title="[Exit]", exec_func=exit, args=(0,))

    def start_loop(self):
        """开启主循环"""
        self._enter_next_level(self._root)
