#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import datetime
import decimal
from typing import NoReturn

import pymysql
from dbutils.pooled_db import PooledDB
from jsonpath import jsonpath

from fastpt.common.env_handler import write_env_vars
from fastpt.common.log import log
from fastpt.common.variable_cache import VariableCache
from fastpt.common.yaml_handler import write_yaml_vars
from fastpt.core import get_conf
from fastpt.core.path_conf import RUN_ENV_PATH
from fastpt.enums.sql_type import SqlType
from fastpt.enums.var_type import VarType
from fastpt.utils.enum_control import get_enum_values


class MysqlDB:
    def __init__(self):
        try:
            self.conn = PooledDB(
                pymysql,
                maxconnections=15,
                blocking=True,  # 防止连接过多报错
                host=get_conf.MysqlDB_HOST,
                port=get_conf.MysqlDB_PORT,
                user=get_conf.MysqlDB_USER,
                password=get_conf.MysqlDB_PASSWORD,
                database=get_conf.MysqlDB_DATABASE,
            ).connection()
        except BaseException as e:
            log.error(f'数据库 mysql 连接失败: {e}')
        # 声明游标
        self.cursor = self.conn.cursor()

    def query(self, sql: str, fetch: str = 'all'):
        """
        数据库查询

        :param sql:
        :param fetch: 查询条件; all / 任意内容（单条记录）
        :return:
        """
        try:
            self.cursor.execute(sql)
            if fetch == 'all':
                query_data = self.cursor.fetchall()
            else:
                query_data = self.cursor.fetchone()
        except Exception as e:
            log.error(f'执行 {sql} 失败: {e}')
        else:
            log.info(f'执行 {sql} 成功')
            return query_data
        finally:
            self.close()

    def execute(self, sql: str) -> NoReturn:
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
        else:
            log.info(f'执行 {sql} 成功')
        finally:
            self.close()

    def close(self) -> NoReturn:
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
        sql_type = get_enum_values(SqlType)
        if any(_.upper() in sql for _ in sql_type):
            raise ValueError(f'{sql} 中存在不允许的命令类型, 仅支持 DQL 类型 sql 语句')
        else:
            data = {}
            for s in sql:
                # 获取返回数据
                if isinstance(s, str):
                    log.info(f'执行 sql: {s}')
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
                    log.info(f'执行变量提取 sql: {s["sql"]}')
                    key = s['key']
                    set_type = s['type']
                    sql = s['sql']
                    json_path = s['jsonpath']
                    query_data = self.query(sql)
                    value = jsonpath(query_data, json_path)
                    if value:
                        value = value[0]
                    else:
                        raise ValueError(f'jsonpath 取值失败, 表达式: {json_path}')
                    if set_type == VarType.CACHE:
                        VariableCache().set(key, value)
                    elif set_type == VarType.ENV:
                        if env is None:
                            raise ValueError('写入环境变量准备失败, 缺少参数 env, 请检查传参')
                        write_env_vars(RUN_ENV_PATH, env, key, value)
                    elif set_type == VarType.GLOBAL:
                        write_yaml_vars({key: value})
                    else:
                        raise ValueError(
                            f'前置 sql 设置变量失败, 用例参数 "type: {set_type}" 值错误, 请使用 cache / env / global'  # noqa: E501
                        )
            return data
