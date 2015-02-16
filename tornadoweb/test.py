# -*- coding:utf-8 -*-

"""
    单元测试辅助

    自动查找 "/utest/test_*.py" 单元测试模块，并载入所有继承自 TestCase 中的测试方法。
    通常配合 "交互式执行环境 (Shell)" 使用，可以完成单个、多个或全部单元测试执行。
    支持在 Shell 中完成对单元测试名称的自动补全操作。

    注意事项:
        1. 测试模块文件名必须是 test_*.py。
        2. 测试模块中可以包含多个继承自 unittest.TestCase 的测试类。
        3. 每个测试类中可以有多个以 "test" 开头的测试方法。

    [code]
    class MyTest(TestCase):

        def test_cache(self):
            self.assertEqual(...)
    [/code]

    作者: Q.yuhen
    创建: 2011-07-31

    历史:
        2011-08-18  * _run_testcase 支持通配符
"""

from os import listdir
from os.path import join as path_join
from fnmatch import fnmatch
from pprint import pprint
from inspect import isclass, ismethod, getmembers
from unittest import TestCase, TextTestRunner, TestSuite

from utility import get_members


class UTestLoader(object):
    """
        单元测试辅助类

        1. 扫描 utest 下所有单元测试模块 (test_*.py)。
        2. 提取所有单元测试单元(TestCase subclass)中可用的单元测试函数(test_* function)。
        3. 对命令行交互 Shell 进行扩展，提供 utest 命令。
        4. 支持 utest, utest all, utest t1, t2, utest t* 等执行方式。
    """

    def __init__(self):
        self._suites = {}
        self._names = []
        self._load()
        self._shell()


    def _load(self):
        # 载入所有测试模块(test_*.py)，并提取所有 TestCase 类。
        testcases = get_members("utest", 
                lambda k: k.startswith("test_"), 
                lambda o: isclass(o) and issubclass(o, TestCase))

        # 找出所有测试方法，并构件 TestSuite 对象。
        for name, cls in testcases.items():
            for n, m in getmembers(cls):
                if n.startswith("test") and ismethod(m):
                    self._suites["{0}.{1}".format(name, n)] =  TestSuite((cls(n),))

        self._names = sorted(self._suites.keys())


    def run(self, names):
        """
            执行单元测试

            参数：
                names = all     运行全部单元测试方法
                                也可以是多个以空格隔离的 test_name。
        """
        if names == "all":
            suite = TestSuite(self._suites.values())
        else:
            # 按照参数（用户输入）顺序执行单元测试
            keys = names.split()
            vals = [self._suites[n] for k in keys for n in self._names if fnmatch(n, k)]

            if not vals:
                print "UnitTest method not found!"
                return

            # 去重
            values = []
            map(lambda v: v not in values and values.append(v), vals)

            # 显示要执行的单元测试
            print "UnitTest:"
            pprint(values)
            print "-" * 20
                        
            suite = TestSuite(values)
       
        TextTestRunner().run(suite)


    def _shell(self):
        """
            扩展 Shell
        """

        utest = self

        def do_utest(self, line):
            """
                单元测试

                utest               显示所有可用单元测试
                utest <TAB><TAB>    命令参数自动完成
                utest <name>, ...   执行一个或多个单元测试（支持通配符）        
                utest all           执行全部单元测试
            """
            if not line or not line.strip():
                pprint(utest._names)
            else:
                utest.run(line)
                

        def complete_utest(self, text, line, begidx, endidx):
            """
                单元测试自动完成
            """
            if not text:
                return utest._names
            else:
                return [n for n in utest._names if n.startswith(text)]

        from shell import Shell
        Shell.do_utest = do_utest
        Shell.complete_utest = complete_utest


def __load__():
    if __debug__: UTestLoader() 



# 不对外公开成员
__all__ = []
