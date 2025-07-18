#!/usr/bin/env python

"""
数据存储模块.

该模块定义了数据存储的基类和具体实现，用于处理数据的加载和保存。
"""

from storage.base import Storage
from storage.csv_storage import CsvStorage

__all__ = ["Storage", "CsvStorage"]
