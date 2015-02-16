    # -*- coding:utf-8 -*-

"""
    系统配置文件

    不建议修改本文件，应用设置应该保存在 /settings.py 应用配置文件中。
    应用配置会覆盖同名的系统配置。


    作者: Q.yuhen
    创建: 2011-07-31

    历史:
"""

# 服务器监听端口
PORT = 9999

# 网络连接超时(秒)
SOCK_TIMEOUT = 10

# SESSION 过期时间(秒)
SESSION_EXPIRE = 60 * 10

# 是否启动调试模式
DEBUG = True

# 是否启动压缩
GZIP = True

# 静态目录名
STATIC_DIR_NAME = "static"

# 模板目录名
TEMPLATE_DIR_NAME = "template"

# Action 目录名 
ACTION_DIR_NAME = "action"

# 登录链接
LOGIN_URL = "/login"

# COOKIE 加密
COOKIE_SECRET = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="

# COOKIE 安全
XSRF_COOKIES = False

# 对称加密 Key
ENCRYPT_KEY = "UfddHJa2H$43Lfd*saFf/da"

# 缓存服务器
CACHE_SERVERS = ("localhost", )

# 数据库服务器
DB_HOST = "localhost"

# 数据库名
DB_NAME = "test"

# GFS
GFS_NAME = "test_fs"

# 服务队列订阅
SERVICE_CHANNEL = "test_service"
