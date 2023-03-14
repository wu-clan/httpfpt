# python接口自动化测试框架

## 🧠 设计思路

- python3 + pytest + parametrize + requests / httpx + yaml / ~~excel~~ ...

## 🌴 目录结构介绍

- common/: 公共类
- core/: 配置
- data/: 测试数据
- db/: 数据库相关
- log/: 日志文件
- report/: 测试报告存放
- test_case/: 放置接口自动化测试项目和用例
- utils/: 工具包
- conftest.py: pytest.fixture 配置
- pytest.ini pytest 参数配置
- run.py: pytest 主程序运行入口

## ⬇️ 下载

克隆:

```shell
git clone https://gitee.com/wu_cl/automated_api_pytest.git
```

安装依赖包:

```shell
pip install -r requirements.txt
```

## 指定测试项目

为什么要指定测试项目？

为了能够将多个项目同时使用此套架构，而设计的这种模式，它的概念大致如下：

1. 在主的 test_case 目录下的一级目录视为单个项目目录，如 demo 中的 test_project 目录， 就等于是 test_project
   这个项目，需要在此项目目录下存放该项目所有相关的测试用例
2. 测试数据文件同样使用此规则，在 data > test_data > excel_data / yaml_data 目录下的一级目录视为单个项目目录，如 demo 中的
   test_project 目录， 就等于是 test_project 这个项目，需要在此项目目录下存放该项目所有相关的测试数据

## 测试用例数据说明

### 数据结构展示

yaml 数据：

```yaml
config:
  allure:
    epic:
    feature:
    story:
    severity:
  request:
    env:
    headers:
    timeout:
    verify:
    redirects:
    proxies:
      http:
      https:
  module:

test_steps:
  - name:
    case_id:
    description:
    is_run:
    request:
      method:
      url:
      params:
      headers:
      body_type:
      body:
      files:
    setup:
      testcase:
        - case_id:
          key:
          jsonpath:
        - event_query_001
      sql:
        - key:
          set_type:
          sql:
          jsonpath:
        - select * from xxx where xxx=xxx
      hooks:
      wait_time:
    teardown:
      sql:
      hooks:
      extract:
        - key:
          set_type:
          jsonpath:
      assert:
        - check:
          value:
          type:
          jsonpath:
        - assert 200 = pm.response.get('status_code')
        - check:
          value:
          type:
          sql:
          jsonpath:

      wait_time:
```

~~excel 数据：~~

release 版本暂不支持使用，目前这种方式会被提前拦截，就针对 excel 数据提出了参考方案，但
并未实现相关代码，感兴趣的话可以到文件 file_data_parse.py 中查看

### 参数说明

必填列中 `Y / Y` 表示如果父级填写则必须填写

