# -*- coding:utf-8 -*-

"""
    GridFS 模块

    分布式文件系统辅助方法


    作者: Q.yuhen
    创建: 2011-08-24

    历史:
"""

from os.path import join as path_join, basename
from zlib import compress, decompress

from bson.objectid import ObjectId
from gridfs.errors import NoFile

from utility import mongo_conv, staticclass
from logic import get_context


@staticclass
class RedisGFS(object):

    @staticmethod
    def put(filename, data, gzip = False, **kwargs):
        """
            将字节数组作为文件内容保存到 GFS

            参数:
                filename    文件识别名
                data        文件内容
                gzip        是否压缩
                kwargs      附加元属性

            返回:
                文件唯一编号
        """
        kwargs.update(dict(filename = filename))

        if gzip:
            kwargs["gzip"] = True
            data = compress(data)

        gfs = get_context().get_gfs()
        return gfs.put(data, **kwargs)



    @staticmethod
    def get(fid):
        """
            获取文件内容和元数据

            参数:
                fid             文件唯一编号

            返回:
                (data, meta)    文件内容(字节数组), 元属性字典
        """
        if type(fid) is not ObjectId: fid = ObjectId(fid)
        gfs = get_context().get_gfs()

        with gfs.get(fid) as out:
            data, meta = out.read(), mongo_conv(out._file)
            if meta.get("gzip"): data = decompress(data)

            return data, meta


    @staticmethod
    def delete(fid):
        """
            删除文件
        """
        if type(fid) is not ObjectId: fid = ObjectId(fid)

        gfs = get_context().get_gfs()
        gfs.delete(fid)


    @staticmethod
    def delete_by_filename(filename):
        """
            相同文件名可能保存了多个副本，统统删除。
        """
        gfs = get_context().get_gfs()

        while True:
            try:
                fid = gfs.get_version(filename = filename)._id
                gfs.delete(fid)
            except NoFile:
                break


    @staticmethod
    def exists(fid):
        """
            判断文件是否存在
        """
        if type(fid) is not ObjectId: fid = ObjectId(fid)

        gfs = get_context().get_gfs()
        return gfs.exists(fid)


    @staticmethod
    def exists_by_filename(filename):
        """
            删除文件
        """
        gfs = get_context().get_gfs()
        return gfs.exists(filename = filename)


    @classmethod
    def put_file(cls, filename, gzip = False, **kwargs):
        """
            上传本地文件到 GFS

            参数:
                filename        本地文件名
                gzip            是否压缩
                kwargs          附加元属性

            返回:
                文件唯一编号
        """
        with open(filename, "r") as f:
            return cls.put(filename, f.read(), gzip, **kwargs)
   

    @classmethod
    def put_data(cls, filename, data, gzip = False, **kwargs):
        """
            上传文件流到 GFS
            参数:
                data        文件流
            返回：
                文件唯一编号
        """
        return cls.put(filename, data, gzip, **kwargs)


    @classmethod
    def get_file(cls, fid, saved_path):
        """
            下载文件，并保存到指定目录。

            参数:
                fid                 文件唯一编号
                saved_path          目标保存路径

            返回:
                (filename, meta)    保存后的目标文件名, 元属性字典
        """
        data, meta = cls.get(fid)
        filename = path_join(saved_path, basename(meta.get("filename")))

        with open(filename, "w") as f:
            f.write(data)

        return filename, meta



gfs_put = RedisGFS.put
gfs_get = RedisGFS.get
gfs_delete = RedisGFS.delete
gfs_delete_by_filename = RedisGFS.delete_by_filename
gfs_exists = RedisGFS.exists
gfs_exists_by_filename = RedisGFS.exists_by_filename
gfs_put_file = RedisGFS.put_file
gfs_get_file = RedisGFS.get_file
gfs_put_data = RedisGFS.put_data


__all__ = ["gfs_put", "gfs_get", "gfs_delete", "gfs_delete_by_filename", 
        "gfs_exists", "gfs_exists_by_filename", "gfs_put_file", "gfs_get_file",'gfs_put_data']
