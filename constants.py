# coding: utf-8
"""
常量定义模块

提供项目中使用的所有常量定义，便于维护和修改。

@author: OsKhQuant
@version: 1.0
"""

from enum import Enum


# ============================================================================
# 交易日历常量
# ============================================================================

class TradeCalendar:
    """交易日历相关常量"""

    # 交易所代码
    EXCHANGE_SHanghai = "SH"
    EXCHANGE_SHENZHEN = "SZ"

    # 交易时间（24小时制）
    TRADING_HOURS_START = "09:30"
    TRADING_HOURS_END = "15:00"
    TRADING_HOURS_MORNING_START = "09:30"
    TRADING_HOURS_MORNING_END = "11:30"
    TRADING_HOURS_AFTERNOON_START = "13:00"
    TRADING_HOURS_AFTERNOON_END = "15:00"

    # 午休时间
    LUNCH_BREAK_START = "11:30"
    LUNCH_BREAK_END = "13:00"

    # 竞价时间
    AUCTION_START = "09:15"
    AUCTION_END = "09:25"


# ============================================================================
# 交易常量
# ============================================================================

class Trading:
    """交易相关常量"""

    # 初始资金默认值
    DEFAULT_INIT_CAPITAL = 1_000_000

    # 佣金
    COMMISSION_RATE = 0.0003  # 万三
    MIN_COMMISSION = 5.0  # 最低佣金5元

    # 印花税
    STAMP_TAX_RATE = 0.001  # 千一，仅卖出收取

    # 过户费
    TRANSFER_FEE_RATE = 0.00002  # 万二

    # 默认风控参数
    DEFAULT_POSITION_LIMIT = 0.95  # 持仓比例限制95%
    DEFAULT_ORDER_LIMIT = 100  # 日委托次数限制
    DEFAULT_LOSS_LIMIT = 0.1  # 止损线10%
    DEFAULT_DRAWDOWN_LIMIT = 0.15  # 最大回撤限制15%
    DEFAULT_SINGLE_ORDER_LIMIT = 0.3  # 单笔委托限制30%
    DEFAULT_DAILY_LOSS_LIMIT = 0.05  # 日亏损限制5%


# ============================================================================
# 数据周期常量
# ============================================================================

class DataPeriod:
    """数据周期常量"""

    TICK = "tick"
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    HOURLY = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"

    # 周期映射
    PERIOD_MAP = {
        TICK: "Tick",
        ONE_MINUTE: "1分钟",
        FIVE_MINUTES: "5分钟",
        FIFTEEN_MINUTES: "15分钟",
        THIRTY_MINUTES: "30分钟",
        HOURLY: "1小时",
        DAILY: "日线",
        WEEKLY: "周线",
        MONTHLY: "月线",
    }

    # 数据周期选项（用于界面显示）
    PERIOD_OPTIONS = [
        (TICK, PERIOD_MAP[TICK]),
        (ONE_MINUTE, PERIOD_MAP[ONE_MINUTE]),
        (FIVE_MINUTES, PERIOD_MAP[FIVE_MINUTES]),
        (DAILY, PERIOD_MAP[DAILY]),
    ]


# ============================================================================
# 复权常量
# ============================================================================

class DividendType:
    """复权类型常量"""

    NONE = "none"  # 不复权
    FORWARD = "qfq"  # 前复权
    BACKWARD = "hfq"  # 后复权

    # 显示名称映射
    NAME_MAP = {
        NONE: "不复权",
        FORWARD: "前复权",
        BACKWARD: "后复权",
    }

    # 默认复权方式
    DEFAULT = FORWARD


# ============================================================================
# 触发器类型常量
# ============================================================================

class TriggerType:
    """触发器类型常量"""

    TICK = "tick"
    KLINE = "kline"
    CUSTOM = "custom"

    # 显示名称映射
    NAME_MAP = {
        TICK: "Tick触发",
        KLINE: "K线触发",
        CUSTOM: "自定义时间触发",
    }


# ============================================================================
# 交易方向常量
# ============================================================================

class OrderDirection:
    """交易方向常量"""

    BUY = "buy"
    SELL = "sell"

    # 中文名称
    NAME_MAP = {
        BUY: "买入",
        SELL: "卖出",
    }


# ============================================================================
# 日志级别常量
# ============================================================================

