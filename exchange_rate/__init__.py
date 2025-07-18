#!/usr/bin/env python

"""
汇率数据获取模块.

这个模块提供了获取美元对人民币汇率的功能。
使用聚合数据API和美心智能平台API获取实时汇率数据。
如果主要API调用失败，将使用备用API获取数据。
"""

from .exchange_rate_api import get_exchange_rate

__all__ = ["get_exchange_rate"]
