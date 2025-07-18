#!/usr/bin/env python
"""日志配置模块.

该模块提供了统一的日志配置功能，用于整个项目的日志记录。
"""

import logging
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# 日志目录
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保日志目录存在
os.makedirs(LOGS_DIR, exist_ok=True)


def get_logger(name: str, log_file: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """获取配置好的logger实例.
    
    Args:
        name: logger名称，通常使用__name__
        log_file: 日志文件名，如果不指定，则只输出到控制台
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的logger实例
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = LOGS_DIR / log_file
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 默认日志配置
def configure_basic_logging(log_file: str = "price_crawler.log", level: int = logging.INFO) -> None:
    """配置基本的日志设置.
    
    Args:
        log_file: 日志文件名
        level: 日志级别
    """
    log_path = LOGS_DIR / log_file
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8")
        ]
    )