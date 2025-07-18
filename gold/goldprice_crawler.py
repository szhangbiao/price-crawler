#!/usr/bin/env python

"""
GoldPrice网站黄金价格爬虫模块.

这个模块提供了从GoldPrice.org获取黄金价格的功能。
使用requests库调用GoldPrice.org的API获取实时黄金价格数据。
"""

# 标准库导入
import logging
from datetime import datetime

# 第三方库导入
import requests

# 获取logger
logger = logging.getLogger(__name__)

# API URL
GOLDPRICE_API_URL = "https://goldpricez.com/cn/gram"

# 人民币兑美元汇率（备用）
USD_TO_CNY_RATE = 7.1  # 备用汇率，实际使用时应从exchange_rate模块获取


def get_gold_price_from_goldprice() -> dict | None:
    """
    从GoldPrice.org获取黄金价格.

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    try:
        logger.debug(f"请求GoldPrice API: {GOLDPRICE_API_URL}")

        # 设置请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(GOLDPRICE_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 检查API返回的数据
        if "items" in data and len(data["items"]) > 0:
            # 获取黄金价格（美元/盎司）
            gold_price_usd_oz = data["items"][0]["xauPrice"]
            # 获取涨跌幅
            change_percent = data["items"][0]["pcXau"]

            # 将盎司转换为克（1盎司 = 31.1034768克）
            gold_price_usd_g = gold_price_usd_oz / 31.1034768

            # 尝试从exchange_rate模块获取汇率
            try:
                from exchange_rate import get_exchange_rate

                rate_data = get_exchange_rate()
                if rate_data and "price" in rate_data:
                    usd_to_cny_rate = float(rate_data["price"])
                    logger.info(f"获取到实时汇率: {usd_to_cny_rate}")
                else:
                    usd_to_cny_rate = USD_TO_CNY_RATE
                    logger.warning(f"无法获取实时汇率，使用备用汇率: {USD_TO_CNY_RATE}")
            except ImportError:
                usd_to_cny_rate = USD_TO_CNY_RATE
                logger.warning(f"无法导入exchange_rate模块，使用备用汇率: {USD_TO_CNY_RATE}")

            # 将美元价格转换为人民币价格
            gold_price_cny_g = gold_price_usd_g * usd_to_cny_rate

            # 计算涨跌额（基于涨跌幅）
            change = gold_price_cny_g * change_percent / 100

            return {
                "price": round(gold_price_cny_g, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "goldprice.org",
            }
        else:
            logger.warning("API返回数据格式不正确")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"请求GoldPrice API时发生网络错误: {e}")
        return None
    except Exception as e:
        logger.error(f"从GoldPrice获取黄金价格时出错: {e}")
        return None


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("goldprice_crawler.log", encoding="utf-8"),
        ],
    )

    print("GoldPrice.org黄金价格爬虫测试")
    print("-" * 50)

    # 测试获取黄金价格
    gold_info = get_gold_price_from_goldprice()
    if gold_info:
        print(f"黄金价格: {gold_info['price']} 元/克")
        print(f"涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%")
        print(f"更新时间: {gold_info.get('update_time', '未知')}")
        print(f"数据来源: {gold_info.get('source', '未知')}")
    else:
        print("获取黄金价格失败")

    print("-" * 50)
