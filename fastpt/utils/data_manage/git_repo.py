#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil

import typer


class GitRepoPaser:
    @staticmethod
    def import_git_to_local(src: str) -> None:
        """
        导入 git 仓库测试数据

        :param src:
        :return:
        """

        if 'https' not in src:
            raise ValueError('git 仓库克隆地址错误, 请使用 https 地址')

        try:
            online_dir = os.path.join(os.path.abspath('./data'), 'online')
            typer.echo(online_dir)
            if os.path.exists(online_dir):
                shutil.rmtree(online_dir)
            os.makedirs(online_dir)
            c = os.system(f'cd {online_dir} && git clone {src}')
        except Exception as e:
            raise RuntimeError(f'git 苍鹭测试数据拉取失败：{e}')
        else:
            if c == 0:
                typer.secho('✅ git 仓库数据文件拉取成功')
            else:
                raise RuntimeError('❌ git 仓库测试数据拉取失败')
