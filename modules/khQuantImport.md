# khQuantImport模块 - 统一导入和便捷函数

## 📋 模块概述

**文件**: `khQuantImport.py` (521行)
**功能**: 量化交易策略开发的一站式导入模块，提供统一的API接口和便捷函数
**设计理念**: 简化策略开发，提供`from khQuantImport import *`即可获取所有必需工具
**核心价值**: 减少学习成本，提高开发效率，统一开发体验

## 🏗️ 模块架构

### 导入层次结构
```
khQuantImport
├── 标准库导入 (os, sys, json, logging, datetime, typing)
├── 数据处理库 (numpy, pandas)
├── 量化核心库 (xtquant, xttrader)
├── 项目工具 (khQTTools, MyTT)
├── 核心类 (TimeInfo, StockDataParser, PositionParser, StockPoolParser, StrategyContext)
└── 便捷函数 (khGet, khPrice, khHas, khBuy, khSell)
```

### 核心组件关系
```python
# 统一导入的设计理念
from khQuantImport import *  # 一行代码获取所有工具

# 自动可用的组件
- 所有标准库和数据处理库
- 完整的量化工具集 (khQTTools)
- 技术指标库 (MyTT)
- 便捷函数和解析器类
- 时间和数据处理工具
```

## 🔧 核心类详解

### 1. TimeInfo - 时间信息解析类
```python
class TimeInfo:
    """标准化的时间信息类

    提供统一的时间访问接口，支持多种时间格式转换
    """

    def __init__(self, data: Dict):
        self._data = data
        self._current_time = data.get("__current_time__", {})

    @property
    def date_str(self) -> str:
        """返回标准日期格式: 2024-01-15"""
        return self._current_time.get("date", "")

    @property
    def date_num(self) -> str:
        """返回数字日期格式: 20240115"""
        date_str = self.date_str
        return date_str.replace("-", "") if date_str else ""

    @property
    def time_str(self) -> str:
        """返回时间格式: 09:30:00"""
        return self._current_time.get("time", "")

    @property
    def datetime_str(self) -> str:
        """返回完整日期时间: 2024-01-15 09:30:00"""
        if self.date_str and self.time_str:
            return f"{self.date_str} {self.time_str}"
        return ""

    @property
    def datetime_num(self) -> str:
        """返回数字日期时间: 20240115093000"""
        if self.date_num and self.time_str:
            time_num = self.time_str.replace(":", "")
            return f"{self.date_num}{time_num}"
        return ""

    @property
    def datetime_obj(self) -> Optional[dt]:
        """返回datetime对象"""
        if self.datetime_str:
            try:
                return dt.strptime(self.datetime_str, "%Y-%m-%d %H:%M:%S")
            except:
                pass
        return None

    @property
    def timestamp(self) -> Optional[float]:
        """返回时间戳"""
        return self._current_time.get("timestamp")
```

**使用示例**:
```python
def init(stock_list, context):
    time_info = TimeInfo(context)

    print(f"策略初始化日期: {time_info.date_str}")
    print(f"数字日期: {time_info.date_num}")
    print(f"当前时间: {time_info.time_str}")
    print(f"完整时间: {time_info.datetime_str}")
    print(f"时间戳: {time_info.timestamp}")

    # 判断是否为交易时间
    if "09:30:00" <= time_info.time_str <= "15:00:00":
        print("当前为交易时间")
```

