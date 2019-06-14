# -*- coding:utf-8 -*-

from inspect import isclass
from tornado.web import RequestHandler, ErrorHandler

class BaseHandler(RequestHandler):
    """
        Torando RequestHandler
        http://www.tornadoweb.org/

    """
    __UID__ = "__UID__"
    __USERNAME__ = "__USERNAME__"


    #def set_default_headers(self):
    #    self.set_header("Access-Control-Allow-Origin", "*")
    #    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    #    self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    #def options(self, *args, **kwargs):
    #    self.set_header("Access-Control-Allow-Origin", "*")
    #    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    #    self.set_header('Access-Control-Allow-Methods', 'POST, GET')

    def get_current_user(self):
        return self.get_secure_cookie(self.__USERNAME__)




ErrorHandler.__bases__ = (BaseHandler,)


def url(pattern, order = 0):
    def actual(handler):
        if not isclass(handler) or not issubclass(handler, RequestHandler):
            raise Exception("must be RequestHandler's sub class.")

        if not hasattr(handler, "__urls__"): handler.__urls__ = []
        handler.__urls__.append((pattern, order))

        return handler

    return actual


__all__ = ["BaseHandler", "url"]
