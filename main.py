#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
黄金价格和A股大盘指数监控程序

该程序用于监控黄金价格和A股大盘指数的变动，并将数据保存到CSV文件中。
"""

# 标准库导入
import time
import logging
from datetime import datetime

# 本地模块导入
from stock_indices import get_all_indices
from gold_price import get_gold_price
from exchange_rate import get_exchange_rate
from data_storage import CsvStorage


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('price_crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def monitor_prices(intervals):
    """监控价格变动
    
    Args:
        intervals (dict): 包含各类资产监控间隔的字典, e.g. {'gold': 60, 'indices': 120, 'exchange_rate': 300}
    """
    """监控价格变动
    
    Args:
        interval: 监控间隔，单位为秒
    """
    logger.info("开始监控黄金价格、汇率和A股大盘指数...")
    logger.info(f"监控间隔: 黄金 {intervals.get('gold', 'N/A')}s, 股指 {intervals.get('indices', 'N/A')}s, 汇率 {intervals.get('exchange_rate', 'N/A')}s")
    print("-" * 50)
    
    # 初始化数据存储
    storage = CsvStorage()
    
    # 加载已存在的数据
    gold_data, indices_data, exchange_rate_data = storage.load()
    
    last_fetch_times = {
        'gold': 0,
        'indices': 0,
        'exchange_rate': 0
    }
    error_counts = {
        'gold': 0,
        'indices': 0,
        'exchange_rate': 0
    }
    MAX_RETRIES = 3

    try:
        while True:
            current_time = time.time()
            data_updated = False

            # 获取黄金价格
            if current_time - last_fetch_times['gold'] >= intervals.get('gold', 60):
                gold_info = get_gold_price()
                last_fetch_times['gold'] = current_time
                if gold_info:
                    print(f"黄金价格: {gold_info['price']} 元/克 | 涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%" )
                    gold_data.loc[len(gold_data)] = gold_info
                    data_updated = True

            # 获取所有股指数据
            if current_time - last_fetch_times['indices'] >= intervals.get('indices', 60):
                all_indices = get_all_indices()
                last_fetch_times['indices'] = current_time
                if all_indices:
                    for index_info in all_indices:
                        print(f"{index_info['name']}: {index_info['price']} | 涨跌: {index_info['change']} | 涨跌幅: {index_info['change_percent']}%" )
                        indices_data.loc[len(indices_data)] = index_info
                    data_updated = True


            # 获取汇率数据
            if current_time - last_fetch_times['exchange_rate'] >= intervals.get('exchange_rate', 60*60):
                exchange_rate_info = get_exchange_rate()
                if exchange_rate_info:
                    print(f"汇率: {exchange_rate_info['name']} | 描述: {exchange_rate_info['desc']} | 价格: {exchange_rate_info['price']} | 更新时间: {exchange_rate_info['update']}")
                    exchange_rate_data.loc[len(exchange_rate_data)] = exchange_rate_info
                    last_fetch_times['exchange_rate'] = current_time
                    error_counts['exchange_rate'] = 0  # 成功后重置计数器
                    data_updated = True
                else:
                    error_counts['exchange_rate'] += 1
                    logger.warning(f"获取汇率数据失败，尝试次数: {error_counts['exchange_rate']}")
                    if error_counts['exchange_rate'] >= MAX_RETRIES:
                        logger.error("获取汇率数据连续失败次数过多，停止该次监控。")
                        last_fetch_times['exchange_rate'] = current_time

            if data_updated:
                print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
                storage.save(gold_data, indices_data, exchange_rate_data)

            # 短暂休眠以避免CPU占用过高
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n监控已停止")
        # 保存最终数据
        storage.save(gold_data, indices_data, exchange_rate_data)
        logger.info(f"数据已保存")
    except Exception as e:
        logger.error(f"监控过程中出错: {e}")
        # 尝试保存已收集的数据
        storage.save(gold_data, indices_data, exchange_rate_data)


def main():
    """主函数"""
    print("黄金价格、汇率和A股大盘指数监控程序")
    print("==============================")
    print("按 Ctrl+C 停止监控")
    print()
    
    # 设置不同资产的监控间隔（单位：秒）
    intervals = {
        'gold': 60,          # 每60秒获取一次黄金价格
        'indices': 60,      # 每60秒获取一次股指
        'exchange_rate': 60 * 60 # 每1小时获取一次汇率
    }
    monitor_prices(intervals)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"程序运行出错: {e}")
        raise
