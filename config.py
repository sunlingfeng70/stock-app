"""全局配置：股票列表、策略参数"""

STOCKS = [
    {"code": "000001", "name": "平安银行"},
    {"code": "000002", "name": "万科A"},
    {"code": "600519", "name": "贵州茅台"},
    {"code": "300750", "name": "宁德时代"},
]

# 策略参数
STRATEGY = {
    "ma_short": 20,          # 短期均线
    "ma_long": 60,           # 长期均线
    "boll_period": 20,       # 布林带周期
    "boll_std": 2.0,         # 布林带标准差倍数
    "rsi_period": 14,        # RSI 周期
    "rsi_oversold": 30,      # RSI 超卖阈值
    "rsi_overbought": 70,    # RSI 超买阈值
    "volume_ma_period": 5,   # 均量周期
    "volume_surge_ratio": 1.2,  # 放量倍数阈值
}

# 行情数据获取天数
FETCH_DAYS = 365

# 数据库路径
DB_PATH = "stock_app.db"

# 仓位配比
POSITION = {
    "buy_ratio": 0.5,    # 首次买入仓位比例
    "add_ratio": 0.3,    # 加仓仓位比例
}