class LogLevel:
    """日志级别常量"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # 数值映射（用于比较）
    LEVEL_MAP = {
        DEBUG: 10,
        INFO: 20,
        WARNING: 30,
        ERROR: 40,
        CRITICAL: 50,
    }


# ============================================================================
# 文件路径常量
# ============================================================================

class FilePath:
    """文件路径相关常量"""

    # 配置目录
    CONFIG_DIR = "config"
    CONFIG_FILE = "config.json"

    # 数据目录
    DATA_DIR = "data"

    # 日志目录
    LOG_DIR = "logs"

    # 缓存目录
    CACHE_DIR = "cache"

    # 图标目录
    ICONS_DIR = "icons"

    # 策略目录
    STRATEGIES_DIR = "strategies"

    # 临时目录
    TEMP_DIR = "temp"

    # 默认配置文件名
    DEFAULT_CONFIG = "config.json"

    # 股票列表文件名
    STOCK_LIST_FILE = "stock_list.txt"


# ============================================================================
# 文件大小常量
# ============================================================================

class FileSize:
    """文件大小常量"""

    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB

    # 默认日志文件大小
    DEFAULT_LOG_SIZE = 10 * MB

    # 最大日志文件大小
    MAX_LOG_SIZE = 50 * MB


# ============================================================================
# 时间常量
# ============================================================================

class TimeConstant:
    """时间相关常量"""

    # 毫秒转换
    MS_PER_SECOND = 1000
    MS_PER_MINUTE = 60 * MS_PER_SECOND
    MS_PER_HOUR = 60 * MS_PER_MINUTE

    # 默认时间格式
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    # 文件名时间格式
    FILENAME_DATE_FORMAT = "%Y%m%d"

    # MiniQMT时间格式
    XT_DATE_FORMAT = "%Y%m%d"


# ============================================================================
# 状态常量
# ============================================================================

class Status:
    """状态常量"""

    # 成功/失败
    SUCCESS = "success"
    FAILED = "failed"

    # 运行状态
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"

    # 连接状态
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


# ============================================================================
# 错误代码常量
# ============================================================================

class ErrorCode:
    """错误代码常量"""

    # 通用错误
    SUCCESS = 0
    UNKNOWN_ERROR = 1

    # 配置错误
    CONFIG_LOAD_FAILED = 1001
    CONFIG_SAVE_FAILED = 1002
    CONFIG_INVALID = 1003

    # 数据错误
    DATA_DOWNLOAD_FAILED = 2001
    DATA_PARSE_FAILED = 2002
    DATA_NOT_FOUND = 2003

    # 交易错误
    ORDER_FAILED = 3001
    INSUFFICIENT_FUNDS = 3002
    INSUFFICIENT_POSITION = 3003

    # 风控错误
    RISK_CHECK_FAILED = 4001
    POSITION_LIMIT_EXCEEDED = 4002
    ORDER_LIMIT_EXCEEDED = 4003

    # 安全错误
    SECURITY_CHECK_FAILED = 5001
    INVALID_STRATEGY = 5002


# ============================================================================
# 界面常量
# ============================================================================

class UI:
    """界面相关常量"""

    # 窗口标题
    WINDOW_TITLE = "看海量化交易系统"
    WINDOW_TITLE_PATTERN = "{} - {}".format(WINDOW_TITLE, "{}")

    # 窗口大小
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600

    # 字体设置
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 14
    HEADER_FONT_SIZE = 12

    # 颜色设置
    PRIMARY_COLOR = "#007bff"
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#dc3545"
    INFO_COLOR = "#17a2b8"

    # 背景色
    DARK_BG_COLOR = "#2b2b2b"
    LIGHT_BG_COLOR = "#f8f9fa"


# ============================================================================
# 便捷访问
# ============================================================================

# 导出常用常量，方便直接访问
TRADING_HOURS = (
    TradeCalendar.TRADING_HOURS_MORNING_START,
    TradeCalendar.TRADING_HOURS_MORNING_END,
    TradeCalendar.TRADING_HOURS_AFTERNOON_START,
    TradeCalendar.TRADING_HOURS_AFTERNOON_END,
)

DEFAULT_RISK_CONFIG = {
    'position_limit': Trading.DEFAULT_POSITION_LIMIT,
    'order_limit': Trading.DEFAULT_ORDER_LIMIT,
    'loss_limit': Trading.DEFAULT_LOSS_LIMIT,
    'drawdown_limit': Trading.DEFAULT_DRAWDOWN_LIMIT,
    'single_order_limit': Trading.DEFAULT_SINGLE_ORDER_LIMIT,
    'daily_loss_limit': Trading.DEFAULT_DAILY_LOSS_LIMIT,
}
