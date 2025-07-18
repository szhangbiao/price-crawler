# 项目规范 (Project Rules)

## 1. 代码风格与格式

### 1.1 Python 代码风格

-   遵循 PEP 8 规范
-   使用 4 个空格进行缩进，不使用制表符
-   行长度不超过 100 个字符
-   函数和类之间空两行，类中的方法之间空一行
-   使用有意义的变量名和函数名，采用小写字母和下划线命名法（snake_case）
-   所有公共函数和方法必须包含参数和返回值的类型注解
-   使用Python内置的typing模块进行类型注解
-   复杂类型使用类型别名（TypeAlias）提高可读性
-   示例：
    ```python
    from typing import List, Dict, Optional, Union
    
    def process_data(data: List[Dict[str, Union[str, int]]], filter_empty: bool = False) -> Optional[Dict[str, int]]:
        """处理数据函数
        
        Args:
            data: 要处理的数据列表
            filter_empty: 是否过滤空值
            
        Returns:
            处理后的数据字典，如果处理失败则返回None
        """
    ```
-   导入顺序必须严格遵循：
    1. 标准库导入
    2. 空行
    3. 第三方库导入
    4. 空行
    5. 本地模块导入
-   每个分组内部按字母顺序排序
-   同一分组内，先导入模块，再导入from语句
-   本地模块导入时，相对导入（以.开头）应放在绝对导入之前
-   示例：
    ```python
    # 标准库导入
    import os
    import sys
    from datetime import datetime
    
    # 第三方库导入
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    
    # 本地模块导入
    from .utils import helper
    from config import settings
    ```

### 1.2 文件格式

-   所有 Python 文件使用 UTF-8 编码
-   文件开头添加 shebang 行（对于可执行脚本）：
    ```python
    #!/usr/bin/env python
    ```
-   不再需要添加编码声明（# -*- coding: utf-8 -*-），Python 3默认使用UTF-8
-   每个文件末尾保留一个空行

### 1.3 注释规范

-   每个模块、类和函数都应有文档字符串（docstring）
-   模块级文档字符串应描述模块的功能和用途
-   函数文档字符串应包含参数、返回值和异常说明
-   文档字符串必须以句点结尾
-   模块级文档字符串应简洁描述模块功能，以句点结尾
-   函数文档字符串中的Args、Returns、Raises等部分不需要句点结尾，但描述文本需要句点结尾
-   使用 Google 风格的文档字符串格式：

    ```python
    def function(param1, param2):
        """函数描述。

        Args:
            param1: 参数1的描述。
            param2: 参数2的描述。

        Returns:
            返回值的描述。

        Raises:
            异常类型: 异常描述。
        """
    ```

## 2. 项目结构

### 2.1 目录结构

-   保持项目结构清晰，遵循以下布局：
    ```
    ├── .python-version    # Python版本信息
    ├── .venv/             # 虚拟环境目录
    ├── .env               # 环境变量配置文件（API密钥等）
    ├── data/              # 数据存储目录
    ├── logs/              # 日志文件目录
    ├── tests/             # 测试代码目录
    ├── gold/              # 黄金价格数据获取模块
    ├── stock/             # 股票指数数据获取模块
    ├── exchange_rate/     # 汇率数据获取模块
    ├── storage/           # 数据存储模块
    ├── utils/             # 工具模块
    ├── README.md          # 项目说明文档
    ├── main.py            # 主程序代码
    ├── pyproject.toml     # 项目配置和依赖信息
    └── uv.lock            # 依赖锁定文件
    ```

### 2.2 模块化原则

-   每个功能模块应该是独立的，有明确的职责
-   相关功能应组织在同一个模块或包中
-   避免循环导入
-   模块目录必须包含 `__init__.py` 文件
-   模块化设计：
    -   `gold/`：负责从多个来源获取黄金价格数据
        -   `gold_crawler.py`：统一接口，整合多个数据源
        -   `cngold_crawler.py`：金投网爬虫
        -   `goldprice_crawler.py`：GoldPrice.org爬虫
        -   `juhe_api.py`：聚合数据API调用
    -   `stock/`：负责获取股票指数数据
    -   `exchange_rate/`：负责获取汇率数据
    -   `storage/`：负责数据存储
        -   `base.py`：存储基类定义
        -   `csv_storage.py`：CSV存储实现
    -   `utils/`：工具模块
        -   `scheduler.py`：任务调度模块，提供交易时间判断和数据获取调度功能

## 3. 编程实践

### 3.1 错误处理

-   使用 try-except 块捕获和处理异常
-   避免捕获过于宽泛的异常（如 `except Exception:`），除非有明确的错误恢复策略
-   使用日志记录异常，而不是简单地打印错误信息
-   优先使用更通用的异常类型，如OSError而不是IOError、FileNotFoundError或PermissionError
-   异常处理示例：
    ```python
    try:
        with open(file_path, 'r') as f:
            data = f.read()
    except OSError as e:
        logger.error("读取文件出错: %s", e)
    ```

