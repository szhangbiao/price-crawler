#!/usr/bin/env python

"""
汇率数据API调用模块.

这个模块提供了从不同API获取美元对人民币汇率的功能。
包括聚合数据API和美心智能平台API的调用实现。
"""

import logging
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from utils.logger import get_logger

load_dotenv()

# 获取logger
logger = get_logger(__name__, "exchange_rate.log")

# https://www.mxnzp.com 平台秘钥 (备用API)
APP_ID = os.getenv("MXNZP_APP_ID")
APP_SECRET = os.getenv("MXNZP_APP_SECRET")
MXZNP_URL = "https://www.mxnzp.com/api/exchange_rate/aim?from=USD&to=CNY&app_id={}&app_secret={}"

# 聚合数据汇率API
JUHE_APPKEY = os.getenv("JUHE_EXCHANGE_RATE_APPKEY")
JUHE_URL = "http://op.juhe.cn/onebox/exchange/currency?key={}&from=USD&to=CNY&version=2"


def get_exchange_rate_from_juhe() -> dict | None:
    """从聚合数据API获取美元对人民币的实时汇率.
    
    Returns:
        dict | None: 包含汇率信息的字典，如果获取失败则返回None
    """
    try:
        if not JUHE_APPKEY:
            logger.warning("聚合数据API密钥未配置，无法获取汇率数据")
            return None

        url = JUHE_URL.format(JUHE_APPKEY)
        response = requests.get(url,timeout=10)
        response.raise_for_status()  # 如果请求失败则抛出HTTPError
        data = response.json()

        if data.get("error_code") == 0:
            # 从返回的数据中找到美元对人民币的汇率
            result_list = data.get("result", [])

            # 查找美元对人民币的汇率数据
            usd_cny_data = None
            for item in result_list:
                if item.get("currencyF") == "USD" and item.get("currencyT") == "CNY":
                    usd_cny_data = item
                    break

            if usd_cny_data:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rate_data = {
                    "name": "USD/CNY",
                    "desc": f"{usd_cny_data.get('currencyF_Name', '美元')}/{usd_cny_data.get('currencyT_Name', '人民币')}",
                    "price": f"{float(usd_cny_data.get('exchange', '0')):.4f}",
                    "time": current_time,
                    "update": usd_cny_data.get("updateTime", current_time),
                    "source": "聚合数据",
                }
                logger.info("成功从聚合数据获取汇率数据：%s = %s", rate_data['name'], rate_data['price'])
                return rate_data
            else:
                logger.error("在聚合数据API返回中未找到USD/CNY汇率数据")
                return None
        else:
            logger.error("聚合数据API返回错误: %s", data.get('reason'))
            return None

    except requests.exceptions.RequestException as e:
        logger.error("请求聚合数据API时发生网络错误: %s", e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有未预见的异常，确保API调用失败不会导致程序崩溃
        logger.error("从聚合数据获取汇率数据时发生未知错误: %s", e)
        return None


def get_exchange_rate_from_mxnzp() -> dict | None:
    """从美心智能平台获取美元对人民币的实时汇率（备用方法）.
    
    Returns:
        dict | None: 包含汇率信息的字典，如果获取失败则返回None
    """
    try:
        if not APP_ID or not APP_SECRET:
            logger.warning("美心智能平台API密钥未配置，无法获取汇率数据")
            return None

        url = MXZNP_URL.format(APP_ID, APP_SECRET)
        response = requests.get(url,timeout=10)
        response.raise_for_status()  # 如果请求失败则抛出HTTPError
        data = response.json()
        if data.get("code") == 1:
            item = data.get("data")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rate_data = {
                "name": "USD/CNY",
                "desc": item["nameDesc"],
                "price": f"{float(item['price']):.4f}",
                "time": current_time,
                "update": item["updateTime"],
                "source": "美心智能平台",
            }
            logger.info("成功从美心智能平台获取汇率数据：%s = %s", rate_data['name'], rate_data['price'])
            return rate_data
        else:
            logger.error("美心智能平台API返回错误: %s", data.get('msg'))
            return None

    except requests.exceptions.RequestException as e:
        logger.error("请求美心智能平台API时发生网络错误: %s", e)
        return None
    except (ValueError, TypeError, KeyError) as e:
        logger.error("处理美心智能平台数据时出错: %s", e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有未预见的异常，确保API调用失败不会导致程序崩溃
        logger.error("从美心智能平台获取汇率数据时发生未知错误: %s", e)
        return None


def get_exchange_rate() -> dict | None:
    """获取美元对人民币的实时汇率，优先使用聚合数据API，如果失败则使用美心智能平台API.
    
    Returns:
        dict | None: 包含汇率信息的字典，如果获取失败则返回None
    """
    # 首先尝试从聚合数据获取
    rate_data = get_exchange_rate_from_juhe()
    if rate_data:
        return rate_data

    # 如果聚合数据获取失败，尝试从美心智能平台获取
    logger.info("从聚合数据获取汇率失败，尝试从美心智能平台获取")
    rate_data = get_exchange_rate_from_mxnzp()
    if rate_data:
        return rate_data

    logger.error("所有API获取汇率数据均失败")
    return None


if __name__ == "__main__":
    # 设置日志级别为DEBUG以查看更多信息
    logger.setLevel(logging.DEBUG)

    # 测试 get_exchange_rate 函数
    rate = get_exchange_rate()
    if rate:
        print(f"汇率名称: {rate['name']}")
        print(f"汇率描述: {rate['desc']}")
        print(f"当前汇率: {rate['price']}")
        print(f"请求时间: {rate['time']}")
        print(f"更新时间: {rate['update']}")
        print(f"数据来源: {rate['source']}")
    else:
        print("获取汇率数据失败，请检查API密钥配置和网络连接")
        print("请在.env文件中配置以下密钥：")
        print("JUHE_EXCHANGE_RATE_APPKEY - 聚合数据汇率API密钥")
        print("MXNZP_APP_ID 和 MXNZP_APP_SECRET - 美心智能平台API密钥（备用）")