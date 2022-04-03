#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import pymysql
from dbutils.pooled_db import PooledDB

from fastpt.common.log import log
from fastpt.core import get_conf


class DB:

    def __init__(self):
        try:
            self.conn = PooledDB(
                pymysql,
                maxconnections=15,
                blocking=True,  # 防止连接过多报错
                host=get_conf.DB_HOST,
                port=get_conf.DB_PORT,
                user=get_conf.DB_USER,
                password=get_conf.DB_PASSWORD,
                database=get_conf.DB_DATABASE,
                charset=get_conf.DB_CHARSET,
            ).connection()
        except BaseException as e:
            log.error(f'数据库连接失败 \n {e}')
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        """
        数据库操作执行
        :return:
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            log.error(f'执行 {sql} 失败 \n {e}')
        else:
            self.close()

    def close(self):
        """
        关闭数据库
        :return:
        """
        self.cursor.close()
        self.conn.close()


db = DB()
