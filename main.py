#!/usr/bin/env python

"""
中美汇率和A股大盘指数监控程序.

该程序用于监控黄金价格、中美汇率和A股大盘指数的变动，并将数据保存到CSV文件中。
"""

# 标准库导入
import logging
import time
from datetime import datetime

# 第三方库导入
import pandas as pd

# 本地模块导入
from exchange_rate import get_exchange_rate
from gold import get_gold_price
from stock import get_all_indices
from storage import CsvStorage, Storage
from utils.logger import get_logger
from utils.scheduler import Scheduler

# 配置日志记录
logger = get_logger(__name__, "price_crawler.log", level=logging.INFO)


def fetch_gold_price(scheduler: Scheduler, gold_data: pd.DataFrame) -> bool:
    """获取黄金价格数据.

    Args:
        scheduler: 调度器实例。
        gold_data: 黄金价格数据DataFrame。

    Returns:
        bool: 是否成功获取并更新数据。
    """
    if not scheduler.should_fetch("gold"):
        return False

    gold_info = get_gold_price("Au9999")
    scheduler.update_fetch_time("gold")
    if gold_info:
        print(
            f"黄金价格: {gold_info['price']} 元/克 | 涨跌: {gold_info['change']} | 涨跌幅: {gold_info['change_percent']}%  | 更新时间: {gold_info.get('update_time', gold_info.get('update', '未知'))}"
        )
        gold_data.loc[len(gold_data)] = gold_info
        return True
    return False


def fetch_stock_indices(scheduler: Scheduler, indices_data: pd.DataFrame) -> bool:
    """获取股指数据.

    Args:
        scheduler: 调度器实例。
        indices_data: 股指数据DataFrame。

    Returns:
        bool: 是否成功获取并更新数据。
    """
    if not scheduler.should_fetch("indices"):
        return False

    all_indices = get_all_indices()
    scheduler.update_fetch_time("indices")
    if all_indices:
        for index_info in all_indices:
            print(
                f"{index_info['name']}: {index_info['price']} | 涨跌: {index_info['change']} | 涨跌幅: {index_info['change_percent']}%"
            )
            indices_data.loc[len(indices_data)] = index_info
        return True
    else:
        logger.info("当前为休市时间，不获取股指数据。")
        return False


def fetch_exchange_rate(scheduler: Scheduler, exchange_rate_data: pd.DataFrame, error_counts: dict, max_retries: int) -> tuple[bool, bool]:
    """获取中美汇率数据.

    Args:
        scheduler: 调度器实例。
        exchange_rate_data: 汇率数据DataFrame。
        error_counts: 错误计数字典。
        max_retries: 最大重试次数。

    Returns:
        tuple[bool, bool]: (是否成功获取并更新数据, 是否应该停止监控)。
    """
    if not scheduler.should_fetch("exchange_rate"):
        return False, False

    exchange_rate_info = get_exchange_rate()
    scheduler.update_fetch_time("exchange_rate")
    if exchange_rate_info:
        print(
            f"汇率: {exchange_rate_info['name']} | 描述: {exchange_rate_info['desc']} | 价格: {exchange_rate_info['price']} | 更新时间: {exchange_rate_info['update']}"
        )
        exchange_rate_data.loc[len(exchange_rate_data)] = exchange_rate_info
        error_counts["exchange_rate"] = 0  # 成功后重置计数器
        return True, False
    else:
        error_counts["exchange_rate"] += 1
        logger.warning("获取汇率数据失败，尝试次数: %s", error_counts['exchange_rate'])
        if error_counts["exchange_rate"] >= max_retries:
            logger.error("获取汇率数据连续失败次数过多，停止监控。")
            return False, True  # 返回失败且应该停止监控
        return False, False


def save_data(storage: 'Storage', gold_data: 'pd.DataFrame', indices_data: 'pd.DataFrame', exchange_rate_data: 'pd.DataFrame') -> None:
    """保存所有数据到存储.

    Args:
        storage: 存储实例，必须是Storage的子类实例。
        gold_data: 黄金价格数据。
        indices_data: 股指数据。
        exchange_rate_data: 汇率数据。
    """
    try:
        storage.save(gold_data, indices_data, exchange_rate_data)
        logger.debug("数据已成功保存")
    except OSError as e:
        logger.error("保存数据时文件操作错误: %s", e)
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有异常以确保监控循环不会因数据保存失败而中断
        logger.error("保存数据时出错: %s", e)


def monitor_prices(intervals: dict[str, int]) -> None:
    """监控价格变动.

    Args:
        intervals: 包含各类资产监控间隔的字典, e.g. {'gold': 1800, 'indices': 60, 'exchange_rate': 1800}.
    """
    logger.info("开始监控黄金价格、中美汇率和A股大盘指数...")
    logger.info("监控间隔: 黄金 %s s, 股指 %s s, 汇率 %s s", intervals.get('gold', 'N/A'), intervals.get('indices', 'N/A'), intervals.get('exchange_rate', 'N/A'))
    print("-" * 50)

    # 初始化数据存储
    storage = CsvStorage()

    # 加载已存在的数据
    gold_data, indices_data, exchange_rate_data = storage.load()

    # 初始化调度器
    scheduler = Scheduler(intervals)

    error_counts = {"gold": 0, "indices": 0, "exchange_rate": 0}
    max_retries = 3

    try:
        while True:
            data_updated = False

            # 获取黄金价格
            gold_updated = fetch_gold_price(scheduler, gold_data)
            data_updated = data_updated or gold_updated

            # 获取所有股指数据
            indices_updated = fetch_stock_indices(scheduler, indices_data)
            data_updated = data_updated or indices_updated

            # 获取汇率数据
            exchange_updated, should_stop = fetch_exchange_rate(
                scheduler, exchange_rate_data, error_counts, max_retries
            )
            data_updated = data_updated or exchange_updated

            if should_stop:
                break

            if data_updated:
                print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
                save_data(storage, gold_data, indices_data, exchange_rate_data)

            # 短暂休眠以避免CPU占用过高
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("\n监控已停止")
        # 保存最终数据
        save_data(storage, gold_data, indices_data, exchange_rate_data)
        logger.info("数据已保存")
    except Exception as e:  # pylint: disable=broad-except
        # 捕获所有异常以记录错误并尝试保存数据
        logger.error("监控过程中出错: %s", e)
        # 尝试保存已收集的数据
        save_data(storage, gold_data, indices_data, exchange_rate_data)


def main() -> None:
    """主函数."""
    print("黄金价格、中美汇率和A股大盘指数监控程序")
    print("==============================")
    print("按 Ctrl+C 停止监控")
    print()

    # 设置不同资产的监控间隔（单位：秒）
    intervals = {
        "gold": 30 * 60,  # 每半小时获取一次黄金价格
        "indices": 60,  # 每60秒获取一次股指
        "exchange_rate": 30 * 60,  # 每半小时获取一次汇率
    }
    monitor_prices(intervals)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # pylint: disable=broad-except
        # 主程序入口点需要捕获所有异常以确保错误被记录
        logger.critical("程序运行出错: %s", e)
        raise  # 重新抛出异常，允许程序以非零状态退出
