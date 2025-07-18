#!/usr/bin/env python

"""
黄金价格爬虫统一接口模块.

这个模块提供了统一的接口，用于从多个来源获取黄金价格数据。
包括金投网(cngold.org)和GoldPrice.org网站。
"""

# 标准库导入
import logging

# 导入爬虫模块
from .cngold_crawler import get_gold_price_from_cngold
from .goldprice_crawler import get_gold_price_from_goldprice

# 获取logger
logger = logging.getLogger(__name__)


def get_gold_price() -> dict | None:
    """
    获取黄金价格.

    首先尝试从金投网获取，如果失败则尝试从GoldPrice.org获取，
    如果两者都失败则返回None。

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

        # 如果两者都失败，返回None
        logger.warning("无法从任何来源获取黄金价格")
        return None
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有异常以确保爬虫失败不会影响主程序运行
        logger.error("获取黄金价格时出错: %s", e)
        return None


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("gold_crawler.log", encoding="utf-8"),
        ],
    )

    print("黄金价格爬虫测试")
    print("-" * 50)

    # 测试获取黄金价格
    gold_info = get_gold_price()
    if gold_info:
        print(f"黄金价格: {gold_info['price']} 元/克")
        print(f"涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%")
        print(f"更新时间: {gold_info.get('update_time', '未知')}")
        print(f"数据来源: {gold_info.get('source', '未知')}")
    else:
        print("获取黄金价格失败")

    print("-" * 50)
