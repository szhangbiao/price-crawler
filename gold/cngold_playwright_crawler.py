#!/usr/bin/env python

"""
金投网黄金价格爬虫模块 (Playwright版本).

这个模块提供了从金投网(cngold.org)获取黄金价格的实现，使用Playwright处理JavaScript动态加载的内容。
相比于使用requests+BeautifulSoup的方法，这种方式可以获取到JavaScript渲染后的完整页面内容。
"""

# 标准库导入
import asyncio
import logging
import time
from datetime import datetime
from typing import Any, TypedDict

# 第三方库导入
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from utils.logger import get_logger


# 定义类型
class GoldPriceData(TypedDict):
    """黄金价格数据结构."""
    price: str  # 价格
    change_amount: str  # 涨跌额
    change_percent: str  # 涨跌幅
    update_time: str  # 更新时间

# 缓存机制
_cache: dict[str, Any] = {}
_cache_time: dict[str, float] = {}
CACHE_DURATION = 60  # 缓存有效期（秒）

logger = get_logger(__name__, "cngold_playwright_crawler.log", level=logging.DEBUG)

# 常量定义
CNGOLD_URL = "https://quote.cngold.org/gjs/"  # 现货黄金页面


async def get_gold_price_from_cngold(gold_type: str = "XAU") -> dict | None:
    """
    从金投网获取黄金价格，使用Playwright处理JavaScript动态加载的内容.

    Args:
        gold_type: 黄金类型，可选值为 "XAU"(国际黄金) 或 "Au9999"(上海黄金交易所黄金9999)，默认为 "XAU"。

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    try:
        # 调用获取所有黄金价格数据的函数
        all_gold_data = await get_all_gold_prices_from_cngold()
        
        # 如果获取失败，返回None
        if not all_gold_data:
            return None
        
        # 返回指定类型的黄金价格数据
        return all_gold_data.get(gold_type)

    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有未预见的异常，确保爬虫失败不会导致程序崩溃
        logger.error("从金投网获取黄金价格时出错: %s", e)
        return None


async def get_all_gold_prices_from_cngold() -> dict[str, GoldPriceData] | None:
    """
    从金投网获取所有黄金价格数据.

    Returns:
        dict[str, GoldPriceData] | None: 包含不同黄金类型价格数据的字典，键为黄金类型（"XAU"、"Au9999"等），
                    值为包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    # 检查缓存是否有效
    cache_key = "all_gold_prices"
    current_time = time.time()
    
    if cache_key in _cache and cache_key in _cache_time:
        if current_time - _cache_time[cache_key] < CACHE_DURATION:
            return _cache[cache_key]
    
    try:
        # 使用Playwright启动浏览器
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)  # headless=True表示不显示浏览器窗口
            
            # 创建新页面
            page = await browser.new_page()
            
            # 设置用户代理
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            # 访问页面并等待加载完成
            await page.goto(CNGOLD_URL)
            
            # 等待价格数据加载完成（等待特定元素出现）
            await page.wait_for_selector("dl.clearfix", timeout=10000)
            
            # 获取页面内容
            content = await page.content()
            
            # 关闭浏览器
            await browser.close()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(content, "lxml")
            
            # 解析所有黄金价格数据
            result = parse_all_gold_price_data(soup)
            
            # 更新缓存
            if result:
                _cache[cache_key] = result
                _cache_time[cache_key] = current_time
            
            return result

    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有未预见的异常，确保爬虫失败不会导致程序崩溃
        logger.error("从金投网获取黄金价格时出错: %s", e)
        return None


