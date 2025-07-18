"""任务调度模块.

该模块提供了任务调度功能，包括判断A股交易时间和管理不同数据的获取时间间隔。

包含以下主要功能：
- is_market_open: 判断当前是否为A股交易时间。
- Scheduler: 管理不同数据类型的获取频率和调度。

注意：
- 股指数据仅在A股交易时间获取。
- 黄金和汇率数据不受交易时间限制。
"""

import logging
import time
from datetime import datetime
from datetime import time as time_obj

import chinese_calendar as chinesecalendar

# 获取logger
logger = logging.getLogger(__name__)


def is_market_open() -> bool:
    """检查当前是否为A股交易时间（包括节假日判断）.
    
    Returns:
        bool: 如果当前是交易时间则返回True，否则返回False。
    """
    now = datetime.now()
    logger.debug("检查市场开放状态: 当前时间 %s", now)

    # 检查是否为工作日（排除法定节假日）
    if not chinesecalendar.is_workday(now.date()):
        logger.info("%s 不是工作日，市场关闭", now.date())
        return False

    # 检查是否为周一至周五
    if now.weekday() >= 5:
        logger.info("%s 是周末，市场关闭", now.date())
        return False

    # 检查交易时间段
    current_time = now.time()
    morning_start = time_obj(9, 25)
    morning_end = time_obj(11, 30)
    afternoon_start = time_obj(13, 0)
    afternoon_end = time_obj(15, 0)

    if (morning_start <= current_time <= morning_end) or (
        afternoon_start <= current_time <= afternoon_end
    ):
        logger.debug("当前时间 %s 在交易时段内，市场开放", current_time)
        return True

    logger.info("当前时间 %s 不在交易时段内，市场关闭", current_time)
    return False


class Scheduler:
    """负责调度任务的类.
    
    负责管理不同数据（黄金、股指、汇率）的获取时间间隔和最后获取时间。
    """

    def __init__(self, intervals: dict[str, int]) -> None:
        """初始化调度器.
        
        Args:
            intervals: 包含各类资产监控间隔的字典，键为资产名称，值为间隔秒数。
        """
        self.intervals = intervals
        self.last_fetch_times = {"gold": 0, "indices": 0, "exchange_rate": 0}

    def should_fetch(self, asset_name: str) -> bool:
        """根据资产名称和时间间隔判断是否应该获取数据.
        
        Args:
            asset_name: 资产名称，可以是'gold'、'indices'或'exchange_rate'。
            
        Returns:
            bool: 如果应该获取数据则返回True，否则返回False。
        """
        current_time = time.time()
        time_since_last_fetch = current_time - self.last_fetch_times[asset_name]
        interval = self.intervals.get(asset_name, 60)

        logger.debug(
            "检查是否应获取 %s 数据: 上次获取时间: %s, 间隔: %s秒, 已过时间: %.1f秒",
            asset_name, self.last_fetch_times[asset_name], interval, time_since_last_fetch
        )

        if time_since_last_fetch >= interval:
            if asset_name == "indices" and not is_market_open():
                logger.info("当前为休市时间，跳过获取股指数据")
                return False  # 休市期间不获取股指数据
            logger.debug("应该获取 %s 数据", asset_name)
            return True

        logger.debug(
            "暂不需要获取 %s 数据，距离下次获取还有 %.1f 秒",
            asset_name, interval - time_since_last_fetch
        )
        return False

    def update_fetch_time(self, asset_name: str) -> None:
        """更新资产的最后获取时间.
        
        Args:
            asset_name: 资产名称，可以是'gold'、'indices'或'exchange_rate'。
        """
        current_time = time.time()
        self.last_fetch_times[asset_name] = current_time
        logger.debug(
            "已更新 %s 的最后获取时间: %s (%s)",
            asset_name, current_time, datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        )
        logger.debug(
            "下次获取 %s 数据的时间: %s",
            asset_name, datetime.fromtimestamp(current_time + self.intervals.get(asset_name, 60)).strftime('%Y-%m-%d %H:%M:%S')
        )