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
            ).connection()
        except BaseException as e:
            log.error(f'数据库连接失败 \n {e}')
        # 声明游标
        self.cursor = self.conn.cursor()

    def query(self, sql: str, fetch: str = "all"):
        """
        数据库查询

        :param sql:
        :param fetch: 查询条件; all / 任意内容（单条记录）
        :return:
        """
        self.cursor.execute(sql)
        if fetch == 'all':
            query_data = self.cursor.fetchall()
        else:
            query_data = self.cursor.fetchone()
        self.close()
        return query_data

    def execute(self, sql: str):
        """
        执行 sql 操作

        :return:
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            log.error(f'执行 {sql} 失败 \n {e}')
        finally:
            self.close()

    def close(self):
        """
        关闭游标和数据库连接

        :return:
        """
        self.cursor.close()
        self.conn.close()


db = DB()