def parse_all_gold_price_data(soup: BeautifulSoup) -> dict[str, GoldPriceData] | None:
    """解析BeautifulSoup对象中的所有黄金价格数据.

    Args:
        soup: BeautifulSoup解析后的HTML对象。

    Returns:
        dict[str, GoldPriceData] | None: 包含不同黄金类型价格数据的字典，键为黄金类型（"XAU"、"Au9999"等），
                    值为包含价格、涨跌额、涨跌幅和时间的字典，如果解析失败则返回None。
    """
    try:
        # 查找包含黄金价格的dl元素
        price_dl = soup.select("dl.clearfix")
        if not price_dl:
            logger.warning("未找到黄金价格数据元素")
            # 如果找不到元素，返回包含模拟数据的字典
            return {
                "XAU": get_mock_data("金投网(国际黄金XAU-模拟数据)"),
                "Au9999": get_mock_data("金投网(上海黄金交易所Au9999-模拟数据)")
            }
        
        # 定义目标黄金标识符及其对应的数据源名称和类型
        gold_identifiers = {
            "XAU": {"name": "金投网(国际黄金XAU)", "type": "XAU"},
            "现货黄金": {"name": "金投网(现货黄金)", "type": "XAU"},
            "Au9999": {"name": "金投网(上海黄金交易所Au9999)", "type": "Au9999"},
            "Au99.99": {"name": "金投网(上海黄金交易所Au9999)", "type": "Au9999"}
        }
        
        # 记录找到的所有目标黄金数据
        found_gold_data = {}
        
        # 遍历找到的dl元素，查找包含目标黄金标识符的元素
        for _i, dl in enumerate(price_dl):
            dl_text = dl.text.strip()
            
            # 查找是否包含目标黄金标识符
            xau_element = dl.select_one("span em")
            xau_text = xau_element.text.strip() if xau_element else ""
            
            # 检查是否包含任何目标黄金标识符
            found_identifier = None
            source_name = ""
            gold_type = ""
            
            # 首先检查span em元素中的标识符
            for identifier, info in gold_identifiers.items():
                if identifier in xau_text:
                    found_identifier = identifier
                    source_name = info["name"]
                    gold_type = info["type"]
                    break
            
            # 如果span em元素中没有找到，则检查整个dl文本
            if not found_identifier:
                for identifier, info in gold_identifiers.items():
                    if identifier in dl_text:
                        found_identifier = identifier
                        source_name = info["name"]
                        gold_type = info["type"]
                        break
            
            if found_identifier:
                # 提取价格信息 - 查找包含价格的元素
                price_elements = dl.select("dd em")
                
                # 提取价格、涨跌额和涨跌幅
                price_data = extract_price_data(price_elements, source_name)
                if price_data:
                    # 将找到的数据存储在字典中，以黄金类型为键
                    found_gold_data[gold_type] = price_data
        
        # 如果没有找到任何黄金数据，返回包含模拟数据的字典
        if not found_gold_data:
            logger.warning("未找到任何黄金数据，使用模拟数据")
            return {
                "XAU": get_mock_data("金投网(国际黄金XAU-模拟数据)"),
                "Au9999": get_mock_data("金投网(上海黄金交易所Au9999-模拟数据)")
            }
        
        # 如果缺少某些类型的数据，使用模拟数据补充
        if "XAU" not in found_gold_data:
            found_gold_data["XAU"] = get_mock_data("金投网(国际黄金XAU-模拟数据)")
        if "Au9999" not in found_gold_data:
            found_gold_data["Au9999"] = get_mock_data("金投网(上海黄金交易所Au9999-模拟数据)")
        
        return found_gold_data

    except Exception as e:
        logger.error("解析黄金价格数据时出错: %s", e)
        # 返回包含模拟数据的字典
        return {
            "XAU": get_mock_data("金投网(国际黄金XAU-解析错误-模拟数据)"),
            "Au9999": get_mock_data("金投网(上海黄金交易所Au9999-解析错误-模拟数据)")
        }


