#!/usr/bin/env python

"""
黄金价格爬虫包.

这个包提供了从多个来源获取黄金价格的功能。
包括金投网(cngold.org)、GoldPrice.org网站和聚合数据API。
"""

# 导入子模块
from .gold_crawler import get_gold_price
from .goldprice_crawler import get_gold_price_from_goldprice
from .juhe_api import get_gold_price_fallback, get_gold_price_from_juhe
