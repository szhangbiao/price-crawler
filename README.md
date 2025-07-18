# price-crawler

使用 Python 实现黄金价格、汇率和 A 股大盘指数变动的监控程序

## 项目介绍

这是一个使用 Python 开发的实时监控工具，可以定期获取并记录黄金价格和 A 股大盘指数的变动情况。主要功能包括：

-   实时获取黄金价格数据
-   实时获取多个 A 股指数数据（上证指数、深证成指、创业板指）
-   将数据保存到 CSV 文件中，方便后续分析
-   在控制台实时显示价格变动情况

## 环境要求

-   Python 3.13+
-   依赖包：requests, pandas, python-dotenv

## 使用 uv 初始化项目的步骤

1. **初始化项目结构**

    ```bash
    uv init
    ```

    这个命令创建了基本的项目结构，包括`pyproject.toml`、`.python-version`和一个简单的`main.py`文件。

2. **同步项目依赖并创建虚拟环境**

    ```bash
    uv sync
    ```

    这个命令创建了`.venv`虚拟环境目录和`uv.lock`锁定文件。

3. **添加项目依赖**
    ```bash
    uv add requests pandas python-dotenv
    ```
    这个命令将 requests、pandas 和 python-dotenv 库添加到项目依赖中，并更新了`pyproject.toml`文件。

## 项目文件结构

```
├── .python-version    # Python版本信息
├── .venv/             # 虚拟环境目录
├── .env               # 环境变量配置文件（API密钥等）
├── .env.example       # 环境变量示例文件
├── .gitignore         # Git忽略文件配置
├── .pre-commit-config.yaml # pre-commit钩子配置
├── .pylintrc          # pylint配置文件
├── data/              # 数据存储目录
│   ├── gold_price_data.csv    # 黄金价格数据
│   ├── stock_indices_data.csv # 多个股指数据
│   └── exchange_rate_data.csv # 中美汇率数据
├── exchange_rate/     # 汇率数据获取模块
│   ├── __init__.py    # 模块初始化文件
│   └── exchange_rate_api.py # 汇率API调用实现
├── gold/              # 黄金价格数据获取模块
│   ├── __init__.py    # 模块初始化文件
│   ├── cngold_crawler.py # 金投网爬虫
│   ├── gold_crawler.py # 黄金价格爬虫统一接口
│   ├── goldprice_crawler.py # GoldPrice.org爬虫
│   └── juhe_api.py    # 聚合数据API调用
├── stock/             # 股票数据获取模块
│   ├── __init__.py    # 模块初始化文件
│   └── stock_indices.py # 股指数据获取实现
├── storage/           # 数据存储模块
│   ├── __init__.py    # 模块初始化文件
│   ├── base.py        # 存储基类定义
│   └── csv_storage.py # CSV存储实现
├── README.md          # 项目说明文档
├── main.py            # 主程序代码
├── utils/             # 工具模块
│   ├── __init__.py    # 模块初始化文件
│   └── scheduler.py   # 调度器模块
# 日志文件存储在 D:/booslink/logs/ 目录下
├── pyproject.toml     # 项目配置和依赖信息
├── uv.toml            # uv工具配置
└── uv_usage.md        # uv使用说明
```

## 安装与设置

本项目使用 uv 进行依赖管理，确保您已安装 uv 工具。

1. 克隆项目

```bash
git clone https://github.com/yourusername/price-crawler.git
cd price-crawler
```

2. 使用 uv 同步项目依赖并创建虚拟环境

```bash
uv sync
```

3. 配置 API 密钥

在项目根目录下创建或编辑`.env`文件，添加以下配置（可参考 `.env.example` 文件）：

```
# 聚合数据黄金价格API密钥
JUHE_GOLD_APPKEY=your_juhe_gold_appkey_here

# 聚合数据汇率换算API密钥
JUHE_EXCHANGE_RATE_APPKEY=your_juhe_exchange_rate_appkey_here
```

### 获取 API 密钥

