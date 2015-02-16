# -*- coding:utf-8 -*-

"""
    交互式执行环境

    在 Bash Shell 下使用的交互式执行环境。
    支持 readline 的全部操作，包括快捷键和 <TAB> 命令补全。

    如果需要扩展命令，不建议直接修改本文件，可在其他模块中进行。

    [code]
    from mvc import Shell

    def do_hello(self, line):
        print "Hello, World!"


    Shell.do_hello = do_hello
    [/code]


    作者: Q.yuhen
    创建: 2011-07-31

    历史:
        2011-08-04  + 增加 add_methods。
"""

from sys import argv, _getframe
from os import popen
from cmd import Cmd
from subprocess import call
from pprint import pprint
from inspect import isfunction
from code import interact

from utility import ROOT_PATH



class Shell(Cmd, object):
    """
        交互式执行环境
    """

    intro = "Interactive Shell, version: 0.9.2011.08\n"                     \
        "\n"                                                                \
        "Commands:\n"                                                       \
        "   ?           List all commands\n"                                \
        "   ?<cmd>      Show cmd help message\n"                            \
        "   !<cmd>      Exec BashShell command\n"                           \
        "   clean       Remove project temp files\n"                        \
        "   py          Python interactive shell (CTRL+D exit)\n"           \
        "   q           Exit\n"                                             \
        "\n"                                                                \
        "Press <TAB><TAB> auto-complete, support readline shortcut key。\n" \
        "\n"                                                                \
        "Support command line args:\n"                                      \
        "   example: $ ./shell.py utest all\n"

    prompt = "$ "


    def default(self, line):
        if not line: return

        if line in ("quit", "exit", "q"):
            self.do_EOF(None)
        else:
            print "Unknown Command..."


    def do_shell(self, line):
        """
            执行 Bash Shell 命令
        """
        print popen(line).read()


    def do_clean(self, line):
        """
            删除临时文件
        """
        print "Remove temp files ..."
        call("""find "{0}" -name "*.py[co]" | xargs rm -rf""".format(ROOT_PATH), shell = True)


    def do_py(self, line):
        """
            进入 Python 交互环境，CTRL+D 返回。
        """
        interact(local = dict(shell = self))


    def do_config(self, line):
        """
            显示系统设置
        """
        for k in sorted(__conf__.__dict__.keys()):
            if k.startswith("__"): continue
            print "  {0:<20} : {1}".format(k, __conf__.__dict__[k])


    def do_EOF(self, line):
        print "Bye..."
        exit(0)


    def run(self):
        if len(argv) > 1:
            method = getattr(self, "do_" + argv[1], None)

            if not method: 
                print "Unknown command!"
                exit(0)

            method(" ".join(argv[2:]))

        else:
            self.cmdloop()


    @staticmethod
    def add_methods(*funcs):
        """
            检索调用模块所有测试函数，并添加到 Shell。

            参数:
                funcs   要添加的函数，为空时自动查找。
        """
        if not funcs:
            funcs = [v for k, v in _getframe(1).f_globals.items() if k.startswith("do_") and isfunction(v)]

        for f in funcs:
            setattr(Shell, f.__name__, f)



__all__ = ["Shell"]
