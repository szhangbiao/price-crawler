#!/usr/bin/env python

"""
聚合数据API黄金价格获取模块.

这个模块提供了从聚合数据API获取黄金价格的功能。
如果API调用失败，将使用备用方法获取数据。
"""

# 标准库导入
import logging
import os
import random
from datetime import datetime

# 第三方库导入
import requests
from dotenv import load_dotenv

from utils.logger import get_logger

# 加载环境变量
load_dotenv()

# 获取logger
logger = get_logger(__name__, "gold_juhe_price.log")

# API配置
JUHE_APPKEY = os.getenv("JUHE_GOLD_APPKEY")

# API URL
JUHE_URL = "http://web.juhe.cn/finance/gold/shgold?key={}&v=1"

# 常量定义
BASE_GOLD_PRICE = 450.0  # 基准黄金价格，用于生成模拟数据（备用）


def get_gold_price_from_juhe() -> dict | None:
    """
    从聚合数据API获取黄金价格.

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    if not JUHE_APPKEY or JUHE_APPKEY == "your_juhe_appkey":
        logger.warning("聚合数据API密钥未配置")
        return None

    try:
        url = JUHE_URL.format(JUHE_APPKEY)
        logger.debug("请求聚合数据API: %s", url)

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("resultcode") == "200" and data.get("result"):
            # 获取Au99.99（沪金99）的数据
            gold_data = None
            for _key, item in data["result"][0].items():
                if item.get("variety") == "Au99.99":
                    gold_data = item
                    break

            if gold_data:
                price = float(gold_data["latestpri"])
                last_price = float(gold_data["yespri"])
                change = round(price - last_price, 2)
                change_percent = float(gold_data["limit"].strip("%"))

                return {
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "update_time": gold_data["time"],
                    "source": "聚合数据API",
                }
            else:
                logger.warning("未找到Au99.99黄金价格数据")
        else:
            logger.warning("聚合数据API返回错误: %s", data.get('reason'))

        return None
    except requests.exceptions.RequestException as e:
        logger.error("请求聚合数据API时发生网络错误: %s", e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有未预见的异常，确保API调用失败不会导致程序崩溃
        logger.error("从聚合数据获取黄金价格时出错: %s", e)
        return None


def get_gold_price_fallback() -> dict | None:
    """
    获取黄金价格（模拟数据）- 备用方法.

    当API调用失败时，使用此方法生成模拟数据。

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    try:
        # 添加一些随机波动，模拟真实数据
        random_change = round(random.uniform(-2.0, 2.0), 2)

        price = round(BASE_GOLD_PRICE + random_change, 2)
        change = random_change
        change_percent = round(change / BASE_GOLD_PRICE * 100, 2)

        logger.info("使用备用方法生成模拟黄金价格数据")
        return {
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_fallback": True,
            "source": "模拟数据",
        }
    except (ValueError, TypeError) as e:
        logger.error("生成模拟黄金价格数据时出错: %s", e)
        return None


# 测试代码
if __name__ == "__main__":
    # 配置日志
    from utils.logger import configure_basic_logging
    configure_basic_logging("gold_price.log", level=logging.DEBUG)

    print("聚合数据API黄金价格获取测试")
    print("-" * 50)

    # 测试获取黄金价格
    gold_info = get_gold_price_from_juhe()
    if gold_info:
        print(f"黄金价格: {gold_info['price']} 元/克")
        print(f"涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%")
        print(f"更新时间: {gold_info.get('update_time', '未知')}")
        print(f"数据来源: {gold_info.get('source', '聚合数据API')}")
    else:
        print("从聚合数据API获取黄金价格失败，尝试备用方法")
        gold_info = get_gold_price_fallback()
        if gold_info:
            print(f"黄金价格: {gold_info['price']} 元/克")
            print(f"涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%")
            print(f"更新时间: {gold_info.get('update_time', '未知')}")
            print(f"数据来源: {gold_info.get('source', '模拟数据')}")
        else:
            print("获取黄金价格失败")

    print("-" * 50)
    print("提示: 请在.env文件中配置有效的API密钥以获取实时数据")