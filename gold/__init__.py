#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
黄金价格爬虫包

这个包提供了从多个来源获取黄金价格的功能。
包括金投网(cngold.org)和GoldPrice.org网站。
"""

# 导入子模块
from .cngold_crawler import get_gold_price_from_cngold
from .goldprice_crawler import get_gold_price_from_goldprice