### 2. StockDataParser - 股票数据解析器
```python
class StockDataParser:
    """股票数据解析器

    提供统一的股票数据访问接口，处理不同数据格式的兼容性
    """

    def __init__(self, data: Dict):
        self._data = data

    def get_price(self, stock_code: str, field: str = "close") -> float:
        """获取指定股票的价格数据

        Args:
            stock_code: 股票代码，如 '000001.SZ'
            field: 价格字段，默认为'close'，支持'open','high','low','close','volume'

        Returns:
            float: 价格值，获取失败返回0.0

        注意:
            - 自动处理pandas Series和字典格式
            - 包含完整的错误处理和数据验证
            - 返回float类型，方便数值计算
        """
        try:
            stock_data = self.get(stock_code)

            # 空值检查
            if stock_data is None:
                return 0.0

            # pandas Series处理
            if hasattr(stock_data, 'empty'):
                if stock_data.empty:
                    return 0.0

            # 获取字段值
            value = None
            if hasattr(stock_data, 'get'):
                value = stock_data.get(field, 0.0)
            elif hasattr(stock_data, field):
                value = getattr(stock_data, field)
            elif hasattr(stock_data, '__getitem__'):
                try:
                    value = stock_data[field]
                except (KeyError, IndexError):
                    return 0.0
            else:
                return 0.0

            # 转换为float并验证
            result = float(value)
            if np.isnan(result) or np.isinf(result):
                return 0.0
            return result

        except Exception as e:
            logging.debug(f"获取股票{stock_code}的{field}数据失败: {str(e)}")
            return 0.0

    # 便捷方法
    def get_close(self, stock_code: str) -> float:
        """获取收盘价"""
        return self.get_price(stock_code, "close")

    def get_open(self, stock_code: str) -> float:
        """获取开盘价"""
        return self.get_price(stock_code, "open")

    def get_high(self, stock_code: str) -> float:
        """获取最高价"""
        return self.get_price(stock_code, "high")

    def get_low(self, stock_code: str) -> float:
        """获取最低价"""
        return self.get_price(stock_code, "low")

    def get_volume(self, stock_code: str) -> float:
        """获取成交量"""
        return self.get_price(stock_code, "volume")
```

**使用示例**:
```python
def khHandlebar(context):
    stocks = StockDataParser(context)

    # 获取平安银行的价格数据
    stock_code = '000001.SZ'
    current_price = stocks.get_close(stock_code)
    open_price = stocks.get_open(stock_code)
    high_price = stocks.get_high(stock_code)
    low_price = stocks.get_low(stock_code)
    volume = stocks.get_volume(stock_code)

    print(f"当前价: {current_price}, 开盘价: {open_price}")
    print(f"最高价: {high_price}, 最低价: {low_price}, 成交量: {volume}")
```

### 3. PositionParser - 持仓数据解析器
```python
class PositionParser:
    """持仓数据解析器

    提供统一的持仓信息访问接口
    """

    def __init__(self, data: Dict):
        self._positions = data.get("__positions__", {})

    def has(self, stock_code: str) -> bool:
        """检查是否持有某股票

        Args:
            stock_code: 股票代码

        Returns:
            bool: 是否持有该股票且数量大于0
        """
        position = self._positions.get(stock_code, {})
        return position.get("volume", 0) > 0

    def get_volume(self, stock_code: str) -> float:
        """获取持仓数量"""
        return self._positions.get(stock_code, {}).get("volume", 0)

    def get_cost(self, stock_code: str) -> float:
        """获取持仓成本价"""
        return self._positions.get(stock_code, {}).get("avg_price", 0)

    def get_profit_ratio(self, stock_code: str) -> float:
        """获取持仓盈亏率"""
        position = self._positions.get(stock_code, {})
        return position.get("profit_ratio", 0)

    def get_all(self) -> Dict:
        """获取所有持仓信息"""
        return self._positions.copy()
```

**使用示例**:
```python
def khHandlebar(context):
    positions = PositionParser(context)

    # 检查是否持有平安银行
    stock_code = '000001.SZ'
    if positions.has(stock_code):
        volume = positions.get_volume(stock_code)
        cost_price = positions.get_cost(stock_code)
        profit_ratio = positions.get_profit_ratio(stock_code)

        print(f"持有{stock_code}: {volume}股, 成本价: {cost_price}, 盈亏率: {profit_ratio:.2%}")

        # 止盈止损逻辑
        if profit_ratio > 0.2:  # 盈利20%止盈
            return [khSell(context, stock_code, 1.0, "止盈")]
        elif profit_ratio < -0.1:  # 亏损10%止损
            return [khSell(context, stock_code, 1.0, "止损")]
```

