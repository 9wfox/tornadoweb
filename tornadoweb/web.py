# -*- coding:utf-8 -*-

"""
    Web 模块

    本模块主要对 Tornado (http://www.tornadoweb.org) 的 web.py 进行扩展和继承。

    作者: Q.yuhen
    创建: 2011-07-31

    历史:
        2011-08-19  + 增加登录相关操作。
        2011-08-20  + 增加 BaseHandler.get_error_html 处理。
                    - 删除 NotFoundHandler。
        2011-08-29  + 增加 Session。
                    * 在 BaseHandler 中自动创建上下文对象。
"""

from os.path import exists
from functools import wraps as func_wraps
from inspect import isclass, ismethod, isfunction
from datetime import datetime
from httplib import responses
from uuid import uuid4

from redis import Redis
from tornado.web import RequestHandler, ErrorHandler, authenticated as auth

from logic import LogicContext
from cache import op_cache
from utility import template_path, loads, dumps



class Session(object):
    """
        Session (cache store)

        示例:
            with LogicContext():
                session = Session("session_a", 60)

                session.a = 1
                session.b = "Hello, World!"

                self.assertEqual(session.a, 1)
                self.assertEqual(session.b, "Hello, World!")

                for k, v in session:
                    print k, v, type(v)

                del session.a
                self.assertIsNone(session.a)
    """

    _ID = "__SESSIONID__"

    def __init__(self, sid, expire = None):

        # 不要直接使用属性，或者使用getattr/setattr，和 __getattr__,__setattr__ 冲突。
        self.__dict__["_id"] = sid
        self.__dict__["_expire"] = expire or __conf__.SESSION_EXPIRE

    
    def __getattr__(self, name):
        value = op_cache(self._id, Redis.hget, name, expire_seconds = self._expire)
        return value and loads(value)


    def __setattr__(self, name, value):
        op_cache(self._id, Redis.hset, name, dumps(value), expire_seconds = self._expire)        


    def __delattr__(self, name):
        op_cache(self._id, Redis.hdel, name, expire_seconds = self._expire)        


    def __iter__(self):
        items = op_cache(self._id, Redis.hgetall, expire_seconds = self._expire)
        for k, v in items.items():
            yield k, loads(v)


    @classmethod
    def get(cls, get_cookie, set_cookie):
        """
            设置或获取 Session
        """
        sid = get_cookie(cls._ID)

        if not sid:
            sid = str(uuid4())
            set_cookie(cls._ID, sid)

        return Session(sid)



class BaseHandler(RequestHandler):
    """
        Torando RequestHandler

        http://www.tornadoweb.org/


        1. 自动创建和管理 LogicContext。
        2. 提供 Session 供 Action、Template 间共享数据。
        3. 提供登录和注销方法。
        4. 自定义错误模板，优先查找 {error_code}.html, error.html。

    """

    _USER_NAME = "__DONTASKMEWHOAMI__"
    _RETURN_URL = "__RETURNURL__"

    ### override ####################

    def _execute(self, transforms, *args, **kwargs):
        """
            为 Action Method 准备额外的上下文环境。
        """
        with LogicContext():
            super(BaseHandler, self)._execute(transforms, *args, **kwargs)


    def prepare(self):
        """
            预处理操作
        """
        self._pv_log()
        self._session()
        self._return_url()


    def get_current_user(self):
        """
            返回当前登录的用户名

            可以通过 current_user 读取。
        """
        return self.get_secure_cookie(self._USER_NAME)


    def get_error_html(self, status_code, **kwargs):
        """
            返回错误页面信息

            可以通过 send_error 向错误模板页发送数据。
        """
        template_name = "{0}.html".format(status_code)
        print status_code
        if not exists(template_path(template_name)): template_name = "error.html"
        if not exists(template_path(template_name)): return super(BaseHandler, self).get_error_html(status_code, **kwargs)
        
        kwargs.update(dict(status_code = status_code, message = responses[status_code]))
        return self.render_string(template_name, **kwargs)


    def render_string(self, template_name, **kwargs):
        """
            添加注入模板的自定义参数等信息
        """
        if hasattr(self, "session"): kwargs["session"] = self.session
        return super(BaseHandler, self).render_string(template_name, **kwargs)


    def render(self, template_path, **kwargs):
        super(BaseHandler,self).render(template_path, current_request = self, **kwargs)


    ### Log #######################

    def _pv_log(self):
        """
            记录访问日志
        """
        # _log 这个名字已经被霸占了！(#^.^#)
        if __conf__.DEBUG:
            print "{0}: {1}, {2}, {3}".format(
                    datetime.now().strftime("%H:%M:%S"), 
                    self.request.remote_ip, self.request.method, self.request.uri)


    ### Session ###################

    def _session(self):
        """
            设置或获取 Session
        """
        self.session = Session.get(self.get_cookie, self.set_cookie)


    ### Login ######################

    def _return_url(self):
        """
            处理登录返回跳转链接
        """
        if type(self).__name__ == "LoginHandler" and self.request.method == "GET":
            return_url = self.get_argument("next", None)
            if return_url: self.set_cookie(self._RETURN_URL, return_url)


    def signin(self, loginname, redirect = True, expires_days = None):
        """
            设置登录状态

            参数:
                loginname        用户名或者编号。
                redirect        是否跳转回登录前链接。
                expires_days    保存时间，None 表示 Session Cookie，关浏览器就木有了。
        """
        self.set_secure_cookie(self._USER_NAME, loginname, expires_days = expires_days)

        return_url = self.get_cookie(self._RETURN_URL)
        self.clear_cookie(self._RETURN_URL)
        if redirect and return_url: self.redirect(return_url)


    def signout(self, redirect_url = "/"):
        """
            注销登录状态

            参数:
                redirect_url    跳转链接，为 None 时不跳转 (Ajax 可能用得到)。
        """
        self.clear_cookie(self._USER_NAME)
        if redirect_url: self.redirect(redirect_url)



# 修改 tornado.web 默认错误处理方式
ErrorHandler.__bases__ = (BaseHandler,)



### Decorator ##############################################################################################

def url(pattern, order = 0):
    """
        Class Decorator: 设置路径匹配模式和排序序号

        1. 支持设置多个链接匹配规则。

        参数:
            pattern     链接正则匹配
            order       排序序号

        示例:
            @url(r"(?i)/(index.html?)?", 10)
            @url(r"(?i)/default.html?", 8)
            class IndexHandler(BaseHandler):
                pass
    """
    def actual(handler):
        if not isclass(handler) or not issubclass(handler, BaseHandler):
            raise Exception("must be BaseHandler's sub class.")

        if not hasattr(handler, "__urls__"): handler.__urls__ = []
        handler.__urls__.append((pattern, order))

        return handler

    return actual



def nocache(method):
    """
        Method Decorator: 不缓存，通用用于 ajax.getJSON。
    """
    if not ismethod(method) and not isfunction(method):
        raise Exception("must be Method.")

    @func_wraps(method)
    def wrap(self, *args, **kwargs):
        self.set_header("Cache-Control", "No-Cache")
        method(self, *args, **kwargs)

    return wrap



__all__ = ["BaseHandler", "auth", "url", "nocache"]