| 参数            |         类型          | 必填    | 说明                                                                       |
|:--------------|:-------------------:|-------|:-------------------------------------------------------------------------|
| config        |        dict         | Y     | 当前文件中所有测试用例测统一配置                                                         |
| + allure      |        dict         | Y     | allure 测试报告配置                                                            |
| ++ epic       |         str         | Y     | allure epic                                                              |
| ++ feature    |         str         | Y     | allure feature                                                           |
| ++ story      |         str         | Y     | allure story                                                             |
| ++ severity   |         str         | N     | allure severity: severity、critical、normal、minor、trivial                  |
| + request     |        dict         | Y     | 请求参数                                                                     |
| ++ env        |         str         | Y     | 测试环境文件名, 位于 core/run_env/ 目录下                                            |
| ++ headers    |     dict / null     | N     | 请求头                                                                      |
| ++ timeout    |     int / null      | N     | 请求超时时长，如果存在且不为空，则应用到当前文件中的所有测试用例，如果不存在或为空，则默认应用 conf.toml 中的配置           |
| ++ verify     |     bool / null     | N     | 请求验证，应用同上                                                                |
| ++ redirects  |     bool / null     | N     | 重定向，应用同上                                                                 |
| ++ proxies    |     dict / null     | N     | 请求代理，应用同上                                                                |
| +++ http      |     str / null      | Y / Y | http 代理                                                                  |
| +++ https     |     str / null      | Y / Y | https 代理                                                                 |                                                                  |
| + module      |         str         | Y     | 用例所属模块, 为后期设计, 暂未特殊使用                                                    |
| test_steps    |     list / dict     | Y     | 测试步骤, 多条测试用例时，必须使用 list 格式                                               |
| + name        |         str         | Y     | 测试用例名称                                                                   |
| + case_id     |         str         | Y     | 测试用例唯一id                                                                 |
| + description |         str         | Y     | 测试用例描述                                                                   |
| + is_run      |     bool / null     | Y     | 跳过执行此测试用例                                                                |
| + request     |        dict         | Y     | 请求参数                                                                     |
| ++ method     |         str         | Y     | 请求方式，支持大小写                                                               |
| ++ url        |         str         | Y     | 请求链接，不包含域名，域名需在测试环境文件中配置                                                 |
| ++ params     |     dict / null     | Y     | 请求/查询参数                                                                  |
| ++ headers    |     dict / null     | Y     | 请求头，如果为空，则会应用上方配置中的请求头，如果上方也未配置，则不使用请求头                                  |
| ++ body_type  |     str / null      | Y     | 请求数据类型: None、form、x_form、binary、graphQL、text、js、json、html、xml            |
| ++ body       | dict / bytes / null | Y     | 请求体                                                                      |
| ++ files      |     dict / null     | Y     | 请求文件上传                                                                   |
| + setup       |        dict         | N     | 请求前置                                                                     |
| ++ testcase   |     list / null     | N     | 前置 testcase，当执行测试用例时，格式应为 List\[str]，当设置当前测试执行过程中的缓存变量时，格式应为 List\[dict] |  
| ++ sql        |     list / null     | N     | 前置 sql，当为执行 sql 时，格式为 List\[str]，当为设置变量时，格式为 List\[dict]                 |                                                              |
| ++ hooks      |     list / null     | N     | 前置函数，调用钩子函数，格式为 List\[str]                                               |
| ++ wait_time  |     int / null      | N     | 请求前等待时间                                                                  |
| + teardown    |        dict         | N     | 请求后置                                                                     |
| ++ sql        |     list / null     | N     | 后置 sql，同前置                                                               |
| ++ hooks      |     list / null     | N     | 后置函数，同前置                                                                 |
| ++ extract    |        list         | N     | 变量提取, 格式为 List\[dict]                                                    |
| ++ assert     |  list / str / null  | N     | 断言                                                                       |                                                        |
| ++ wait_time  |     int / null      | N     | 请求后等待时间                                                                  |

### 参数附加说明

#### testcase

setup 中的 testcase 参数支持两种功能

1: 执行关联测试用例

```yaml
testcase:
  - event_query_001
  - event_query_002
```

2: 设置当前测试用例执行前的缓存变量, 且仅供当前测试用例使用

```yaml
testcase:
  - case_id: 关联测试用例的 case_id
    key: 变量 key，str
    jsonpath: 值 value, jsonpath 表达式, 数据依赖关联测试用例的请求返回数据集
```

#### sql

setup / teardown 中的 sql 参数支持两种功能

1: 执行 sql 语句

```yaml
sql:
  - select * from xxx where xxx=xxx
  - select ...
```

2: 设置变量

```yaml
sql:
  - key: 变量 key，str
    set_type: 变量类型：env / global / cache
    sql: 执行 sql 查询，str
    jsonpath: 值 value, jsonpath 表达式, 数据依赖 sql 查询结果
```

#### extract

teardown 中的 extract 参数支持单种功能

- 变量提取

```yaml
extract:
  - key: 变量 key，str
    set_type: 变量类型：env / global / cache
    jsonpath: 值 value, jsonpath 表达式, 数据依赖 response 数据集
```

#### assert

1: 常规断言：

与正常 assert 的语法格式一致，但比较值受约束；

比较直从 response 数据集进行取值， 并且以 pm.response.get('') 开始取值，
后面可以继续 get() 方法，也可以使用其他方法，但前提是 python 可执行代码，并且为了避免引号问题，断言脚本请使用单引号处理,
E.g:

str:

```yaml
assert: assert xxx 条件 pm.response.get('xxx'), '错误说明'
```

list:

```yaml
assert:
  - assert xxx 条件 pm.response.get('xxx')
  - assert xxx 条件 pm.response.get('xxx').get('xxx'), '错误说明'
```

2: jsonpath 断言:

使用 jsonpath 从 response 数据集进行取值比较

```yaml
assert:
  - check: 断言说明 / 错误信息, str / None，为空时，将展示内部定义信息
    value: 想要进行比较的值, Any
    type: 断言类型，str
    jsonpath: jsonpath 表达式, 数据依赖用例的请求返回数据集
```

3: sql 断言:

使用 jsonpath 从 sql 查询结果中取值比较

```yaml
assert:
  - check: 断言说明 / 错误信息, str / None，为空时，将展示内部定义信息
    value: 想要进行比较的值, Any
    type: 断言类型，str
    sql: 执行 sql 查询，str
    jsonpath: jsonpath 表达式, 数据依赖 sql 查询结果
```

