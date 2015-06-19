# -*- coding:utf-8 -*-

"""
    杂类工具

    作者: Q.yuhen
    创建: 2011-07-31

    历史:
        2011-08-03  + 重构 get_pys_members。
        2011-08-15  * 修改 con_mongo_object，支持 objectid。
        2011-08-20  + 增加 template_path, static_path。
        2011-08-25  * 将参数检查函数从 loigc 转移过来。
        2011-08-27  * 重构 get_pys_members，改名 get_members。
"""

from sys import argv
from os import walk, listdir
from os.path import abspath, join as path_join, dirname, basename, splitext
from fnmatch import fnmatch
from hashlib import md5
from base64 import b64encode, b64decode
from inspect import ismodule, getmembers
from msgpack import loads, dumps

from bson.objectid import ObjectId
from pyDes import des, triple_des, PAD_PKCS5, CBC



### 应用程序路径函数 ####################################################################################

ROOT_PATH = dirname(abspath(argv[0]))
app_path = lambda n: path_join(ROOT_PATH, n)
template_path = lambda n: path_join(ROOT_PATH, "{0}/{1}".format(__conf__.TEMPLATE_DIR_NAME, n))
static_path = lambda n: path_join(ROOT_PATH, "{0}/{1}".format(__conf__.STATIC_DIR_NAME, n))



### 装饰器 #############################################################################################

def staticclass(cls):
    def new(cls, *args, **kwargs):
        raise RuntimeError("Static Class")

    setattr(cls, "__new__", staticmethod(new))
    return cls



class sealedclass(type):
    """
        metaclass: Sealed Class
    """
    _types = set()

    def __init__(cls, name, bases, attr):
        for t in bases:
            if t in cls._types: raise SyntaxError("sealed class")

        cls._types.add(cls)



class partialclass(type):
    """
        metaclass: Partial Class


        class A(object):
            y = 456
            def test(self): print "test"


        class B(object):
            __metaclass__ = partialclass
            __mainclass__ = A

            x = 1234
            def do(self):
                self.test()
                print self.x, self.y


        A().do()
    """
    def __init__(cls, name, bases, attr):
        print "cls:", cls
        print "name:", name
        print "bases:", bases
        print "attr:", attr

        main_class = attr.pop("__mainclass__")
        map(lambda a: setattr(main_class, a[0], a[1]), [(k, v) for k, v in attr.items() if "__" not in k])



### 杂类函数 ############################################################################################

def get_modules(pkg_name, module_filter = None):
    """
        返回包中所有符合条件的模块。

        参数:
            pkg_name        包名称
            module_filter   模块名过滤器 def (module_name)
    """
    path = app_path(pkg_name)
    py_filter = lambda f: all((fnmatch(f, "*.py"), not f.startswith("__"), module_filter and module_filter(f) or True))
    names = [splitext(n)[0] for n in listdir(path) if py_filter(n)]
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
    '''try:
        modules = get_modules(pkg_name, module_filter)
    except:
        return {}'''

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
    sys.setdefaultencoding(coding)



def conv_mongo_object(d):
    """
        将 MongoDB 返回结果中的:
            (1) Unicode 还原为 str。
            (2) ObjectId 还原为 str。
    """
    if isinstance(d, (unicode, ObjectId)):
        return str(d)
    elif isinstance(d, (list, tuple)):
        return [conv_mongo_object(x) for x in d]
    elif isinstance(d, dict):
        return dict([(conv_mongo_object(k), conv_mongo_object(v)) for k, v in d.items()])
    else:
        return d


mongo_conv = conv_mongo_object


### 哈希加密函数 ########################################################################################

def hash2(o):
    """
        哈希函数
    """
    return md5(str(o)).hexdigest()



_enc_key = lambda length: __conf__.ENCRYPT_KEY.zfill(length)[:length]
_cipher = lambda: des(_enc_key(8), mode = CBC, IV = "\0" * 8, padmode = PAD_PKCS5)

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



__all__ = ["ROOT_PATH", "app_path", "template_path", "static_path",
        "staticclass", "sealedclass", "partialclass",
        "get_modules", "get_members",
        "conv_mongo_object", "mongo_conv", "set_default_encoding",
        "hash2", "loads", "dumps", "encrypt", "decrypt",
        "not_null", "not_empty", "args_range", "args_length"]