### 4. StrategyContext - 策略上下文类
```python
class StrategyContext:
    """策略上下文，提供便捷的数据访问和信号生成方法

    整合所有解析器，提供统一的策略开发接口
    """

    def __init__(self, data: Dict):
        self.data = data
        self.time = TimeInfo(data)
        self.stocks = StockDataParser(data)
        self.positions = PositionParser(data)
        self.pool = StockPoolParser(data)

    def buy_signal(self, stock_code: str, ratio: float = 1.0,
                   volume: Optional[int] = None, reason: str = "") -> Dict:
        """生成买入信号

        Args:
            stock_code: 股票代码
            ratio: 资金使用比例，默认1.0(全仓)
            volume: 指定买入数量，如果提供则忽略ratio
            reason: 买入原因

        Returns:
            Dict: 买入信号字典，失败返回空字典
        """
        current_price = self.stocks.get_close(stock_code)
        if current_price <= 0:
            logging.warning(f"无法获取股票{stock_code}的价格信息")
            return {}

        if reason == "":
            reason = f"策略买入{stock_code}"

        signals = generate_signal(self.data, stock_code, current_price, ratio, 'buy', reason)
        return signals[0] if signals else {}

    def sell_signal(self, stock_code: str, ratio: float = 1.0,
                    volume: Optional[int] = None, reason: str = "") -> Dict:
        """生成卖出信号

        Args:
            stock_code: 股票代码
            ratio: 卖出比例，默认1.0(全部卖出)
            volume: 指定卖出数量，如果提供则忽略ratio
            reason: 卖出原因

        Returns:
            Dict: 卖出信号字典，失败返回空字典
        """
        current_price = self.stocks.get_close(stock_code)
        if current_price <= 0:
            logging.warning(f"无法获取股票{stock_code}的价格信息")
            return {}

        if reason == "":
            reason = f"策略卖出{stock_code}"

        signals = generate_signal(self.data, stock_code, current_price, ratio, 'sell', reason)
        return signals[0] if signals else {}
```

## 🔧 便捷函数详解

### 1. khGet - 通用数据获取函数
```python
def khGet(data: Dict, key: str) -> Any:
    """通用的数据获取函数

    支持多种简洁格式的数据访问，简化策略代码

    Args:
        data: 策略数据字典
        key: 要获取的数据键，支持以下格式：
            - 'date', 'date_str': 获取日期字符串 "2024-01-15"
            - 'date_num': 获取数字日期 "20240115"
            - 'time', 'time_str': 获取时间字符串 "09:30:00"
            - 'datetime', 'datetime_str': 获取完整日期时间
            - 'cash': 获取可用资金
            - 'total_asset': 获取总资产
            - 'market_value': 获取持仓市值
            - 'stocks': 获取所有股票代码
            - 'first_stock': 获取第一个股票代码
            - 'positions': 获取所有持仓信息

    Returns:
        Any: 对应的数据值，获取失败返回None
    """
    # 时间相关
    if key in ["date", "date_str", "time", "time_str", "datetime", "datetime_str", "date_num", "timestamp", "datetime_obj"]:
        time_info = TimeInfo(data)
        if key in ["date", "date_str"]:
            return time_info.date_str
        elif key == "date_num":
            return time_info.date_num
        elif key in ["time", "time_str"]:
            return time_info.time_str
        elif key in ["datetime", "datetime_str"]:
            return time_info.datetime_str
        elif key == "timestamp":
            return time_info.timestamp
        elif key == "datetime_obj":
            return time_info.datetime_obj

    # 股票池相关
    elif key in ["first_stock", "stocks"]:
        pool = StockPoolParser(data)
        if key == "first_stock":
            return pool.first()
        elif key == "stocks":
            return pool.get_all()

    # 账户相关
    elif key in ["cash", "total_asset", "market_value"]:
        account = data.get("__account__", {})
        return account.get(key, 0)

    # 持仓相关
    elif key == "positions":
        positions = PositionParser(data)
        return positions.get_all()

    # 直接获取
    try:
        return data.get(key)
    except (AttributeError, TypeError):
        return None
```

