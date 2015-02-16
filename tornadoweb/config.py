#-*- coding:utf-8 -*-

"""
    配置模块

    整个系统配置存放在 "系统配置文件 mvc/setting.py"、"应用配置文件 /setting.py" 中。
    应用配置文件会覆盖系统配置文件中的同名设置。鉴于 mvc 更新需要，不建议修改系统配置文件的任何参数。

    配置信息保存在 __builtin__.__conf__ 动态模块中，任何直接引用 __conf__.<name> 即可访问。


    作者: Q.yuhen
    创建: 2011-07-31

    历史:
        2011-08-04  * 将 refresh 改为 internal。
        2011-08-28  * 重构为 ConfigLoader。
"""

import __builtin__

from os.path import exists
from types import ModuleType

from utility import app_path, staticclass



@staticclass
class ConfigLoader(object):

    @staticmethod
    def _load():
        """
            合并设置，返回设置模块对象。
        """
        pys = map(app_path, ("mvc/settings.py", "settings.py"))
        dct = {}
        module = ModuleType("__conf__")

        for py in pys:
            if exists(py): execfile(py, dct)

        for k, v in dct.items():
            if not k.startswith("__"):
                setattr(module, k, v)
                
        return module


    @classmethod
    def refresh(cls):
        """
            设置内置配置访问模块
        """
        __builtin__.__conf__ = cls._load()



def __load__():
    ConfigLoader.refresh()



# 不对外部公开成员
__all__ = []
