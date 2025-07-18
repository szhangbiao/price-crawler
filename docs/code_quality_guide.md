# Python 代码质量与审查指南

> 本文档提供了项目中使用的代码质量工具的详细说明、配置方法和最佳实践，旨在帮助开发者编写高质量、一致性强的 Python 代码。

## 目录

-   [代码质量工具概述](#代码质量工具概述)
-   [Ruff](#ruff)
-   [Pylint](#pylint)
-   [Pre-commit](#pre-commit)
-   [代码质量标准](#代码质量标准)
-   [常见问题与解决方案](#常见问题与解决方案)

## 代码质量工具概述

本项目使用以下工具来保证代码质量：

| 工具       | 主要功能         | 优势                       |
| ---------- | ---------------- | -------------------------- |
| Ruff       | 代码检查与格式化 | 速度快、规则全面、兼容性好 |
| Pylint     | 深度静态代码分析 | 更严格的检查、更全面的报告 |
| Pre-commit | 提交前自动检查   | 防止不合规代码提交到仓库   |

## Ruff

Ruff 是一个快速的 Python 代码检查和格式化工具，由 Rust 编写，速度比传统工具快 10-100 倍。

### 安装

```bash
uv pip install ruff
```

### 基本使用

```bash
# 检查代码问题
ruff check .

# 自动修复可修复的问题
ruff check --fix .

# 格式化代码
ruff format .

# 使用UV运行Ruff
uv run -m ruff check .
uv run -m ruff format .
```

### 配置

项目中的 Ruff 配置位于`pyproject.toml`文件的`[tool.ruff]`部分：

```toml
[tool.ruff]
line-length = 200

# 设置 Python 版本
target-version = "py312"

# 排除目录
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

# Lint 配置
[tool.ruff.lint]
# 启用规则集
select = [
    "E",   # pycodestyle 错误
    "F",   # Pyflakes
    "B",   # flake8-bugbear
    "I",   # isort
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "ANN", # flake8-annotations
    "D",   # pydocstyle
]

# 忽略特定规则
ignore = [
    "D203",    # one-blank-line-before-class
    "D212",    # multi-line-summary-first-line
]

# 在特定文件中忽略规则
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401", "D104"]
"test_*.py" = ["ANN", "D"]

# pydocstyle 配置
[tool.ruff.lint.pydocstyle]
convention = "google"  # 使用 Google 风格的文档字符串

# isort 配置
[tool.ruff.lint.isort]
known-first-party = ["stock", "gold", "exchange_rate", "storage", "utils"]
```

### Ruff 规则集说明

-   **E**: pycodestyle 错误（PEP 8 编码规范）
-   **F**: pyflakes（检测逻辑错误）
-   **B**: flake8-bugbear（检测潜在 bug）
-   **I**: isort（导入排序）
-   **UP**: pyupgrade（使用更现代的 Python 语法）
-   **N**: pep8-naming（命名规范）
-   **ANN**: flake8-annotations（类型注解检查）
-   **D**: pydocstyle（文档字符串规范）

## Pylint

Pylint 是一个更严格的 Python 代码分析工具，能够检查代码风格、错误和复杂度。

### 安装

```bash
uv pip install pylint
```

### 基本使用

```bash
# 检查单个模块
pylint gold

# 检查多个模块
pylint gold stock exchange_rate

# 生成详细报告
pylint --output-format=colorized gold
```

### 配置

项目中的 Pylint 配置位于`.pylintrc`文件：

```ini
[MASTER]
init-hook='import sys; sys.path.append("D:/booslink/price-crawler")'
```

这是一个最小化的配置，主要用于设置 Python 模块导入路径。在实际项目中，你可以根据需要添加更多配置，例如：

```ini
[MASTER]
# 忽略的目录和文件
ignore=.git,__pycache__,.venv,build,dist

# 使用多进程加速检查
jobs=4

# 设置Python模块导入路径
init-hook='import sys; sys.path.append("D:/booslink/price-crawler")'

[MESSAGES CONTROL]
# 禁用的检查
disable=
    C0111, # 缺少文档字符串（由ruff的pydocstyle处理）
    C0103, # 命名不符合规范（由ruff的pep8-naming处理）
    W0511, # TODO/FIXME注释
    R0903, # 方法太少
    R0913, # 参数太多

[REPORTS]
# 评分输出格式
output-format=colorized

[FORMAT]
# 最大行长度
max-line-length=200

[DESIGN]
# 最大允许的方法复杂度
max-complexity=10
```

### Pylint 评分说明

Pylint 会给代码打分（满分 10 分），评分基于以下几个方面：

-   **代码风格**: 命名规范、空格使用、注释等
-   **代码结构**: 类设计、函数设计、模块组织等
-   **代码错误**: 潜在的 bug、逻辑错误等
-   **代码复杂度**: 函数复杂度、嵌套层级等
-   **代码重复**: 重复代码检测

## Pre-commit

Pre-commit 是一个用于管理和维护 Git pre-commit 钩子的框架，可以在代码提交前自动运行检查工具。

### 安装

```bash
uv pip install pre-commit
pre-commit install
```

### 配置

项目中的 Pre-commit 配置位于`.pre-commit-config.yaml`文件：

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.12.4 # 使用最新版本
  hooks:
      # 运行 linter
      - id: ruff-check
        args: [--fix]
      # 运行 formatter
      - id: ruff-format
```

这是一个最小化的配置，只包含了 Ruff 的检查和格式化钩子。在实际项目中，你可以根据需要添加更多钩子，例如：

```yaml
# 添加Ruff检查和格式化
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.12.4
  hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

# 添加常用的Git钩子
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
      - id: debug-statements
      - id: check-merge-conflict
```

### 使用方法

```bash
# 手动运行所有检查
pre-commit run --all-files

# 运行特定钩子
pre-commit run ruff --all-files

# 跳过钩子（紧急情况）
git commit -m "紧急修复" --no-verify
```

## 代码质量标准

### 复杂度控制

-   **函数复杂度**: McCabe 复杂度不超过 10
-   **函数长度**: 不超过 50 行
-   **模块长度**: 不超过 500 行
-   **嵌套层级**: 不超过 4 层

### 命名规范

-   **模块名**: 小写，单词间用下划线分隔（如`gold_crawler.py`）
-   **类名**: 驼峰命名法（如`GoldCrawler`）
-   **函数名/方法名**: 小写，单词间用下划线分隔（如`fetch_gold_price`）
-   **变量名**: 小写，单词间用下划线分隔（如`gold_price`）
-   **常量名**: 全大写，单词间用下划线分隔（如`MAX_RETRY_COUNT`）

### 注释规范

-   **模块注释**: 每个模块开头应有文档字符串，说明模块功能
-   **类注释**: 每个类应有文档字符串，说明类的功能和用途
-   **函数注释**: 每个公共函数应有文档字符串，包含参数、返回值和异常说明
-   **复杂逻辑注释**: 对于复杂的代码逻辑，应添加行内注释说明

## 常见问题与解决方案

### 1. Ruff 和 Pylint 规则冲突

**问题**: Ruff 和 Pylint 可能对同一段代码给出不同的建议。

**解决方案**:

-   优先遵循 Ruff 的建议，因为它更新更频繁
-   在`.pylintrc`中禁用与 Ruff 重复的检查
-   对于特定文件，可以使用行内注释禁用特定检查：
    ```python
    # pylint: disable=invalid-name
    # ruff: noqa: N803
    ```

### 2. 处理第三方库导致的警告

**问题**: 第三方库可能导致导入或使用相关的警告。

**解决方案**:

-   在`pyproject.toml`的`[tool.ruff.per-file-ignores]`中添加特定规则
-   对于特定导入，使用行内注释：
    ```python
    import some_problematic_module  # noqa: F401
    ```

### 3. 提高代码质量分数

**问题**: Pylint 评分较低，需要提高代码质量。

**解决方案**:

-   运行`pylint --output-format=colorized <module>`查看详细报告
-   优先修复错误(E)和警告(W)类别的问题
-   重构复杂函数，降低复杂度
-   添加缺失的文档字符串
-   修复命名规范问题

### 4. Pre-commit 钩子运行缓慢

**问题**: Pre-commit 钩子运行时间过长，影响开发效率。

**解决方案**:

-   使用`pre-commit run --hook-stage manual ruff`只运行特定钩子
-   配置钩子只检查修改的文件
-   在开发过程中使用编辑器集成的 Ruff 插件，提前发现问题

## 项目特定的代码质量实践

### 模块化设计

本项目采用模块化设计，每个模块有明确的职责：

-   `gold/`: 负责从多个来源获取黄金价格数据
-   `stock/`: 负责获取股票指数数据
-   `exchange_rate/`: 负责获取汇率数据
-   `storage/`: 负责数据存储
-   `utils/`: 工具模块，提供共享功能

在编写代码时，应遵循以下原则：

1. 保持模块间的低耦合度
2. 确保每个模块内的高内聚性
3. 避免循环依赖
4. 使用明确的接口进行模块间通信

### 测试最佳实践

本项目采用多层次的测试策略，确保代码质量和功能正确性：

#### 单元测试

单元测试应该关注最小可测试单元（通常是函数或方法）的行为：

```python
# tests/test_gold_validator.py
import pytest
from gold.validator import validate_gold_price

def test_validate_gold_price_valid_data():
    """测试有效的黄金价格数据验证。"""
    data = {"price": "1800.50", "timestamp": "2023-01-01T12:00:00Z", "currency": "USD"}
    validated = validate_gold_price(data)
    assert validated["price"] == 1800.50
    assert validated["timestamp"] == "2023-01-01T12:00:00Z"
    assert validated["currency"] == "USD"

def test_validate_gold_price_missing_field():
    """测试缺少必要字段的情况。"""
    data = {"price": "1800.50", "timestamp": "2023-01-01T12:00:00Z"}
    with pytest.raises(ValueError) as excinfo:
        validate_gold_price(data)
    assert "缺少必要字段: currency" in str(excinfo.value)

def test_validate_gold_price_invalid_price():
    """测试无效价格值的情况。"""
    data = {"price": "invalid", "timestamp": "2023-01-01T12:00:00Z", "currency": "USD"}
    with pytest.raises(ValueError) as excinfo:
        validate_gold_price(data)
    assert "无法转换价格为数字" in str(excinfo.value)
```

#### 集成测试

集成测试应该关注模块间的交互：

```python
# tests/integration/test_gold_storage.py
import pytest
from gold.fetcher import fetch_gold_price
from storage.database import store_gold_price

@pytest.mark.integration
def test_fetch_and_store_gold_price():
    """测试获取黄金价格并存储到数据库的完整流程。"""
    # 设置测试环境（如使用测试数据库）
    setup_test_db()

    try:
        # 执行获取和存储操作
        price_data = fetch_gold_price("source_a")
        result = store_gold_price(price_data)

        # 验证结果
        assert result.success is True
        assert result.record_id is not None

        # 从数据库验证数据
        stored_data = get_from_test_db(result.record_id)
        assert stored_data["price"] == price_data["price"]
        assert stored_data["timestamp"] == price_data["timestamp"]
    finally:
        # 清理测试环境
        teardown_test_db()
```

#### 模拟和打桩

对于依赖外部服务的测试，应使用模拟（mock）和打桩（stub）技术：

```python
# tests/test_gold_fetcher.py
import pytest
from unittest.mock import patch, MagicMock
from gold.fetcher import fetch_gold_price

def test_fetch_gold_price_with_mock():
    """使用模拟对象测试黄金价格获取功能。"""
    # 创建模拟的HTTP响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"price": "1800.50", "timestamp": "2023-01-01T12:00:00Z", "currency": "USD"}
    }

    # 使用patch替换requests.get函数
    with patch("requests.get", return_value=mock_response):
        result = fetch_gold_price("source_a")

        # 验证结果
        assert result["price"] == "1800.50"
        assert result["timestamp"] == "2023-01-01T12:00:00Z"
        assert result["currency"] == "USD"
```

#### 测试覆盖率

使用`pytest-cov`插件监控测试覆盖率：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html tests/

# 使用UV运行测试并生成覆盖率报告
uv run -m pytest --cov=. --cov-report=html tests/
```

目标是达到至少 80%的代码覆盖率，重点关注核心业务逻辑的覆盖。

### 错误处理与日志记录

项目中的错误处理应遵循以下规范：

1. 使用具体的异常类型，而非通用的`Exception`
2. 在适当的层级处理异常
3. 记录足够的上下文信息

日志记录示例：

```python
import logging

logger = logging.getLogger(__name__)

try:
    # 尝试执行可能失败的操作
    result = api_client.fetch_data()
except ConnectionError as e:
    logger.error("连接API失败: %s", str(e))
    # 使用备用数据源或返回适当的错误信息
except ValueError as e:
    logger.warning("数据格式错误: %s", str(e))
    # 尝试修复或使用默认值
except Exception as e:
    # 只在最后才捕获通用异常，并记录详细信息
    logger.exception("未预期的错误: %s", str(e))
    raise
```

### 数据验证与清洗

从外部来源获取的数据应进行验证和清洗：

1. 检查数据完整性和有效性
2. 处理缺失值和异常值
3. 转换数据格式为统一标准

示例：

```python
def validate_gold_price(price_data):
    """验证黄金价格数据。

    Args:
        price_data: 原始价格数据

    Returns:
        验证后的价格数据

    Raises:
        ValueError: 当数据无效时
    """
    if not price_data:
        raise ValueError("空的价格数据")

    # 检查必要字段
    required_fields = ["price", "timestamp", "currency"]
    for field in required_fields:
        if field not in price_data:
            raise ValueError(f"缺少必要字段: {field}")

    # 验证价格值
    try:
        price = float(price_data["price"])
        if price <= 0:
            raise ValueError(f"无效的价格值: {price}")
        price_data["price"] = price  # 确保是浮点数
    except (ValueError, TypeError):
        raise ValueError(f"无法转换价格为数字: {price_data['price']}")

    return price_data
```

## 总结

遵循本文档中的代码质量标准和工具使用指南，可以帮助团队成员编写高质量、一致性强的 Python 代码。定期运行代码质量检查工具，及时修复发现的问题，将有助于保持代码库的健康状态和可维护性。

记住，代码质量工具是辅助手段，不是目的。最终目标是编写清晰、可读、可维护的代码，工具只是帮助我们达到这个目标的手段。

## 代码审查最佳实践

代码审查是确保代码质量的重要环节。以下是一些代码审查的最佳实践：

### 审查清单

在进行代码审查时，可以参考以下清单：

#### 功能性

-   代码是否实现了预期功能？
-   是否处理了边缘情况和异常情况？
-   是否有足够的错误处理？

#### 可读性和可维护性

-   命名是否清晰、一致且有意义？
-   代码结构是否清晰？
-   是否有必要的注释和文档？
-   是否遵循了项目的代码风格指南？

#### 性能和效率

-   算法和数据结构的选择是否合适？
-   是否有潜在的性能问题？
-   是否有不必要的计算或操作？

#### 安全性

-   是否存在安全漏洞？
-   敏感数据是否得到适当保护？
-   用户输入是否得到验证和清洗？

#### 测试

-   是否有足够的测试覆盖率？
-   测试是否覆盖了关键路径和边缘情况？

### 审查流程

1. **自我审查**：提交代码前，开发者应该自我审查代码，确保代码符合项目标准。

2. **工具辅助审查**：使用 Ruff、Pylint 等工具进行自动化检查，解决工具发现的问题。

3. **同行审查**：由团队其他成员进行代码审查，提供反馈和建议。

4. **修改和再审查**：根据反馈修改代码，必要时进行再次审查。

### 审查注意事项

-   关注代码的整体设计和结构，而不仅仅是语法和格式。
-   提供具体、建设性的反馈，而不是模糊的批评。
-   区分必须修改的问题和可选的改进建议。
-   保持开放的心态，愿意接受和提供反馈。
-   及时进行审查，避免延误开发进度。

### 使用 Git 提交规范

良好的 Git 提交消息有助于代码审查和项目维护。建议使用以下格式：

```
<类型>(<范围>): <简短描述>

<详细描述>

<关闭的问题>
```

类型可以是：

-   `feat`：新功能
-   `fix`：修复 bug
-   `docs`：文档更新
-   `style`：代码风格更改（不影响代码功能）
-   `refactor`：代码重构
-   `perf`：性能优化
-   `test`：添加或修改测试
-   `chore`：构建过程或辅助工具的变动

示例：

```
feat(gold): 添加黄金价格数据验证功能

- 添加对价格数据的完整性检查
- 添加对价格值的有效性验证
- 添加对时间戳格式的验证

Closes #123
```

## 参考资源

-   [Ruff 官方文档](https://docs.astral.sh/ruff/)
-   [Pylint 官方文档](https://pylint.pycqa.org/)
-   [Pre-commit 官方文档](https://pre-commit.com/)
-   [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)
-   [PEP 8 -- Python 代码风格指南](https://peps.python.org/pep-0008/)
-   [Conventional Commits](https://www.conventionalcommits.org/)
-   [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/)