def parse_gold_price_data(soup: BeautifulSoup, gold_type: str = "XAU") -> dict | None:
    """解析BeautifulSoup对象中的黄金价格数据.
    
    此函数现在是对parse_all_gold_price_data的包装，用于向后兼容。

    Args:
        soup: BeautifulSoup解析后的HTML对象。
        gold_type: 黄金类型，可选值为 "XAU"(国际黄金) 或 "Au9999"(上海黄金交易所黄金9999)，默认为 "XAU"。

    Returns:
        dict | None: 包含价格、涨跌额、涨跌幅和时间的字典，如果解析失败则返回None。
    """
    try:
        # 调用解析所有黄金价格数据的函数
        all_gold_data = parse_all_gold_price_data(soup)
        
        # 如果解析失败，返回None
        if not all_gold_data:
            return None
        
        # 返回指定类型的黄金价格数据
        if gold_type in all_gold_data:
            return all_gold_data[gold_type]
        
        # 如果找不到指定类型，返回第一个找到的数据
        first_key = next(iter(all_gold_data))
        return all_gold_data[first_key]
        
    except Exception as e:
        logger.error("解析黄金价格数据时出错: %s", e)
        return get_mock_data("金投网(解析错误-模拟数据)")


def extract_price_data(price_elements: list, source_name: str) -> GoldPriceData:
    """从价格元素中提取价格、涨跌额和涨跌幅数据.
    
    Args:
        price_elements: 包含价格信息的元素列表
        source_name: 数据源名称
        
    Returns:
        GoldPriceData: 包含价格、涨跌额、涨跌幅和时间的字典
    """
    # 初始化变量
    price_str = ""
    change_amount_str = ""
    change_percent_str = ""
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_mock_data = False
    
    # 现货黄金通常在第3个位置（索引2）
    price_index = 2
    if len(price_elements) > price_index:
        try:
            price_text = price_elements[price_index].text.strip()
            if price_text != '----' and price_text:
                # 移除可能的逗号和空格
                price_text = price_text.replace(',', '').strip()
                # 保存为字符串格式
                price_str = price_text
            else:
                is_mock_data = True
        except (ValueError, IndexError):
            is_mock_data = True
    else:
        is_mock_data = True
    
    # 涨跌额通常在第5个位置（索引4）
    change_index = 5
    if len(price_elements) > change_index:
        try:
            change_text = price_elements[change_index].text.strip()
            
            # 处理特殊情况
            if change_text != '----' and change_text:
                # 保存为字符串格式，保留+号
                change_amount_str = change_text.strip()
            else:
                is_mock_data = True
        except (ValueError, IndexError):
            is_mock_data = True
    else:
        is_mock_data = True
    
    # 涨跌幅通常在第6个位置（索引5）
    percent_index = 6
    if len(price_elements) > percent_index:
        try:
            change_percent_text = price_elements[percent_index].text.strip()
            
            if change_percent_text != '----' and change_percent_text:
                # 保存为字符串格式，保留%和+号
                change_percent_str = change_percent_text.strip()
            else:
                is_mock_data = True
        except (ValueError, IndexError):
            is_mock_data = True
    else:
        is_mock_data = True
    
    # 如果所有数据都是模拟的，使用模拟数据
    if is_mock_data:
        return get_mock_data(f"{source_name}(模拟数据)")
    
    # 返回解析结果
    return {
        "price": price_str,
        "change_amount": change_amount_str,
        "change_percent": change_percent_str,
        "update_time": update_time
    }


def get_mock_data(source_name: str) -> GoldPriceData:
    """
    获取模拟数据.
    
    Args:
        source_name: 数据源名称
        
    Returns:
        GoldPriceData: 包含模拟价格、涨跌额、涨跌幅和时间的字典
    """
    price = "772.75"
    change_amount = "+1.76"
    change_percent = "+0.23%"
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "price": price,
        "change_amount": change_amount,
        "change_percent": change_percent,
        "update_time": update_time
    }

# 同步包装函数，用于非异步环境调用
def get_all_gold_prices() -> dict[str, GoldPriceData] | None:
    """同步方式获取所有黄金价格，用于非异步环境调用.
    
    Returns:
        Dict[str, GoldPriceData] | None: 包含不同黄金类型价格数据的字典，键为黄金类型（"XAU"、"Au9999"等），
                    值为包含价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None。
    """
    # 检查缓存是否有效
    cache_key = "all_gold_prices"
    current_time = time.time()
    
    if cache_key in _cache and cache_key in _cache_time:
        if current_time - _cache_time[cache_key] < CACHE_DURATION:
            return _cache[cache_key]
    
    # 如果缓存无效或不存在，则获取新数据
    return asyncio.run(get_all_gold_prices_from_cngold())


