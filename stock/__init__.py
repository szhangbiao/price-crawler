#!/usr/bin/env python

"""
A股指数模块.

这个包提供了获取A股主要指数数据的功能。
"""

from .stock_indices import get_all_indices, get_stock_index

__all__ = ["get_stock_index", "get_all_indices"]
