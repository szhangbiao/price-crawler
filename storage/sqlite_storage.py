#!/usr/bin/env python

"""
SQLite数据库存储实现模块.

该模块实现了使用SQLite数据库存储和加载数据的功能。
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from storage.base import Storage

logger = logging.getLogger(__name__)


class SqliteStorage(Storage):
    """SQLite数据库存储实现类.
    
    继承自Storage基类，实现了使用SQLite数据库存储和加载数据的功能。
    """

    def __init__(self, db_path: str = "./data/price_data.db") -> None:
        """初始化SQLite存储对象.
        
        Args:
            db_path: SQLite数据库文件路径，默认为"./data/price_data.db"。
        """
        self.db_path = Path(db_path)
        # 确保数据目录存在
        self.db_path.parent.mkdir(exist_ok=True)
        
        # SQL文件目录
        self.sql_dir = Path(__file__).parent / "sql"
        
        # 初始化数据库连接和表结构
        self._init_database()

    def _init_database(self) -> None:
        """初始化数据库连接和表结构.
        
        创建数据库连接并执行SQL文件中的建表语句。
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 加载并执行SQL文件
            sql_file_path = self.sql_dir / "create_tables.sql"
            if not sql_file_path.exists():
                logger.error("SQL文件不存在: %s", sql_file_path)
                return
                
            with open(sql_file_path, encoding="utf-8") as f:
                sql_content = f.read()
                
            cursor.executescript(sql_content)
            conn.commit()
            logger.info("数据库初始化成功: %s", self.db_path)
        except sqlite3.Error as e:
            logger.error("数据库初始化失败: %s", e)
        except OSError as e:
            logger.error("读取SQL文件出错: %s", e)
        finally:
            if conn:
                conn.close()

    def load(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """从SQLite数据库加载数据.
        
        从数据库中加载黄金价格、股指和汇率数据。
        
        Returns:
            tuple: 包含三个DataFrame的元组，按顺序分别为：
                - 黄金价格数据
                - 股指数据
                - 汇率数据
        """
        gold_data = pd.DataFrame()
        indices_data = pd.DataFrame()
        exchange_rate_data = pd.DataFrame()
        
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 加载黄金价格数据
            gold_data = pd.read_sql_query(
                "SELECT * FROM gold_price WHERE type = 0 ORDER BY latest_time DESC",
                conn
            )
            
            # 加载股指数据
            indices_data = pd.read_sql_query(
                "SELECT * FROM gold_price WHERE type = 1 ORDER BY latest_time DESC",
                conn
            )
            
            # 加载汇率数据
            exchange_rate_data = pd.read_sql_query(
                "SELECT * FROM gold_price WHERE type = 2 ORDER BY latest_time DESC",
                conn
            )
            
            logger.info("已加载黄金价格数据，共%s条记录", len(gold_data))
            logger.info("已加载股指数据，共%s条记录", len(indices_data))
            logger.info("已加载汇率数据，共%s条记录", len(exchange_rate_data))
            
        except sqlite3.Error as e:
            logger.error("从数据库加载数据出错: %s", e)
        finally:
            if conn:
                conn.close()
        
        return gold_data, indices_data, exchange_rate_data

    def save(self, gold_data: pd.DataFrame, indices_data: pd.DataFrame, exchange_rate_data: pd.DataFrame) -> None:
        """保存数据到SQLite数据库.
        
        将黄金价格、股指和汇率数据保存到数据库中。
        
        Args:
            gold_data: 黄金价格数据DataFrame。
            indices_data: 股指数据DataFrame。
            exchange_rate_data: 汇率数据DataFrame。
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 保存黄金价格数据
            if not gold_data.empty:
                self._save_gold_data(cursor, gold_data, data_type=0)
            
            # 保存股指数据
            if not indices_data.empty:
                self._save_gold_data(cursor, indices_data, data_type=1)
            
            # 保存汇率数据
            if not exchange_rate_data.empty:
                self._save_gold_data(cursor, exchange_rate_data, data_type=2)
            
            conn.commit()
            logger.info("数据已成功保存到数据库")
            
        except sqlite3.Error as e:
            logger.error("保存数据到数据库出错: %s", e)
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def _save_gold_data(self, cursor: sqlite3.Cursor, data: pd.DataFrame, data_type: int) -> None:
        """保存数据到gold_price表.
        
        Args:
            cursor: SQLite游标对象。
            data: 要保存的数据DataFrame。
            data_type: 数据类型，0表示黄金价格，1表示股指，2表示汇率。
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, row in data.iterrows():
            # 检查记录是否已存在
            cursor.execute(
                "SELECT id FROM gold_price WHERE code = ? AND type = ? AND latest_time = ?",
                (row.get("code", ""), data_type, row.get("time", current_time))
            )
            result = cursor.fetchone()
            
            if result:
                # 更新现有记录
                cursor.execute(
                    """UPDATE gold_price SET 
                    name = ?, latest_price = ?, change_amount = ?, change_percent = ?,
                    open_price = ?, highest_price = ?, lowest_price = ?,
                    unit = ?, update_time = ? 
                    WHERE id = ?""",
                    (
                        row.get("name", ""),
                        row.get("price", 0),
                        row.get("change", 0),
                        row.get("change_percent", 0),
                        row.get("open", 0),
                        row.get("high", 0),
                        row.get("low", 0),
                        row.get("unit", ""),
                        current_time,
                        result[0]
                    )
                )
            else:
                # 插入新记录
                cursor.execute(
                    """INSERT INTO gold_price 
                    (type, code, name, latest_price, change_amount, change_percent,
                    open_price, highest_price, lowest_price, latest_time, unit, update_time) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        data_type,
                        row.get("code", ""),
                        row.get("name", ""),
                        row.get("price", 0),
                        row.get("change", 0),
                        row.get("change_percent", 0),
                        row.get("open", 0),
                        row.get("high", 0),
                        row.get("low", 0),
                        row.get("time", current_time),
                        row.get("unit", ""),
                        current_time
                    )
                )