# -*- coding:utf-8 -*-
import os
from sys import argv
from hashlib import md5
from fnmatch import fnmatch
from datetime import datetime
from base64 import b64encode, b64decode
from inspect import ismodule, getmembers
from os.path import abspath, join as path_join, dirname, splitext


ROOT_PATH = dirname(abspath(argv[0]))
app_path = lambda n: path_join(ROOT_PATH, n)
template_path = lambda n: path_join(ROOT_PATH, "{0}/{1}".format(__conf__.TEMPLATE_DIR_NAME, n))
static_path = lambda n: path_join(ROOT_PATH, "{0}/{1}".format(__conf__.STATIC_DIR_NAME, n))



def staticclass(cls):
    def new(cls, *args, **kwargs):
        raise RuntimeError("Static Class")

    setattr(cls, "__new__", staticmethod(new))
    return cls



def get_modules(pkg_name, module_filter = None):
    """
        返回包中所有符合条件的模块。

        参数:
            pkg_name        包名称
            module_filter   模块名过滤器 def (module_name)
    """
    path = app_path(pkg_name)
    #py_filter = lambda f: all((fnmatch(f, "*.py"), not f.startswith("__"), module_filter and module_filter(f) or True))
    py_filter = lambda f: all((fnmatch(f, "*.pyc") or fnmatch(f, "*.py"), not f.startswith("__"), module_filter and module_filter(f) or True))
    names = [splitext(n)[0] for n in os.listdir(path) if py_filter(n)]
    return [__import__("{0}.{1}".format(pkg_name, n)).__dict__[n] for n in names]



def get_members(pkg_name, module_filter = None, member_filter = None):
    """
        返回包中所有符合条件的模块成员。

        参数:
            pkg_name        包名称
            module_filter   模块名过滤器 def (module_name)
            member_filter   成员过滤器 def member_filter(module_member_object)
    """
    modules = get_modules(pkg_name, module_filter)

    ret = {}
    for m in modules:
        members = dict(("{0}.{1}".format(v.__module__, k), v) for k, v in getmembers(m, member_filter))
        ret.update(members)

    return ret



def set_default_encoding():
    """
        设置系统默认编码
    """
    import sys, locale
    reload(sys)

    lang, coding = locale.getdefaultlocale()
    #sys.setdefaultencoding(coding)


### 哈希加密函数 ########################################################################################

def hash2(o):
    """
        哈希函数
    """
    return md5(str(o)).hexdigest()


def encrypt(s, base64 = False):
    """
        对称加密函数
    """
    e = _cipher().encrypt(s)
    return base64 and b64encode(e) or e



def decrypt(s, base64 = False):
    """
        对称解密函数
    """
    return _cipher().decrypt(base64 and b64decode(s) or s)



### 参数检查函数 ########################################################################################

def not_null(*args):
    """
        检查参数不为None
    """
    if not all(map(lambda v: v is not None, args)):
        raise ValueError("Argument must be not None/Null!")



def not_empty(*args):
    """
        检查参数不为空
    """
    if not all(args):
        raise ValueError("Argument must be not None/Null/Zero/Empty!")



def args_range(min_value, max_value, *args):
    """
        检查参数范围
    """
    not_null(*args)

    if not all(map(lambda v: min_value <= v <= max_value, args)):
        raise ValueError("Argument must be between {0} and {1}!".format(min_value, max_value))



def args_length(min_len, max_len, *args):
    """
        检查参数长度
    """
    not_null(*args)

    if not all(map(lambda v: min_len <= len(v) <= max_len, args)):
        raise ValueError("Argument length must be between {0} and {1}!".format(min_len, max_len))

