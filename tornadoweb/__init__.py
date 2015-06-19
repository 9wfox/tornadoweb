#-*- coding:utf-8 -*-

"""
    MVC package

    只需 "from mvc import *" 即可，无需导入具体模块。

    需要安装的第三方扩展库:
        pymongo         
        redis
        tornado             
        msgpack-python


    作者: Q.yuhen
    创建: 2011-07-31

    历史:
"""
#DELETE windows不兼容， TODO
from app import *
from cache import *
from config import *
from gfs import *
from logic import *
#DELETE from service import *
from shell import *
from test import *
from utility import *
from web import *
from mvc import settings



def __load__():

    # 默认编码
    set_default_encoding()

    # 执行初始化函数（有优先关系，不能自动扫描执行）
    import config
    config.__load__()

    import test
    test.__load__()
    

__load__()
del __load__
