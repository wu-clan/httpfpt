# python接口自动化测试框架

## 🧠设计思路
- python3 + pytest + parametrize + requests / httpx

## 👀目录结构介绍
- common/: 公共类
- core/: 配置
- data/: 测试数据
- db/: 数据库相关
- log/: 日志文件
- report/: 测试报告存放
- testcase/: 放置接口自动化测试项目和用例
- utils/: 工具包
- conftest.py: pytest.fixture 配置
- main.py: pytest 主程序入口
- pytest.ini pytest 参数配置

## 👨‍💻👩‍💻使用
```shell
# 下载
git clone https://gitee.com/wu_cl/automated_api_pytest.git
# 安装依赖包
pip install -r requirements.txt
```

### 1: 指定用例所在目录
```
testcase 目录下的文件夹可视为单个项目目录

在 config.toml 配置中修改 project = 名称 为对应的项目目录名即可
```
### 2: 如何运行测试
```
直接运行 main.py 文件

main 程序参数可视情况进行自定义
```
### 3: 如何查看报告
```
运行完之后到 report 文件夹下查看
```
## ❓问题相关
### 1: 为什么日志没有内容
```
日志内容需要手动写入, 详细示例demo中几乎都有体现, 请自行查看
```
### 2: 为什么没有测试报告
```
html 检查main程序是否开启html报告,默认开启
excel 测试报告要手动写入, 详情查看测试用例: test_api.py
yaml 测试报告要手动写入, 详情查看测试用例: test_api.py
```
### 2: excel 测试报告有问题
```
1: excel 测试数据要严格按照 APITestCaseTEMPLATE.xlsx 模板格式编写, 
文件名字可以变, 存放位置和文件中参数顺序不可以变
2: excel 测试报告名称可自定义或默认
```
### 3: yaml 测试报告有问题
```
1: yaml 测试数据要严格按照 APITestCaseTEMPLATE.yaml 模板格式编写,
文件名字可以变, 存放位置和文件中参数顺序不可以变
2: yaml 测试报告名称可自定义或默认
```