**使用示例**:
```python
def khHandlebar(context):
    # 时间相关
    current_date = khGet(context, 'date_str')      # "2024-01-15"
    current_time = khGet(context, 'time_str')      # "09:30:00"
    datetime_str = khGet(context, 'datetime_str')  # "2024-01-15 09:30:00"

    # 账户信息
    cash = khGet(context, 'cash')                   # 可用资金
    total_asset = khGet(context, 'total_asset')     # 总资产
    market_value = khGet(context, 'market_value')   # 持仓市值

    # 股票池
    stocks = khGet(context, 'stocks')               # 所有股票代码
    first_stock = khGet(context, 'first_stock')     # 第一个股票代码

    print(f"日期: {current_date}, 时间: {current_time}")
    print(f"可用资金: {cash:.2f}, 总资产: {total_asset:.2f}")
    print(f"股票池: {stocks}")
```

### 2. khPrice - 股票价格获取函数
```python
def khPrice(data: Dict, stock_code: str, field: str = 'close') -> float:
    """获取股票价格的便捷函数

    统一的价格获取接口，处理各种数据格式和异常情况

    Args:
        data: 策略数据字典
        stock_code: 股票代码，如 '000001.SZ'
        field: 价格字段，默认为'close'

    Returns:
        float: 股票价格，获取失败返回0.0
    """
    try:
        stocks = StockDataParser(data)
        price = stocks.get_price(stock_code, field)

        # 空值检查
        if price is None:
            return 0.0

        # pandas Series处理
        if hasattr(price, 'iloc'):
            try:
                if len(price) > 0:
                    price_val = price.iloc[-1]
                else:
                    return 0.0
            except Exception:
                return 0.0

        # 数组处理
        elif hasattr(price, '__len__') and not isinstance(price, str):
            try:
                if len(price) > 0:
                    price_val = price[-1]
                else:
                    return 0.0
            except Exception:
                return 0.0
        else:
            price_val = price

        # 数值验证和转换
        try:
            result = float(price_val)
            if np.isnan(result) or np.isinf(result):
                return 0.0
            return result
        except (ValueError, TypeError):
            return 0.0

    except Exception as e:
        logging.error(f"获取股票{stock_code}价格失败: {str(e)}")
        return 0.0
```

### 3. khHas - 持仓检查函数
```python
def khHas(data: Dict, stock_code: str) -> bool:
    """检查是否持有某股票的便捷函数

    Args:
        data: 策略数据字典
        stock_code: 股票代码

    Returns:
        bool: 是否持有该股票
    """
    try:
        positions = PositionParser(data)
        return positions.has(stock_code)
    except Exception as e:
        logging.error(f"检查持仓失败: {str(e)}")
        return False
```

### 4. khBuy - 买入信号生成函数
```python
def khBuy(data: Dict, stock_code: str, ratio: float = 1.0,
          volume: Optional[int] = None, reason: str = "") -> Dict:
    """生成买入信号的便捷函数

    Args:
        data: 策略数据字典
        stock_code: 股票代码
        ratio: 买入比例，默认1.0（全仓）
        volume: 指定买入数量，如果提供则忽略ratio
        reason: 买入原因

    Returns:
        Dict: 买入信号字典，失败返回空字典
    """
    try:
        current_price = khPrice(data, stock_code)
        if current_price <= 0:
            logging.warning(f"无法获取股票{stock_code}的价格信息")
            return {}

        if reason == "":
            reason = f"策略买入{stock_code}"

        signals = generate_signal(data, stock_code, current_price, ratio, 'buy', reason)
        return signals[0] if signals else {}
    except Exception as e:
        logging.error(f"生成买入信号失败: {str(e)}")
        return {}
```