-   **聚合数据黄金价格 API**：访问 [http://web.juhe.cn:8080/finance/gold/shgold](http://web.juhe.cn:8080/finance/gold/shgold) 注册并获取 APPKEY
-   **聚合数据汇率换算 API**：访问 [https://www.juhe.cn/docs/api/id/80](https://www.juhe.cn/docs/api/id/80) 注册并获取 APPKEY

> 注意：如果未配置 API 密钥或 API 调用失败，程序将按照金投网爬虫 → GoldPrice.org 爬虫 → 聚合数据 API → 模拟数据的顺序尝试获取数据

## 使用方法

1. 激活虚拟环境（Windows）

```bash
.venv\Scripts\activate
```

2. 运行监控程序

```bash
uv run main.py
```

3. 按`Ctrl+C`停止监控

## 数据存储

程序运行过程中会自动生成两个 CSV 文件：

-   `data/gold_price_data.csv`：存储黄金价格数据
-   `data/stock_indices_data.csv`：存储多个 A 股指数数据（上证指数、深证成指、创业板指）
-   `data/exchange_rate_data.csv`：存储中美汇率数据

数据目录会在程序首次运行时自动创建。

## 日志记录

程序运行日志会同时输出到控制台和 `D:/booslink/logs/price_crawler.log` 文件中，便于问题排查和监控。所有日志文件都存储在 `D:/booslink/logs/` 目录下。

## 自定义设置

您可以修改以下设置来自定义程序行为：

-   监控间隔：修改 `main.py` 中的 `intervals` 字典，可以为不同类型的数据设置不同的获取间隔
-   数据存储路径：修改 `main.py` 中的 `DATA_DIR` 常量
-   日志级别：修改 `logging.basicConfig()` 中的 `level` 参数
-   API 密钥：修改 `.env` 文件中的相应配置项
-   黄金价格数据源：默认会按照金投网爬虫 → GoldPrice.org 爬虫 → 聚合数据 API → 模拟数据的顺序尝试获取数据，您可以在 `gold/gold_crawler.py` 中修改这个顺序

## 代码最佳实践

本项目代码遵循以下最佳实践：

1. **模块化设计**：
    - 将功能分解为独立的模块，如 `gold_price.py`、`stock_indices.py` 和 `exchange_rate.py`
    - 每个模块负责特定的数据获取功能，便于维护和扩展
    - 主程序 `main.py` 只负责协调各模块功能和数据存储
2. **错误处理**：使用 try-except 捕获并记录可能的异常
3. **日志记录**：使用 logging 模块记录程序运行状态和错误信息
4. **配置管理**：使用常量定义配置项，便于集中管理
5. **数据持久化**：定期保存数据，并在程序异常退出时尝试保存已收集的数据
6. **代码文档**：为函数和模块添加详细的文档字符串
7. **单一职责原则**：每个模块和函数只负责一个特定的功能
8. **代码质量工具**：
    - 使用 ruff 进行代码检查和格式化
    - 使用 pylint 进行更严格的代码质量检查
    - 使用 pre-commit 钩子在提交前自动运行代码检查

### 代码质量检查

本项目使用以下工具确保代码质量：

1. **Ruff**：快速的 Python linter 和 formatter

    ```bash
    # 运行代码检查
    ruff check .

    # 运行代码格式化
    ruff format .
    ```

2. **Pylint**：更全面的 Python 代码分析工具

    ```bash
    # 运行pylint检查
    pylint main.py gold stock exchange_rate storage
    ```

3. **Pre-commit**：Git 提交前自动运行检查

    ```bash
    # 安装pre-commit钩子
    pre-commit install

    # 手动运行所有pre-commit钩子
    pre-commit run --all-files
    ```

## uv 工具的优势

uv 是一个非常高效的 Python 项目管理工具，它提供了类似于 Node.js 的 npm 或 Rust 的 Cargo 的体验。使用 uv 可以：

-   快速初始化项目结构
-   高效管理项目依赖
-   创建和管理虚拟环境
-   运行 Python 脚本

相比传统的 pip+venv 组合，uv 提供了更加集成和高效的工作流程，特别适合现代 Python 项目开发。

## 许可证

MIT
