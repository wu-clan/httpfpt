#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import datetime
import decimal

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
            log.error(f'数据库连接失败: {e}')
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
            log.error(f'执行 {sql} 失败: {e}')
        finally:
            self.close()

    def close(self):
        """
        关闭游标和数据库连接

        :return:
        """
        self.cursor.close()
        self.conn.close()

    def exec_case_sql(self, sql: list) -> dict:
        """
        执行用例 sql

        :param sql:
        :return:
        """
        data = {}
        rejected_sql_type = ['UPDATE', 'DELETE', 'INSERT', 'update', 'delete', 'insert']
        if any(_ in sql for _ in rejected_sql_type):
            raise ValueError(f'{sql} 中存在不允许的命令类型, 仅支持 DQL 类型 sql 语句')
        else:
            for s in sql:
                query_data = self.query(s)
                for k, v in query_data.items():
                    if isinstance(v, decimal.Decimal):
                        data[k] = float(v)
                    elif isinstance(v, datetime.datetime):
                        data[k] = str(v)
                    else:
                        data[k] = v
            return data
