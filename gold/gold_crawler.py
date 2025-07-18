#!/usr/bin/env python

"""
黄金价格爬虫统一接口模块.

这个模块提供了统一的接口，用于从多个来源获取黄金价格数据。
包括金投网(cngold.org)、GoldPrice.org网站和聚合数据API。
"""

# 标准库导入
import logging

from utils.logger import get_logger

# 导入爬虫模块
from .cngold_crawler import get_gold_price_from_cngold
from .goldprice_crawler import get_gold_price_from_goldprice
from .juhe_api import get_gold_price_fallback, get_gold_price_from_juhe

# 获取logger
logger = get_logger(__name__, "gold_crawler.log")


def get_gold_price() -> dict | None:
    """
    获取黄金价格.

    按照以下顺序尝试获取黄金价格数据：
    1. 金投网爬虫
    2. GoldPrice.org爬虫
    3. 聚合数据API
    4. 备用模拟数据

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    try:
        # 首先尝试从金投网获取
        logger.debug("尝试从金投网获取黄金价格")
        gold_info = get_gold_price_from_cngold()
        if gold_info:
            logger.info("成功从金投网获取黄金价格")
            return gold_info

        # 如果失败，尝试从GoldPrice.org获取
        logger.debug("尝试从GoldPrice.org获取黄金价格")
        gold_info = get_gold_price_from_goldprice()
        if gold_info:
            logger.info("成功从GoldPrice.org获取黄金价格")
            return gold_info
            
        # 如果失败，尝试从聚合数据API获取
        logger.debug("尝试从聚合数据API获取黄金价格")
        gold_info = get_gold_price_from_juhe()
        if gold_info:
            logger.info("成功从聚合数据API获取黄金价格")
            return gold_info

        # 如果所有API都失败，使用备用的模拟数据方法
        logger.warning("无法从任何API获取黄金价格，使用备用方法")
        return get_gold_price_fallback()
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有异常并回退到模拟数据，确保程序能继续运行
        logger.error("获取黄金价格时出错: %s", e)
        return get_gold_price_fallback()


# 测试代码
if __name__ == "__main__":
    # 配置日志
    from utils.logger import configure_basic_logging
    configure_basic_logging("gold_crawler.log", level=logging.DEBUG)

    print("黄金价格爬虫测试")
    print("-" * 50)

    # 测试获取黄金价格
    gold_info = get_gold_price()
    if gold_info:
        print(f"黄金价格: {gold_info['price']} 元/克")
        print(f"涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%")
        print(f"更新时间: {gold_info.get('update_time', '未知')}")
        
        # 显示数据来源
        if gold_info.get("is_fallback"):
            print("数据来源: 模拟数据（备用方法）")
        else:
            print(f"数据来源: {gold_info.get('source', '未知')}")
    else:
        print("获取黄金价格失败")

    print("-" * 50)
    print("提示: 请在.env文件中配置有效的API密钥以获取实时数据")
