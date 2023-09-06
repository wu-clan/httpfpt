#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import datetime
import decimal
from typing import Optional

import pymysql
from dbutils.pooled_db import PooledDB
from jsonpath import jsonpath

from httpfpt.common.env_handler import write_env_vars
from httpfpt.common.log import log
from httpfpt.common.variable_cache import VariableCache
from httpfpt.common.yaml_handler import write_yaml_vars
from httpfpt.core import get_conf
from httpfpt.core.path_conf import RUN_ENV_PATH
from httpfpt.enums.query_fetch import QueryFetchType
from httpfpt.enums.sql_type import SqlType
from httpfpt.enums.var_type import VarType
from httpfpt.utils.enum_control import get_enum_values


class MysqlDB:
    def __init__(self) -> None:
        self._pool = PooledDB(
            pymysql,
            host=get_conf.MysqlDB_HOST,
            port=get_conf.MysqlDB_PORT,
            user=get_conf.MysqlDB_USER,
            password=get_conf.MysqlDB_PASSWORD,
            database=get_conf.MysqlDB_DATABASE,
            charset=get_conf.MysqlDB_CHARSET,
            maxconnections=15,
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待
            autocommit=False,  # 是否自动提交
        )
        self.conn = self._pool.connection()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)  # type: ignore

    def close(self) -> None:
        """
        关闭游标和数据库连接

        :return:
        """
        self.cursor.close()
        self.conn.close()

    def query(self, sql: str, fetch: str = 'all') -> dict:
        """
        数据库查询

        :param sql:
        :param fetch: 查询条件; one: 查询一条数据; all: 查询所有数据
        :return:
        """
        data = {}
        try:
            self.cursor.execute(sql)
            if fetch == QueryFetchType.ONE:
                query_data = self.cursor.fetchone()
            elif fetch == QueryFetchType.ALL:
                query_data = self.cursor.fetchall()
            else:
                raise ValueError(f'查询条件 {fetch} 错误, 请使用 one / all')
        except Exception as e:
            log.error(f'执行 {sql} 失败: {e}')
            raise e
        else:
            log.info(f'执行 {sql} 成功')
            try:
                for k, v in query_data.items():
                    if isinstance(v, decimal.Decimal):
                        if v % 1 == 0:
                            data[k] = int(v)
                        data[k] = float(v)
                    elif isinstance(v, datetime.datetime):
                        data[k] = str(v)
                    else:
                        data[k] = v
            except Exception as e:
                log.error(f'序列化 {sql} 查询结果失败: {e}')
                raise e
            return data
        finally:
            self.close()

    def execute(self, sql: str) -> int:
        """
        执行 sql 操作

        :return:
        """
        try:
            rowcount = self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            log.error(f'执行 {sql} 失败: {e}')
            raise e
        else:
            log.info(f'执行 {sql} 成功')
            return rowcount
        finally:
            self.close()

    def exec_case_sql(self, sql: str | list, env: Optional[str] = None) -> None:
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
            if isinstance(sql, str):
                log.info(f'执行 sql: {sql}')
                self.query(sql)
            for s in sql:
                # 获取返回数据
                if isinstance(s, str):
                    log.info(f'执行 sql: {s}')
                    if SqlType.select in s:
                        self.query(s)
                    else:
                        self.execute(s)
                # 设置变量
                if isinstance(s, dict):
                    log.info(f'执行变量提取 sql: {s["sql"]}')
                    key = s['key']
                    set_type = s['type']
                    sql_text = s['sql']
                    json_path = s['jsonpath']
                    query_data = self.query(sql_text)
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
