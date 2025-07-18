#!/usr/bin/env python

"""
数据存储模块.

该模块定义了数据存储的基类和具体实现，用于处理数据的加载和保存。
"""

import logging
from pathlib import Path
from typing import Any, Never

import pandas as pd

logger = logging.getLogger(__name__)


class Storage:
    """数据存储基类.
    
    定义了数据存储的基本接口，所有具体的存储实现都应该继承此类。
    """

    def load(self, *args: Any, **kwargs: Any) -> Never:  # noqa: ANN401
        """加载数据的抽象方法.
        
        Args:
            *args: 可变位置参数。
            **kwargs: 可变关键字参数。
            
        Returns:
            Never: 该方法不会返回，而是抛出异常。
            
        Raises:
            NotImplementedError: 该方法需要被子类实现。
        """
        raise NotImplementedError

    def save(self, *args: Any, **kwargs: Any) -> Never:  # noqa: ANN401
        """保存数据的抽象方法.
        
        Args:
            *args: 可变位置参数。
            **kwargs: 可变关键字参数。
            
        Returns:
            Never: 该方法不会返回，而是抛出异常。
            
        Raises:
            NotImplementedError: 该方法需要被子类实现。
        """
        raise NotImplementedError


class CsvStorage(Storage):
    """CSV文件存储实现类.
    
    继承自Storage基类，实现了使用CSV文件格式存储和加载数据的功能。
    """

    def __init__(self, data_dir: str = "./data") -> None:
        """初始化CSV存储对象.
        
        Args:
            data_dir: 数据存储目录路径，默认为"./data"。
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.gold_data_file = self.data_dir / "gold_price_data.csv"
        self.indices_data_file = self.data_dir / "stock_indices_data.csv"
        self.exchange_rate_data_file = self.data_dir / "exchange_rate_data.csv"

    def load(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """加载所有数据文件.
        
        从CSV文件中加载黄金价格、股指和汇率数据，包括价格、变化量、变化百分比和时间等信息。
        如果数据文件不存在，将返回空的DataFrame。
        
        Returns:
            tuple: 包含三个DataFrame的元组，按顺序分别为：
                - 黄金价格数据：包含price, change, change_percent, time列
                - 股指数据：包含name, price, change, change_percent, time列
                - 汇率数据：包含name, price, time列
        
        Example:
            >>> storage = CsvStorage()
            >>> gold_data, indices_data, exchange_rate_data = storage.load()
            >>> print(f"加载了{len(gold_data)}条黄金价格数据")
        """
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
        """从CSV文件加载数据.
        
        如果文件存在，尝试读取CSV文件内容；如果文件不存在或读取出错，
        则返回一个包含指定列名的空DataFrame。
        
        Args:
            file_path: CSV文件路径。
            columns: 数据列名列表。
            data_name: 数据名称，用于日志记录。
            
        Returns:
            pd.DataFrame: 加载的数据，如果加载失败则返回空DataFrame。
        """
        if file_path.exists():
            try:
                data = pd.read_csv(file_path)
                logger.info(f"已加载{data_name}数据，共{len(data)}条记录")
                return data
            except Exception as e:
                logger.error(f"加载{data_name}数据出错: {e}")
        return pd.DataFrame(columns=columns)

    def save(self, gold_data: pd.DataFrame, indices_data: pd.DataFrame, exchange_rate_data: pd.DataFrame) -> None:
        """保存所有数据到CSV文件.
        
        将黄金价格、股指和汇率数据保存到对应的CSV文件中。
        
        Args:
            gold_data: 黄金价格数据DataFrame。
            indices_data: 股指数据DataFrame。
            exchange_rate_data: 汇率数据DataFrame。
            
        Raises:
            Exception: 保存数据过程中发生的任何异常。
        """
        try:
            gold_data.to_csv(self.gold_data_file, index=False)
            indices_data.to_csv(self.indices_data_file, index=False)
            exchange_rate_data.to_csv(self.exchange_rate_data_file, index=False)
            logger.debug("数据已保存到CSV文件")
        except Exception as e:
            logger.error(f"保存数据出错: {e}")
