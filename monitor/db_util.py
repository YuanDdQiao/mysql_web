# -*- coding: utf-8 -*-

import base_class
import pymysql
from DBUtils.PooledDB import PooledDB

class DBUtil(object):
    __instance = None
    __connection_pools = {}

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if(DBUtil.__instance is None):
            DBUtil.__instance = object.__new__(cls, *args, **kwargs)
        return DBUtil.__instance

    def execute(self, host_info, sql):
        connection, cursor = None, None
        try:
            connection, cursor = self.execute_for_db(host_info, sql)
        finally:
            self.close(connection, cursor)

    def fetchone(self, host_info, sql):
        connection, cursor = None, None
        try:
            connection, cursor = self.execute_for_db(host_info, sql)
            return cursor.fetchone()
        finally:
            self.close(connection, cursor)

    def fetchall(self, host_info, sql):
        connection, cursor = None, None
        try:
            connection, cursor = self.execute_for_db(host_info, sql)
            return cursor.fetchall()
        finally:
            self.close(connection, cursor)

    def execute_for_cursor(self, sql, connection=None, cursor=None):
        return self.cursor_execute(connection, cursor, sql)

    def fetchone_for_cursor(self, sql, connection=None, cursor=None):
        cursor = self.cursor_execute(connection, cursor, sql)
        return cursor.fetchone()

    def fetchall_for_cursor(self, sql, connection=None, cursor=None):
        cursor = self.cursor_execute(connection, cursor, sql)
        return cursor.fetchall()

    def cursor_execute(self, connection, cursor, sql):
        if(cursor == None):
            cursor = connection.cursor()
        cursor.execute(sql)
        return cursor

    def close(self, connection, cursor):
        if(cursor != None):
            cursor.close()
        if(connection != None):
            connection.commit()
            connection.close()

    def execute_for_db(self, host_info, sql):
        connection, cursor = self.get_conn_and_cur(host_info)
        cursor.execute(sql)
        return connection, cursor

    def get_conn_and_cur(self, host_info):
        connection = self.get_mysql_connection(host_info)
        cursor = connection.cursor()
        return connection, cursor

    def get_mysql_connection(self, host_info):
        if(self.__connection_pools.get(host_info.key) == None):
            # 这边添加超时设置是为了防止多线程操作导致数据库线程堆积
            # connect_timeout=1, read_timeout=1, write_timeout=1)
            # 超时还是会导致很多问题发生，比如查找information_schema.tables，它是一秒钟做不完的，那设置10秒？
            pool = PooledDB(creator=pymysql, mincached=5, maxcached=20,
                            host=host_info.host, port=host_info.port, user=host_info.user, passwd=host_info.password,
                            use_unicode=False, charset="utf8", cursorclass=pymysql.cursors.DictCursor, reset=False, autocommit=True,
                            connect_timeout=10, read_timeout=10, write_timeout=10)
            self.__connection_pools[host_info.key] = pool
        return self.__connection_pools[host_info.key].connection()

    def get_list_infos(self, host_info, sql):
        result = []
        for row in self.fetchall(host_info, sql):
            info = base_class.BaseClass(None)
            for key, value in row.items():
                setattr(info, key, value)
            result.append(info)
        return result

    def escape(self, string):
        return pymysql.escape_string(string)

