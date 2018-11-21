#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
    启动系统服务器

    默认参数保存在 settings.py 中，也可以通过命令行指定(--help 查看所有的命令行参数)。
    如果要使用 80 等端口，可能需要 "sudo ./run.py --port=80"。
"""


import threading
from datetime import datetime
from pprint import pprint
from optparse import OptionParser, OptionGroup

from tornadoweb import *

from action import *
import settings

def _show_info(app):
    """
        显示系统信息
    """
    print ("Server start on port {0} (processes: {1}) ...".format(app.port, app.processes))
    print ("Start time: {0}".format(datetime.now().isoformat(" ")))

    print

    print ("Parameters:")
    for k in sorted(dir(__conf__)):
        if k.startswith("__"): continue
        print ("  {0:<20} : {1}".format(k, getattr(__conf__, k)))

    print

    print ("Handlers:")
    handlers = sorted(app.handlers, key = lambda h: h[0])
    pprint(handlers)

    print



def _get_opt():
    parser = OptionParser("%prog [options]", version="%prog v0.9")
    parser.add_option("--port", dest = "port", default = 0, help = "Listen port.")
    parser.add_option("--config", dest = "config", default = "settings.py", help = "config")
    return parser.parse_args()


def main():
    opts, args = _get_opt()
    ConfigLoader.load(opts.config)
    run(port = opts.port, config = opts.config, callback = _show_info)

if __name__ == "__main__":
    main()




