#!/usr/bin/env python

"""
黄金价格爬虫统一接口模块.

这个模块提供了统一的接口，用于从多个来源获取黄金价格数据。
包括金投网(cngold.org)、GoldPrice.org网站和聚合数据API。
"""

# 标准库导入
import logging

# 导入爬虫模块
from .cngold_playwright_crawler import get_gold_price as get_gold_price_from_cngold_playwright
from .goldprice_crawler import get_gold_price_from_goldprice
from .juhe_api import get_gold_price_fallback, get_gold_price_from_juhe

# 获取logger
logger = logging.getLogger(__name__)


def get_gold_price(gold_type: str = "XAU") -> dict | None:
    """
    获取黄金价格.

    按照以下顺序尝试获取黄金价格数据：
    1. 金投网爬虫
    2. GoldPrice.org爬虫
    3. 聚合数据API
    4. 备用模拟数据

    Args:
        gold_type: 黄金类型，可选值为 "XAU"(国际黄金) 或 "Au9999"(上海黄金交易所黄金9999)，默认为 "XAU"。

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    try:
        # 首先尝试从金投网获取所有黄金价格数据
        all_gold_prices = get_gold_price_from_cngold_playwright()
        if all_gold_prices:
            # 从所有数据中获取指定类型的黄金价格
            gold_info = all_gold_prices.get(gold_type)
            if gold_info:
                logger.info(f"成功从金投网获取{gold_type}黄金价格")
                # 处理字段名变化
                if "change_amount" in gold_info and "change" not in gold_info:
                    gold_info["change"] = gold_info["change_amount"]
                return gold_info

        # 如果失败，尝试从GoldPrice.org获取
        gold_info = get_gold_price_from_goldprice()
        if gold_info:
            logger.info("成功从GoldPrice.org获取黄金价格")
            return gold_info
            
        # 如果失败，尝试从聚合数据API获取
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
    configure_basic_logging("gold_crawler.log", level=logging.INFO)

    print("黄金价格爬虫测试")
    print("-" * 50)

    # 测试获取黄金价格
    gold_type = "XAU"  # 默认获取国际黄金价格
    gold_info = get_gold_price(gold_type)
    if gold_info:
        print(f"{gold_type}黄金价格: {gold_info.get('price', '未知')} 元/克")
        # 处理字段名变化
        change = gold_info.get('change', gold_info.get('change_amount', '未知'))
        print(f"涨跌: {change} | 涨跌幅: {gold_info.get('change_percent', '未知')}")
        print(f"更新时间: {gold_info.get('update_time', '未知')}")
        
        # 显示数据来源
        if gold_info.get("is_fallback"):
            print("数据来源: 模拟数据（备用方法）")
        else:
            source = gold_info.get('source', '金投网')
            print(f"数据来源: {source}")
            
        # 尝试获取其他类型的黄金价格
        print("\n获取所有黄金价格数据:")
        all_prices = get_gold_price()
        if all_prices and isinstance(all_prices, dict):
            # 有效的黄金类型列表
            valid_gold_types = ["XAU", "Au9999"]
            for gold_key, price_data in all_prices.items():
                # 只处理有效的黄金类型，并避免重复打印已显示的数据
                if gold_key in valid_gold_types and gold_key != gold_type:
                    if isinstance(price_data, dict):
                        print(f"\n{gold_key}黄金价格: {price_data.get('price', '未知')} 元/克")
                        change = price_data.get('change', price_data.get('change_amount', '未知'))
                        print(f"涨跌: {change} | 涨跌幅: {price_data.get('change_percent', '未知')}")
                        print(f"更新时间: {price_data.get('update_time', '未知')}")
                    else:
                        print(f"\n{gold_key}黄金价格: 数据格式错误")

    else:
        print("获取黄金价格失败")

    print("-" * 50)