### 3.2 日志记录

-   使用 Python 的 logging 模块进行日志记录
-   为每个模块创建独立的 logger
-   使用适当的日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
-   日志消息应该清晰、具体，包含足够的上下文信息

### 3.3 配置管理

-   使用 .env 文件和 python-dotenv 库管理环境变量和配置
-   敏感信息（如 API 密钥）不应硬编码在源代码中
-   配置参数应集中管理，便于修改和维护

### 3.4 API 调用

-   为 API 请求设置超时参数
-   实现错误重试机制，特别是对于不稳定的外部 API
-   使用备用数据源或方法，以防主要 API 调用失败

## 4. 依赖管理

### 4.1 依赖声明

-   在 pyproject.toml 中声明项目依赖
-   指定依赖的版本范围，避免使用过于宽松的版本约束
-   使用 uv 工具管理依赖和虚拟环境

### 4.2 使用 uv 管理依赖

-   使用 uv 替代 pip 进行包管理，提供更快的安装速度和更好的依赖解析
-   安装依赖：`uv pip install -r requirements.txt` 或 `uv pip install -e .`
-   添加新依赖：`uv pip install <package_name>`
-   更新依赖锁定文件：`uv pip compile pyproject.toml -o uv.lock`
-   使用 `uv.toml` 配置 uv 行为

### 4.3 虚拟环境

-   使用 uv 创建和管理虚拟环境：`uv venv`
-   始终在虚拟环境中开发和运行项目
-   不要将虚拟环境目录（.venv/）提交到版本控制系统

## 5. 数据处理

### 5.1 数据存储

-   使用 pandas 进行数据处理和分析
-   将数据保存为 CSV 格式，便于查看和分析
-   实现数据备份机制，防止数据丢失

### 5.2 数据验证

-   对外部获取的数据进行验证和清洗
-   处理缺失值和异常值
-   记录数据处理过程中的异常情况

## 6. 测试与质量保证

### 6.1 单元测试

-   使用 pytest 框架编写单元测试
-   为核心功能编写测试用例
-   模拟外部 API 响应，避免在测试中发送真实请求

### 6.2 代码质量工具

-   使用 ruff 进行代码检查和格式化
    - 运行 `ruff check .` 检查代码问题
    - 运行 `ruff check . --fix` 自动修复可自动修复的问题
    - 运行 `ruff format .` 格式化代码
    - 配置在 `pyproject.toml` 中的 `[tool.ruff]` 部分
-   使用 pylint 进行更严格的代码质量检查
    - 运行 `pylint <module_name>` 检查特定模块
    - 配置在 `.pylintrc` 文件中
-   使用 `pre-commit` 在提交代码前自动运行检查
    - 配置在 `.pre-commit-config.yaml` 文件中
    - 安装钩子：`pre-commit install`
    - 手动运行：`pre-commit run --all-files`
-   代码质量标准：
    - 遵循 PEP 8 编码规范
    - 保持函数和方法的复杂度低（McCabe复杂度<10）
    - 避免重复代码（DRY原则）
    - 保持高测试覆盖率
-   在开发过程中，定期运行`ruff check .`检查代码问题
-   对于新编写的代码，确保通过所有启用的ruff规则检查
-   在提交代码前，确保运行`ruff format .`格式化代码

### 6.3 ruff规则说明

项目启用的主要ruff规则集及其含义：

- E: pycodestyle错误，基本的代码风格问题
- F: Pyflakes，检测未使用的导入、变量等
- B: flake8-bugbear，检测潜在的bug和设计问题
- I: isort，导入排序
- UP: pyupgrade，使用更现代的Python语法
- N: pep8-naming，命名规范
- ANN: flake8-annotations，类型注解检查
- D: pydocstyle，文档字符串规范

常见问题及解决方法：

1. ANN001/ANN201: 缺少函数参数/返回值类型注解
   - 解决：为所有公共函数添加参数和返回值的类型注解

2. I001: 导入未排序或格式不正确
   - 解决：按照标准库、第三方库、本地模块的顺序组织导入，并在各组之间添加空行

3. UP024: 使用OSError替代IOError等
   - 解决：在异常处理中使用OSError替代IOError、FileNotFoundError等

4. D400: 文档字符串首字母应大写
   - 解决：确保所有文档字符串以大写字母开头

5. D415: 文档字符串应以句点结尾
   - 解决：确保所有文档字符串以句点结尾

## 7. 版本控制

### 7.1 Git 使用规范

-   使用有意义的提交消息
-   遵循语义化版本控制（Semantic Versioning）
-   使用分支进行功能开发和 bug 修复

### 7.2 敏感信息保护

-   使用 .gitignore 文件排除敏感信息和临时文件
-   不要将 .env 文件、API 密钥或其他敏感信息提交到版本控制系统
-   考虑使用环境变量或安全的密钥管理服务存储敏感信息