### 断言类型说明

- eq: 预期结果与实际结果相等
- not_eq: 预期结果不等于实际结果
- gt: 预期结果大于实际结果
- ge: 预期结果大于等于实际结果
- lt: 预期结果小于实际结果
- le: 预期结果小于等于实际结果
- str_eq: 预期结果和实际结果字符串相等
- len_eq: 预期结果长度等于实际结果
- not_len_eq: 预期结果长度不等于实际结果
- len_lt: 预期结果长度小于实际结果
- len_le: 预期结果长度小于等于实际结果
- len_gt: 预期结果长度大于实际结果
- len_ge: 预期结果长度大于等于实际结果
- contains: 预期结果内容包含在实际结果中
- not contains: 预期结果内容不包含在实际结果中
- startswith: 实际结果的开头是预期结果
- endswith: 实际结果的结尾是预期结果

### 变量和hooks说明

#### 1. 变量

变量除了在用例数据中进行提取定义外，还支持进行手动定义

- 全局变量：仅在 data 目录下的 global_vars.yaml 文件中以键值对形式进行定义，请参考文件中示例
- 环境变量：在测试用例依赖的环境文件中以键值对的形式进行定义，请参考文件中示例
- 缓存变量：可以间接的通过 hook 函数定义，例如在 hook 方法中调用缓存变量写入方法实现定义

#### 2. hooks

仅在 data 目录下的 hooks.py 文件中定义，根据定义结构在用例数据文件中使用，可参考文件中示例

### 变量表达式

变量和 hooks 开头请遵循规则: a-zA-Z_

- 普通变量：测试用例全局可用

   ```text
   ${var} 或 $var
   ```

- 关联测试用例变量：只在测试用例中含有关联测试用例并需要引用关联测试用例设置的变量时，使用此方式

   ```text
   ^{var} 或 ^var
   ```

- hooks：仅在测试用例前后置 hooks 参数下配置时生效

   ```text
   ${func()}
   ```

### 用例中的变量替换

#### 普通变量：

请求数据解析时，寻找变量顺序为： cache > env > global，找到变量自动替换数据，未找到抛出异常

- env：在当前测试用例数据所调用的测试环境文件中进行持久化写入，键值不会重复，新值覆盖旧值
- global: 在全局变量文件中进行持久化写入，键值不会重复，新值覆盖旧值
- cache：写入当前指定运行的测试用例目录下所有用例运行过程的内存中，不会持久化，运行结束后自动清除

###### 温馨提示: 变量持久化写入会冲刷掉手写注释内容

#### 关联测试用例变量：

关联测试用例执行后，在 cache 变量中寻找，找到变量自动替换数据，未找到抛出异常

- cache: 默认仅使用 cache 存储变量，需在请求前置中关联测试用例，当前测试用例执行后自动删除

### jsonpath 取值范围

又称 response 数据集, 根结构如下（可在 send_request.py 文件中查看）：

```json
{
  "url": "请求连接",
  "status_code": "请求状态码",
  "elapsed": "请求耗时",
  "headers": "请求头",
  "cookies": "请求 cookies",
  "json": "请求返回 json",
  "content": "请求返回内容",
  "text": "请求返回文本",
  "stat": {
    "execute_time": "请求执行时间"
  }
}
```

## 测试用例数据文件创建

1. 使用 cli 程序自动导入
2. 根据数据结构及参数说明，手动编写测试用例数据文件

## 测试用例创建

1. 通过 cli 程序自动生成测试用例
2. 根据数据结构及参数说明，手动编写测试用例

## cli 程序使用说明

1. 在 fastpt/ 目录下打开终端
   ```shell
    cd fastpt
    ```
2. 查看 cli 程序使用帮助:

    ```shell
    python cli.py --help
    ```

3. 根据帮助说明, 进行其他操作

## 🚀 如何运行测试

运行 run.py 文件即可, 详细参数说明请查看 run.py 文件

## 🔍 如何查看测试报告

测试执行完毕后到 report 文件夹下查看

## ❓ 问题相关

### 1: 为什么没有想要的日志内容

日志内容需要手动写入, 详细示例demo中几乎都有体现, 请自行查看

### 2: 为什么没有测试报告

- html：自动生成，检查 run 参数是否开启 html 报告创建, 默认开启

- yaml：自动生成，用于测试结果统计

- ~~excel：当前 release 版本已不适用~~

- [allure](https://www.yuque.com/poloyy/python/aiqlmi)：自动生成, 默认开启并自动打开浏览器访问, 前提已正确安装 allure 程序