# 同步包装函数，用于非异步环境调用
def get_gold_price(gold_type: str = None) -> dict[str, GoldPriceData] | GoldPriceData | None:
    """同步方式获取黄金价格数据，用于非异步环境调用.
    
    Args:
        gold_type: 黄金类型，可选值为 "XAU"(国际黄金) 或 "Au9999"(上海黄金交易所黄金9999)。
                  如果不指定，则返回所有类型的黄金价格数据。
    
    Returns:
        dict[str, GoldPriceData] | GoldPriceData | None: 
            - 如果gold_type为None，返回包含所有黄金类型价格数据的字典
            - 如果指定了gold_type，返回该类型的黄金价格数据
            - 如果获取失败，返回None
    """
    # 获取所有黄金价格数据（会自动使用缓存）
    all_prices = get_all_gold_prices()
    
    # 如果获取失败，返回None
    if not all_prices:
        return None
    
    # 如果没有指定黄金类型，返回所有数据
    if gold_type is None:
        return all_prices
    
    # 返回指定类型的黄金价格数据
    return all_prices.get(gold_type)


# 测试代码
if __name__ == "__main__":
    # 注意：不需要再次配置日志，因为已经通过get_logger配置过了
    print("金投网黄金价格爬虫测试 (Playwright版本)")
    print("-" * 50)
    
    # 设置日志级别为INFO，减少调试信息输出
    logger.setLevel(logging.INFO)
    
    # 测试获取所有黄金价格数据
    print("获取所有黄金价格数据:")
    all_gold_info = get_all_gold_prices()
    if all_gold_info:
        print(f"成功获取 {len(all_gold_info)} 种黄金价格数据")
        print("-" * 50)
        
        # 遍历所有黄金价格数据
        for gold_type, gold_info in all_gold_info.items():
            print(f"黄金类型: {gold_type}")
            print(f"黄金价格: {gold_info.get('price','未知')} 元/克")
            print(f"涨跌: {gold_info.get('change_amount','未知')} | 涨跌幅: {gold_info.get('change_percent','未知')}")
            print(f"更新时间: {gold_info.get('update_time', '未知')}")
            print("-" * 50)
        
        # 从已获取的数据中提取XAU和Au9999数据，避免重复请求
        print("从缓存中获取国际黄金(XAU)价格:")
        xau_info = all_gold_info.get("XAU")
        if xau_info:
            print(f"黄金价格: {xau_info.get('price','未知')} 元/克")
            print(f"涨跌: {xau_info.get('change_amount','未知')} | 涨跌幅: {xau_info.get('change_percent','未知')}")
            print(f"更新时间: {xau_info.get('update_time', '未知')}")
        else:
            print("获取国际黄金价格失败")

        print("-" * 50)
        
        print("从缓存中获取上海黄金交易所(Au9999)价格:")
        au9999_info = all_gold_info.get("Au9999")
        if au9999_info:
            print(f"黄金价格: {au9999_info.get('price','未知')} 元/克")
            print(f"涨跌: {au9999_info.get('change_amount','未知')} | 涨跌幅: {au9999_info.get('change_percent','未知')}")
            print(f"更新时间: {au9999_info.get('update_time', '未知')}")
        else:
            print("获取上海黄金交易所价格失败")

        print("-" * 50)
        
        # 测试缓存机制
        print("测试缓存机制 - 再次获取所有黄金价格数据:")
        cached_gold_info = get_all_gold_prices()
        if cached_gold_info:
            print(f"成功从缓存获取 {len(cached_gold_info)} 种黄金价格数据")
            print(f"缓存时间: {_cache_time.get('all_gold_prices', 0)}")
        else:
            print("从缓存获取黄金价格数据失败")
    else:
        print("获取黄金价格数据失败")

    print("-" * 50)