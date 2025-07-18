#!/usr/bin/env python

"""
数据存储基类模块.

该模块定义了数据存储的基类接口，所有具体的存储实现都应该继承此类。
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class Storage:
    """数据存储基类.
    
    定义了数据存储的基本接口，所有具体的存储实现都应该继承此类。
    """

    def load(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """加载数据的抽象方法.
        
        该方法需要被子类实现，用于从存储介质加载数据。
        
        Returns:
            tuple: 包含三个DataFrame的元组，按顺序分别为：
                - 黄金价格数据
                - 股指数据
                - 汇率数据
        
        Raises:
            NotImplementedError: 该方法需要被子类实现。
        """
        raise NotImplementedError

    def save(self, gold_data: pd.DataFrame, indices_data: pd.DataFrame, exchange_rate_data: pd.DataFrame) -> None:
        """保存数据的抽象方法.
        
        该方法需要被子类实现，用于将数据保存到存储介质。
        
        Args:
            gold_data: 黄金价格数据DataFrame。
            indices_data: 股指数据DataFrame。
            exchange_rate_data: 汇率数据DataFrame。
        
        Raises:
            NotImplementedError: 该方法需要被子类实现。
        """
        raise NotImplementedError