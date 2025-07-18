#!/usr/bin/env python

"""
数据存储模块.

该模块定义了数据存储的基类和具体实现，用于处理数据的加载和保存。
"""

import logging
from pathlib import Path
from typing import Never

import pandas as pd

logger = logging.getLogger(__name__)


class Storage:
    """数据存储基类."""

    def load(self, *args, **kwargs) -> Never:
        """加载数据."""
        raise NotImplementedError

    def save(self, *args, **kwargs) -> Never:
        """保存数据."""
        raise NotImplementedError


class CsvStorage(Storage):
    """使用CSV文件进行数据存储."""

    def __init__(self, data_dir="./data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.gold_data_file = self.data_dir / "gold_price_data.csv"
        self.indices_data_file = self.data_dir / "stock_indices_data.csv"
        self.exchange_rate_data_file = self.data_dir / "exchange_rate_data.csv"

    def load(self):
        """从CSV文件加载数据."""
        gold_columns = ["price", "change", "change_percent", "time"]
        indices_columns = ["name", "price", "change", "change_percent", "time"]
        exchange_rate_columns = ["name", "price", "time"]

        gold_data = self._load_csv(self.gold_data_file, gold_columns, "黄金价格")
        indices_data = self._load_csv(self.indices_data_file, indices_columns, "股指")
        exchange_rate_data = self._load_csv(
            self.exchange_rate_data_file, exchange_rate_columns, "汇率"
        )

        return gold_data, indices_data, exchange_rate_data

    def _load_csv(self, file_path: Path, columns: list[str], data_name: str) -> pd.DataFrame:
        if file_path.exists():
            try:
                data = pd.read_csv(file_path)
                logger.info(f"已加载{data_name}数据，共{len(data)}条记录")
                return data
            except Exception as e:
                logger.error(f"加载{data_name}数据出错: {e}")
        return pd.DataFrame(columns=columns)

    def save(self, gold_data: pd.DataFrame, indices_data: pd.DataFrame, exchange_rate_data: pd.DataFrame) -> None:
        """将数据保存到CSV文件."""
        try:
            gold_data.to_csv(self.gold_data_file, index=False)
            indices_data.to_csv(self.indices_data_file, index=False)
            exchange_rate_data.to_csv(self.exchange_rate_data_file, index=False)
            logger.debug("数据已保存到CSV文件")
        except Exception as e:
            logger.error(f"保存数据出错: {e}")
