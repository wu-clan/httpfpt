# Automated Api Pytest

基于数据驱动的接口自动化测试框架

## 功能点

- 多项目分级，自由切换，互不干扰
- 测试数据隔离，自动解析与验证
- 多环境自定义配置，不同数据文件可以选择不同的运行环境
- 动态环境配置，自动识别和应用当前请求所需的基础环境数据
- 动态参数化，可以通过全局变量，局部变量，缓存变量，关联变量等方式进行参数化
- 数据依赖，支持接口返回数据共享，轻松实现接口依赖
- 钩子函数，动态数据，自定义扩展等等由你自由发挥
- 日志记录，自动记录测试过程中的请求数据日志
- 多元化断言，json断言，sql断言，原生 python assert 断言
- 测试用例自动生成，可以根据接口测试数据自动生成测试用例
- 自动测试报告，html, allure
- 自动测试结果通知，飞书，钉钉，~~企业微信~~，邮箱
- ......

## 帮助

有关更多详细信息，请参阅 [文档](https://wu-clan.github.io/automated_api_pytest_docs)


## 贡献

欢迎加入，如果你有好的想法，可以提 issue 或者 pr

对于 PR:
1. Fork 仓库
2. git clone 你的仓库
3. 创建虚拟环境 `python3 -m venv venv`
4. 激活虚拟环境 `source venv/bin/activate`
5. 创建分支 `git checkout -b my-new-feature`
6. 提交修改到分支 `git commit -am 'Add some feature'`
7. 执行 ruff 检查并修复 `ruff check . --fix`
8. 执行 pre-commit 检查并修复 `pre-commit run --all-files --verbose`
9. 提交分支 `git push origin my-new-feature`
10. 创建 PR
