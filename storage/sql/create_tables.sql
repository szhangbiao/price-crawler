-- 价格数据表
CREATE TABLE IF NOT EXISTS gold_price (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 主键ID
    type INTEGER, -- values(0 gold,1 stock,2 exchange_rate)
    code TEXT NOT NULL, -- 代码
    name TEXT NOT NULL, -- 名称
    latest_price REAL, -- 最新价
    change_amount REAL, -- 涨跌额
    change_percent REAL, -- 涨跌幅(%)
    open_price REAL, -- 开盘价
    highest_price REAL, -- 最高价
    lowest_price REAL, -- 最低价
    latest_time TEXT NOT NULL, -- 更新时间
    unit TEXT, -- 单位
    source INTEGER, -- values(00:金投网爬虫,01:GoldPricez爬虫,02:聚合API|10:金投网爬虫,11:新浪API|20:金投网爬虫,21:聚合API,22:MXNZP_API)
    remark TEXT, -- 额外说明
    update_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 修改时间
    create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP -- 创建时间
);

-- 创建代码索引
CREATE INDEX idx_code ON gold_price(code);