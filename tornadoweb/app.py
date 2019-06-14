#-*- coding:utf-8 -*-

from inspect import isclass
from multiprocessing import cpu_count

import tornado.web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import RequestHandler, Application as WebApplication

from .utility import app_path, get_members


class Application(object):
    port = property(lambda self: self._port)
    handlers = property(lambda self: self._handlers)
    processes = 1
    settings = property(lambda self: __conf__.__dict__)

    def __init__(self, port = None, callback = None):
        self._port = port or __conf__.PORT
        self._callback = callback
        self._handlers = self._get_handlers()
        self._webapp = self._get_webapp()


    def _get_handlers(self):
        members = {}
        for d in __conf__.ACTION_DIR_NAME:
            members.update(get_members(d,
                           None,
                           lambda m: isclass(m) and issubclass(m, RequestHandler) and hasattr(m, "__urls__") and m.__urls__))

        handlers = [(pattern, order, h) for h in members.values() for pattern, order in h.__urls__]

        try:
            api_version = __conf__.API_VERSION
        except Exception as e:
            api_version = ''

        handlers = [(api_version + pattern, handler) for pattern, _, handler in handlers]

        handlers.append((r'^{}/(.*?)$'.format(api_version), tornado.web.StaticFileHandler, {"path":"static", "default_filename":"index.html"}))
        return handlers



    def _get_webapp(self):
        settings = {
            "PORT"          : self._port,
            "debug"         : __conf__.DEBUG,
            "cookie_secret" : __conf__.COOKIE_SECRET
        }

        self.settings.update(settings)
        return WebApplication(self._handlers, **settings)


    def _run_server(self):
        try:
            if __conf__.DEBUG:
                self._webapp.listen(self._port)
            else:
                server = HTTPServer(self._webapp)
                server.bind(self._port)
                server.start(0)

            IOLoop.current().start()
        except KeyboardInterrupt:
            print ("exit ...")


    def run(self):
        if self._callback: self._callback(self)
        self._run_server()



def run(port = None, config = None, callback = None):
    Application(port, callback).run()

__all__ = ["run"]

