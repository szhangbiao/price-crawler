#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A股指数数据获取模块

这个模块提供了获取A股主要指数（上证指数、深证成指、创业板指）的功能。
使用新浪财经API获取实时数据。
"""

# 标准库导入
import logging
from datetime import datetime

# 第三方库导入
import requests

# 获取logger
logger = logging.getLogger(__name__)

# 常量定义
INDEX_CODES = {
    'sh': 's_sh000001',  # 上证指数
    'sz': 's_sz399001',  # 深证成指
    'cyb': 's_sz399006'  # 创业板指
}

INDEX_NAMES = {
    'sh': '上证指数',
    'sz': '深证成指',
    'cyb': '创业板指'
}


def get_stock_index(index_type='sh'):
    """
    获取指定的A股指数数据
    
    Args:
        index_type: 指数类型，可选值：'sh'(上证指数)、'sz'(深证成指)、'cyb'(创业板指)
    
    Returns:
        dict: 包含指数名称、价格、涨跌额、涨跌幅和时间的字典，如果出错则返回None
    """
    if index_type not in INDEX_CODES:
        logger.error(f"不支持的指数类型: {index_type}")
        return None
        
    try:
        # 使用新浪财经的API获取指数数据
        url = f"https://hq.sinajs.cn/list={INDEX_CODES[index_type]}"
        headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)  # 添加超时设置
        
        # 解析返回的数据
        if response.status_code == 200:
            text = response.text
            data = text.split('="')[1].split('";')[0].split(',')
            
            if len(data) >= 4:
                index_name = INDEX_NAMES[index_type]
                current_price = float(data[1])
                change = float(data[2])
                change_percent = float(data[3])
                
                return {
                    'name': index_name,
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                logger.warning(f"获取{INDEX_NAMES[index_type]}数据格式不正确")
        else:
            logger.warning(f"获取{INDEX_NAMES[index_type]}数据HTTP状态码: {response.status_code}")
        return None
    except requests.RequestException as e:
        logger.error(f"请求{INDEX_NAMES[index_type]}数据时出错: {e}")
        return None
    except Exception as e:
        logger.error(f"获取{INDEX_NAMES[index_type]}数据时出错: {e}")
        return None


def get_all_indices():
    """
    获取所有配置的A股指数数据
    
    Returns:
        list: 包含所有指数数据的列表，每个元素是一个字典
    """
    results = []
    for index_type in INDEX_CODES.keys():
        index_data = get_stock_index(index_type)
        if index_data:
            results.append(index_data)
    return results


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试获取上证指数
    sh_index = get_stock_index('sh')
    if sh_index:
        print(f"{sh_index['name']}: {sh_index['price']} | 涨跌: {sh_index['change']} | 涨跌幅: {sh_index['change_percent']}%")
    
    # 测试获取深证成指
    sz_index = get_stock_index('sz')
    if sz_index:
        print(f"{sz_index['name']}: {sz_index['price']} | 涨跌: {sz_index['change']} | 涨跌幅: {sz_index['change_percent']}%")
    
    # 测试获取创业板指
    cyb_index = get_stock_index('cyb')
    if cyb_index:
        print(f"{cyb_index['name']}: {cyb_index['price']} | 涨跌: {cyb_index['change']} | 涨跌幅: {cyb_index['change_percent']}%")
    
    # 测试获取所有指数
    print("\n获取所有指数:")
    all_indices = get_all_indices()
    for index in all_indices:
        print(f"{index['name']}: {index['price']} | 涨跌: {index['change']} | 涨跌幅: {index['change_percent']}%")