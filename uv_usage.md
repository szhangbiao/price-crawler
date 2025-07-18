# UV 常用命令

```bash
    uv python list # 列出uv支持的python版本
    uv python install cpythonXXX # 安装某个python版本
    uv run -p XXX xxx.py # 使用特定版本python运行xxx.py
    uv run -p XXX python # 运行特定版本python交互界面
    uv run xxx.py # 使用系统python或当前的虚拟环境运行xxx.py
    uv init # 创建或初始化工程
    uv tree # 打印依赖树
    uv remove xxx # 删除依赖
    uv build # 编译工程
```
