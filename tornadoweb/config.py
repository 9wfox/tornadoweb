#-*- coding:utf-8 -*-

import __builtin__

from os.path import exists
from types import ModuleType

from utility import app_path, staticclass



@staticclass
class ConfigLoader(object):

    @staticmethod
    def load(config = None):
        """
            合并设置，返回设置模块对象。
        """
        if config:
            pys = map(app_path, (config, ))
        else:
            pys = map(app_path, ("settings.py", ))

        dct = {}
        module = ModuleType("__conf__")

        for py in pys:
            if exists(py): execfile(py, dct)

        for k, v in dct.items():
            setattr(module, k, v)

        __builtin__.__conf__ = module

