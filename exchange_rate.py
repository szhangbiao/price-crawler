import logging
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# https://www.mxnzp.com 平台秘钥
APP_ID = os.getenv("MXNZP_APP_ID")
APP_SECRET = os.getenv("MXNZP_APP_SECRET")
MXZNP_URL = "https://www.mxnzp.com/api/exchange_rate/aim?from=USD&to=CNY&app_id={}&app_secret={}"

def get_exchange_rate():
    """获取美元对人民币的实时汇率。"""
    try:
        url = MXZNP_URL.format(APP_ID, APP_SECRET)
        #logging.info(f"request url:{url}")
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败则抛出HTTPError
        data = response.json()
        if data.get('code') == 1:
            item = data.get('data')
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            rate_data = {
                'name': 'USD/CNY',
                'desc': item['nameDesc'],
                'price': f"{float(item['price']):.4f}",
                'time': current_time,
                'update':item['updateTime']
            }
            #logging.info(f"成功获取汇率数据：{rate_data['name']} - {rate_data['price']}")
            return rate_data
        else:
            logging.error(f"API返回错误: {data.get('msg')}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"请求API时发生网络错误: {e}")
        return None
    except Exception as e:
        logging.error(f"获取汇率数据时发生未知错误: {e}")
        return None

if __name__ == '__main__':
    # 测试 get_exchange_rate 函数
    rate = get_exchange_rate()
    if rate:
        print(f"汇率名称: {rate['name']}")
        print(f"汇率描述: {rate['desc']}")
        print(f"当前汇率: {rate['price']}")
        print(f"请求时间: {rate['time']}")
        print(f"更新时间: {rate['update']}")