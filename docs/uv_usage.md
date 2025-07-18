# UV 常用命令

> UV 是一个快速的 Python 包管理器和解释器运行器，由 Rust 编写，旨在替代传统的 pip、venv 等工具，提供更快的依赖解析和安装速度。

## 安装 UV

```bash
    # Windows (PowerShell)
    curl -sSf https://astral.sh/uv/install.ps1 | powershell
    
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Python 版本管理

```bash
    uv python list # 列出uv支持的python版本
    uv python install cpythonXXX # 安装某个python版本
    uv python remove cpythonXXX # 删除某个python版本
    uv python default cpythonXXX # 设置默认python版本
    uv python which # 显示当前使用的python解释器路径
```

## 虚拟环境管理

```bash
    uv venv # 在当前目录创建虚拟环境(.venv)
    uv venv -p cpythonXXX # 使用指定版本python创建虚拟环境
    uv venv /path/to/venv # 在指定路径创建虚拟环境
    uv venv --seed # 创建虚拟环境并安装pyproject.toml中的依赖
    uv venv --system-site-packages # 创建可访问系统包的虚拟环境
```

## 依赖管理

```bash
    uv pip install package_name # 安装依赖包
    uv pip install package_name==1.0.0 # 安装特定版本依赖包
    uv pip install -r requirements.txt # 从requirements.txt安装依赖
    uv pip install -e . # 以可编辑模式安装当前项目
    uv pip install --no-deps package_name # 安装包但不安装其依赖
    uv pip install --upgrade package_name # 升级已安装的包
    uv pip uninstall package_name # 卸载依赖包
    uv pip freeze # 列出已安装的依赖包及版本
    uv pip list # 列出已安装的依赖包
    uv pip show package_name # 显示包的详细信息
```

## 项目管理

```bash
    uv init # 创建或初始化工程
    uv run xxx.py # 使用系统python或当前的虚拟环境运行xxx.py
    uv run -p XXX xxx.py # 使用特定版本python运行xxx.py
    uv run -p XXX python # 运行特定版本python交互界面
    uv run -m module_name # 运行指定模块
    uv tree # 打印依赖树
    uv tree --why package_name # 显示为什么需要某个包
    uv remove xxx # 删除依赖
    uv build # 编译工程
    uv lock # 生成或更新uv.lock文件
    uv sync # 同步安装uv.lock中的依赖
    uv cache clean # 清理缓存
```

## 开发工具集成

```bash
    uv pip install pytest # 安装测试框架
    uv run -m pytest # 运行测试
    uv pip install ruff # 安装代码检查工具
    uv run -m ruff check . # 检查代码问题
    uv run -m ruff format . # 格式化代码
    uv pip install pre-commit # 安装pre-commit钩子
    uv run -m pre_commit install # 安装git pre-commit钩子
```

## 高级用法

```bash
    uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple package_name # 使用指定镜像源安装包
    uv pip install --no-binary :all: package_name # 从源代码安装包
    uv pip install --only-binary :all: package_name # 只使用二进制包安装
    uv pip install --platform win_amd64 package_name # 为特定平台安装包
    uv pip install --python-version 3.10 package_name # 为特定Python版本安装包
```

## 环境变量配置

```bash
    # 设置镜像源
    $env:UV_INDEX_URL = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    # 设置缓存目录
    $env:UV_CACHE_DIR = "D:\path\to\cache"
    
    # 设置离线模式
    $env:UV_OFFLINE = "1"
    
    # 设置日志级别
    $env:UV_LOG_LEVEL = "debug"
```

## 常见问题解决

### 1. 安装包失败

```bash
    # 尝试使用国内镜像源
    uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple package_name
    
    # 清理缓存后重试
    uv cache clean
    uv pip install package_name
    
    # 查看详细日志
    $env:UV_LOG_LEVEL = "debug"
    uv pip install package_name
```

### 2. 虚拟环境问题

```bash
    # 重新创建虚拟环境
    Remove-Item -Recurse -Force .venv
    uv venv
    
    # 检查虚拟环境Python版本
    .venv\Scripts\python --version
```

### 3. 依赖冲突

```bash
    # 查看依赖树，找出冲突
    uv tree
    
    # 尝试指定版本安装
    uv pip install package_name==specific_version
    
    # 使用--no-deps选项安装特定包
    uv pip install --no-deps package_name
```

### 4. 与现有工具集成

```bash
    # 在Poetry项目中使用UV
    uv pip install -e .
    
    # 从requirements.txt安装依赖
    uv pip install -r requirements.txt
    
    # 生成requirements.txt
    uv pip freeze > requirements.txt
```

## 参考资源

- [UV 官方文档](https://github.com/astral-sh/uv)
- [UV vs pip 性能对比](https://astral.sh/blog/uv)
- [UV 常见问题解答](https://github.com/astral-sh/uv/blob/main/FAQ.md)
- [Astral 工具集](https://astral.sh/) - UV 的开发团队提供的其他工具，如 Ruff
