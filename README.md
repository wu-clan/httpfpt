# HttpFpt

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/wu-clan/httpfpt/ci.yml?logo=github)
[![GitHub](https://img.shields.io/github/license/wu-clan/httpfpt)](https://github.com/wu-clan/httpfpt/blob/master/LICENSE)
![Static Badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/wu-clan/httpfpt)

[//]: # (![GitHub release &#40;with filter&#41;]&#40;https://img.shields.io/github/v/release/wu-clan/httpfpt&#41;)

基于 HTTP 请求的快速数据驱动 pytest 接口自动化测试框架

我在掘金发表了关于 `HttpFpt` 的前身和由来，包括部分功能点的说明， 感兴趣

的小伙伴可以一睹为快，[点击跳转](https://juejin.cn/post/7224314619867136037)

## 功能点

- 多项目分级，自由切换，互不干扰
- 测试数据隔离，自动解析与验证
- 测试数据错误定位（参数错误，重复测试用例ID...）
- 多环境自定义配置，不同用例可以选择不同的运行环境
- 动态环境配置，自动识别和应用当前请求所需的基础环境配置
- 动态参数化，可以通过全局变量，局部变量，缓存变量，关联变量等方式进行参数化
- 数据依赖，支持接口返回数据共享，轻松实现接口依赖
- 钩子函数，支持调用自定义钩子函数，实现更多的自定义功能
- 日志记录，自动记录测试过程中的请求数据日志
- 多元化断言，json断言，sql断言，原生 python assert 断言
- 测试用例自动生成，可以根据测试数据文件自动生成测试用例
- 自动测试报告，html, allure
- 自动测试结果通知，飞书，钉钉，~~企业微信~~，邮箱
- ......

## ⬇️ 下载

克隆:

```shell
git clone https://github.com/wu-clan/httpfpt.git
```

## 🧑‍💻 DEV

1. 安装依赖:

    ```shell
    pip install -r requirements.txt
    ```

2. 安装 redis 并启动服务

   [Redis Windows](https://github.com/redis-windows/redis-windows)

   [Linux / macOS](https://redis.io/download/)

   [Docker](https://hub.docker.com/_/redis)

3. 安装 mysql 并创建一个任意名称数据库，同步修改 conf.toml 中的数据库配置

   [Windows / Linux / macOS](https://dev.mysql.com/downloads/installer/)

   [Docker](https://hub.docker.com/_/mysql)

> [!WARNING]
> allure 测试报告默认使用 allure-pytest
> 生成，但是不能直接访问，你必须安装 [allure](https://www.yuque.com/poloyy/python/aiqlmi)
> 本地程序和 [Java JDK](https://adoptopenjdk.net/archive.html?variant=openjdk8&jvmVariant=hotspot) 才能进行可视化浏览

## 帮助

有关更多详细信息，请参阅 [文档](https://wu-clan.github.io/httpfpt_docs)