### 5. khSell - 卖出信号生成函数
```python
def khSell(data: Dict, stock_code: str, ratio: float = 1.0,
           volume: Optional[int] = None, reason: str = "") -> Dict:
    """生成卖出信号的便捷函数

    Args:
        data: 策略数据字典
        stock_code: 股票代码
        ratio: 卖出比例，默认1.0（全仓）
        volume: 指定卖出数量，如果提供则忽略ratio
        reason: 卖出原因

    Returns:
        Dict: 卖出信号字典，失败返回空字典
    """
    try:
        current_price = khPrice(data, stock_code)
        if current_price <= 0:
            logging.warning(f"无法获取股票{stock_code}的价格信息")
            return {}

        if reason == "":
            reason = f"策略卖出{stock_code}"

        signals = generate_signal(data, stock_code, current_price, ratio, 'sell', reason)
        return signals[0] if signals else {}
    except Exception as e:
        logging.error(f"生成卖出信号失败: {str(e)}")
        return {}
```

## 🎯 完整使用示例

### 基础策略模板
```python
from khQuantImport import *

def init(stock_list, context):
    """策略初始化"""
    logging.info("策略开始初始化")

    # 获取初始化时间
    time_info = TimeInfo(context)
    logging.info(f"初始化时间: {time_info.datetime_str}")

    # 预加载股票池
    stock_pool = khGet(context, 'stocks')
    logging.info(f"股票池: {stock_pool}")

def khHandlebar(context):
    """主策略逻辑"""
    signals = []

    # 获取当前时间
    current_time = khGet(context, 'time_str')
    logging.info(f"策略执行时间: {current_time}")

    # 获取账户信息
    cash = khGet(context, 'cash')
    total_asset = khGet(context, 'total_asset')
    logging.info(f"可用资金: {cash:.2f}, 总资产: {total_asset:.2f}")

    # 遍历股票池
    for stock_code in khGet(context, 'stocks'):
        # 获取当前价格
        current_price = khPrice(context, stock_code)
        if current_price <= 0:
            continue

        logging.debug(f"{stock_code} 当前价格: {current_price}")

        # 检查是否已持仓
        if khHas(context, stock_code):
            # 持仓逻辑 - 可以考虑止盈止损
            logging.debug(f"已持有 {stock_code}")
        else:
            # 无持仓逻辑 - 可以考虑买入条件
            if should_buy_stock(stock_code, current_price):
                # 使用30%资金买入
                buy_signal = khBuy(context, stock_code, 0.3, f"{stock_code} 满足买入条件")
                if buy_signal:
                    signals.append(buy_signal)
                    logging.info(f"生成买入信号: {buy_signal}")

    return signals

def should_buy_stock(stock_code, price):
    """自定义买入条件判断"""
    # 这里可以添加你的买入逻辑
    # 例如：技术指标、基本面条件等
    return True  # 示例：总是买入

def khPreMarket(context):
    """盘前处理"""
    logging.info(f"盘前处理: {khGet(context, 'date_str')}")
    return []

def khPostMarket(context):
    """盘后处理"""
    logging.info(f"盘后处理: {khGet(context, 'date_str')}")

    # 统计当日交易
    total_asset = khGet(context, 'total_asset')
    cash = khGet(context, 'cash')
    market_value = khGet(context, 'market_value')

    logging.info(f"当日结束 - 总资产: {total_asset:.2f}, 现金: {cash:.2f}, 持仓市值: {market_value:.2f}")
    return []
```

## 🔗 与其他模块的集成

### 与 khQTTools 的集成
```python
from khQuantImport import *

def khHandlebar(context):
    # khQuantImport 自动导入了 khQTTools 的所有函数
    # 可以直接使用 khHistory, calculate_max_buy_volume 等

    stock_code = '000001.SZ'

    # 获取历史数据
    hist_data = khHistory([stock_code], ['close'], 30, '1d')

    if stock_code in hist_data:
        close_prices = hist_data[stock_code]['close'].values

        # 计算技术指标
        ma5 = MA(close_prices, 5)
        ma20 = MA(close_prices, 20)

        current_price = khPrice(context, stock_code)

        # 均线策略
        if len(ma5) > 0 and len(ma20) > 0:
            if ma5[-1] > ma20[-1] and not khHas(context, stock_code):
                # 金叉买入，使用30%资金
                max_volume = calculate_max_buy_volume(context, stock_code, current_price, 0.3)
                if max_volume > 0:
                    return [khBuy(context, stock_code, volume=max_volume, reason="金叉买入")]

    return []
```

