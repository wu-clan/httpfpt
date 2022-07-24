# python接口自动化测试框架

## 🧠设计思路

- python3 + pytest + parametrize + requests / httpx + yaml / excel ...

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
- pytest.ini pytest 参数配置
- run.py: pytest 主程序入口

## 👨‍💻👩‍💻使用

```shell
# 克隆
git clone https://gitee.com/wu_cl/automated_api_pytest.git
# 安装依赖包
pip install -r requirements.txt
```

### 1: 指定用例所在目录

testcase 目录下的一级文件夹可视为单个项目目录

在 config.toml 配置中修改 project = xxx 为对应的项目目录名

### 2: 全局变量及hooks的使用

全局参数定义：

    在 data 目录下的 global_vars.yml 中进行定义，请参考 demo

hooks 函数定义:

    在 data 目录下的 hooks.py 文件中定义，请参考 demo    

使用:

    变量表达式: ${var} 或 $var
    hooks 变量表达式: ${func()} 或 ${func($var1, $var2)
    变量和 hooks 开头: a-zA-Z_

### 3: 用例编写

请勿更改用例模板, 详细介绍在路上...

### 4: 如何运行测试

直接运行 run.py 文件

main 程序参数可视情况进行自定义

### 5: 如何查看报告

运行完之后到 report 文件夹下查看

## ❓问题相关

### 1: 为什么日志没有内容

日志内容需要手动写入, 详细示例demo中几乎都有体现, 请自行查看

### 2: 为什么没有测试报告

html

    自动生成，检查 run 参数是否开启html报告, 默认开启

excel 
    
    测试报告要手动写入, 示例请查看测试用例: test_api.py

yaml 

    测试报告要手动写入, 示例详情请查看测试用例: test_api.py

allure

    自动生成, 默认开启并自动打开浏览器访问, 前提已正确安装 allure 程序
    
### 2: excel 测试报告有问题

1: excel 测试数据要严格按照 APITestCaseTEMPLATE.xlsx 模板格式编写, 

注意用例的 case_id, 末尾数字需要对应顺序, 第几个用例数字就要是几

### 3: yaml 测试报告有问题

1: yaml 测试数据要严格按照 APITestCaseTEMPLATE.yaml 模板格式编写,

但是对用例数据没有特殊要求

*⚠ 对于 excel 和 yaml 测试报告, 建议对文件名使用时间戳, 避免文件覆盖*

