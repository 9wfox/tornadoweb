#-*- coding:utf-8 -*-

"""
    MVC 根模块

    扫描 /action 下所有的 handler，并依据其 @url 装饰器进行组装。
    创建 Tornado HTTPServer 做为系统运行环境。

    执行 run() 启动系统。
"""

from os import getpid#DELETE , getppid
from sys import argv
from inspect import isclass
from multiprocessing import cpu_count

import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application as WebApplication

from web import BaseHandler
from utility import app_path, get_members


class Application(object):
    """
        MVC Application

        1. 扫描 action，自动按照优先级(handler url order)装配 Handlers。
        2. 创建 tornado.web.Application。
        3. 根据配置情况(DEBUG)，创建子进行执行。
    """
    port = property(lambda self: self._port)
    handlers = property(lambda self: self._handlers)
    processes = property(lambda self: __conf__.DEBUG and 1 or cpu_count())
    processes = 1
    settings = property(lambda self: __conf__.__dict__)


    def __init__(self, port = None, callback = None):
        self._port = port or __conf__.PORT
        self._callback = callback
        self._handlers = self._get_handlers()
        self._webapp = self._get_webapp()
        self._parent = getpid()


    def _get_handlers(self):
        """
            获取 action.handlers

            添加路径 __conf__.ACTION_DIR_NAME 列表中的 action by ABeen 
        """
        # 查找所有 Handler。
        members = {}
        for d in __conf__.ACTION_DIR_NAME:
            members.update(get_members(d,
                           None,
                           lambda m: isclass(m) and issubclass(m, BaseHandler) and hasattr(m, "__urls__") and m.__urls__))

        # 分解 __urls__ 配置。
        handlers = [(pattern, order, h) for h in members.values() for pattern, order in h.__urls__]

        # 排序。
        handlers.sort(cmp = cmp, key = lambda x: x[1])

        handlers = [('/api/v1' + pattern, handler) for pattern, _, handler in handlers]

        handlers.append((r'^/(.*?)$', tornado.web.StaticFileHandler, {"path":"static", "default_filename":"index.html"}))
        return handlers



    def _get_webapp(self):
        """
            创建 tornado.web.Application
        """
        settings = {
            "PORT"          : self._port,
            #"static_path"   : app_path(__conf__.STATIC_DIR_NAME),
            #"template_path" : app_path(__conf__.TEMPLATE_DIR_NAME),
            "debug"         : __conf__.DEBUG,
            "cookie_secret" : __conf__.COOKIE_SECRET
        }

        self.settings.update(settings)
        return WebApplication(self._handlers, **settings)


    def _run_server(self):
        """
            启动 HTTP Server
        """
        try:
            if __conf__.DEBUG:
                self._webapp.listen(self._port)
            else:
                server = HTTPServer(self._webapp)
                server.bind(self._port)
                server.start(0)

            IOLoop.current().start()
        except KeyboardInterrupt:
            print "exit ..."


    def run(self):
        if self._callback: self._callback(self)
        self._run_server()



def run(port = None, config = None, callback = None):
    Application(port, callback).run()



__all__ = ["run"]
