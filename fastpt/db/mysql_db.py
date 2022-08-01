#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import datetime
import decimal

import pymysql
from dbutils.pooled_db import PooledDB
from jsonpath import jsonpath

from fastpt.common.env_handler import write_env_vars
from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_handler import write_yaml_vars
from fastpt.core import get_conf
from fastpt.core.path_conf import RUN_ENV_PATH


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

    def exec_case_sql(self, sql: list, env: str = None) -> dict:
        """
        执行用例 sql

        :param sql:
        :param env:
        :return:
        """
        data = {}
        rejected_sql_type = ['UPDATE', 'DELETE', 'INSERT', 'update', 'delete', 'insert']
        if any(_ in sql for _ in rejected_sql_type):
            raise ValueError(f'{sql} 中存在不允许的命令类型, 仅支持 DQL 类型 sql 语句')
        else:
            for s in sql:
                # 获取返回数据
                if isinstance(s, str):
                    query_data = self.query(s)
                    for k, v in query_data.items():
                        if isinstance(v, decimal.Decimal):
                            data[k] = float(v)
                        elif isinstance(v, datetime.datetime):
                            data[k] = str(v)
                        else:
                            data[k] = v
                # 设置变量
                if isinstance(s, dict):
                    key = s['key']
                    set_type = s['set_type']
                    sql = s['sql']
                    json_path = s['jsonpath']
                    query_data = self.query(sql)
                    value = jsonpath(query_data, json_path)
                    if value:
                        value = value[0]
                    else:
                        raise ValueError(f'jsonpath取值失败, 表达式: {json_path}')
                    if set_type is None:
                        VariableCache().set(key, value)
                    elif set_type == 'cache':
                        VariableCache().set(key, value)
                    elif set_type == 'env':
                        if env is None:
                            raise ValueError('写入环境变量准备失败, 缺少参数 env, 请检查传参')
                        write_env_vars(RUN_ENV_PATH, env, key, value)
                    elif set_type == 'global':
                        write_yaml_vars({key: value})
                    else:
                        raise ValueError('前置 sql 设置变量失败, 用例参数 "set_type" 类型错误')
            return data