### 与 MyTT 的集成
```python
from khQuantImport import *

def khHandlebar(context):
    signals = []

    for stock_code in khGet(context, 'stocks'):
        # 获取历史数据
        hist_data = khHistory([stock_code], ['close', 'high', 'low'], 20, '1d')

        if stock_code not in hist_data:
            continue

        df = hist_data[stock_code]
        close_prices = df['close'].values
        high_prices = df['high'].values
        low_prices = df['low'].values

        # 使用 MyTT 计算技术指标
        rsi = RSI(close_prices, 14)
        macd, signal, histogram = MACD(close_prices)
        k, d, j = KDJ(high_prices, low_prices, close_prices)

        current_price = khPrice(context, stock_code)

        # RSI策略
        if len(rsi) >= 2:
            current_rsi = rsi[-1]
            prev_rsi = rsi[-2]

            # RSI超卖买入
            if prev_rsi < 30 <= current_rsi and not khHas(context, stock_code):
                signals.append(khBuy(context, stock_code, 0.5, f"RSI超卖买入: {current_rsi:.2f}"))

            # RSI超买卖出
            elif prev_rsi > 70 >= current_rsi and khHas(context, stock_code):
                signals.append(khSell(context, stock_code, 1.0, f"RSI超买卖出: {current_rsi:.2f}"))

    return signals
```

## 📈 最佳实践建议

### 1. 错误处理
```python
def khHandlebar(context):
    signals = []

    try:
        for stock_code in khGet(context, 'stocks'):
            # 价格检查
            price = khPrice(context, stock_code)
            if price <= 0:
                logging.warning(f"无法获取{stock_code}价格数据")
                continue

            # 信号生成
            signal = generate_signal_logic(stock_code, price, context)
            if signal:
                signals.append(signal)

    except Exception as e:
        logging.error(f"策略执行失败: {str(e)}", exc_info=True)

    return signals
```

### 2. 性能优化
```python
def init(stock_list, context):
    # 在初始化时缓存常用数据
    global g_cache
    g_cache = {}

    for stock_code in stock_list:
        g_cache[stock_code] = {
            'last_update': None,
            'indicators': {}
        }

def khHandlebar(context):
    # 使用缓存减少重复计算
    current_date = khGet(context, 'date_str')

    for stock_code in khGet(context, 'stocks'):
        cache_item = g_cache.get(stock_code)

        if cache_item and cache_item['last_update'] == current_date:
            # 使用缓存的指标
            indicators = cache_item['indicators']
        else:
            # 计算新的指标
            indicators = calculate_indicators(stock_code)
            if stock_code in g_cache:
                g_cache[stock_code]['last_update'] = current_date
                g_cache[stock_code]['indicators'] = indicators
```

### 3. 日志记录
```python
def khHandlebar(context):
    # 合理使用日志级别
    logging.info(f"策略开始执行: {khGet(context, 'datetime_str')}")

    for stock_code in khGet(context, 'stocks'):
        price = khPrice(context, stock_code)

        # 关键信息使用INFO级别
        if should_buy(stock_code, price):
            logging.info(f"{stock_code} 满足买入条件，价格: {price}")

        # 调试信息使用DEBUG级别
        logging.debug(f"{stock_code} 技术指标: RSI={get_rsi(stock_code):.2f}")

    # 错误使用ERROR级别
    try:
        # 策略逻辑
        pass
    except Exception as e:
        logging.error(f"策略执行异常: {str(e)}", exc_info=True)
```

---

*khQuantImport模块通过统一的导入接口和便捷函数，大大简化了量化策略开发的复杂度，让开发者能够专注于策略逻辑本身而不是繁琐的数据处理细节。*