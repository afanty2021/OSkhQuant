# 策略开发模块 - 索引文档

## 📋 策略模块概述

本目录包含看海量化交易系统的策略示例和策略开发相关文档。策略文件基于统一的框架API开发，支持回测和模拟交易。

## 🎯 策略文件列表

### 1. RSI策略 (`RSI策略.py`)
**功能**: 基于RSI指标的超买超卖策略
- **指标**: RSI(14)
- **买入条件**: RSI从下向上突破30
- **卖出条件**: RSI从上向下跌破70
- **仓位管理**: 买入时使用50%资金，卖出时全部清仓
- **适用周期**: 日线数据

```python
# 核心逻辑示例
if (rp < 30 <= rn) and not khHas(data, sc):  # RSI上穿30且无持仓
    signals.extend(generate_signal(data, sc, p, 0.5, "buy", f"{sc[:6]} RSI 上穿30"))
elif (rp > 70 >= rn) and khHas(data, sc):  # RSI下穿70且有持仓
    signals.extend(generate_signal(data, sc, p, 1.0, "sell", f"{sc[:6]} RSI 下穿70"))
```

### 2. 双均线策略 - 使用MA函数 (`双均线多股票_使用MA函数.py`)
**功能**: 基于移动平均线的趋势跟踪策略
- **指标**: MA(5) 和 MA(20)
- **买入条件**: 短期均线上穿长期均线（金叉）
- **卖出条件**: 短期均线下穿长期均线（死叉）
- **适用范围**: 多股票组合
- **技术实现**: 使用MyTT库的MA函数

### 3. 双均线策略 - 使用khMA函数 (`双均线多股票_使用khMA函数.py`)
**功能**: 基于项目内自定义khMA函数的双均线策略
- **指标**: khMA计算的移动平均线
- **特点**: 使用项目内部的优化均线计算函数
- **优势**: 与框架深度集成，性能更优

### 4. 双均线精简策略 (`双均线精简_使用khMA函数.py`)
**功能**: 精简版的双均线策略实现
- **特点**: 代码简洁，适合学习和二次开发
- **核心逻辑**: 专注于均线交叉信号
- **优化**: 减少冗余计算，提高执行效率

## 🔧 策略开发框架

### 标准策略结构
```python
from khQuantImport import *  # 统一导入所有必需模块

def init(stock_list, context):
    """策略初始化函数

    Args:
        stock_list: 股票池列表
        context: 初始化上下文信息
    """
    # 全局变量设置
    # 预计算指标
    # 数据预加载
    pass

def khHandlebar(context: Dict) -> List[Dict]:
    """主策略逻辑函数

    Args:
        context: 包含当前行情、持仓、账户等信息的上下文字典

    Returns:
        List[Dict]: 交易信号列表
    """
    signals = []

    # 1. 获取当前时间和数据
    current_time = khGet(context, 'datetime_str')

    # 2. 遍历股票池
    for stock_code in khGet(context, 'stocks'):
        # 3. 获取历史数据计算指标
        hist_data = khHistory([stock_code], ['close'], 30, '1d')

        # 4. 技术指标计算
        # ma5 = MA(hist_data[stock_code]['close'].values, 5)
        # ma20 = MA(hist_data[stock_code]['close'].values, 20)

        # 5. 信号判断
        # if ma5[-1] > ma20[-1] and ma5[-2] <= ma20[-2]:  # 金叉
        #     signals.append(khBuy(context, stock_code, ratio=0.3, reason='金叉买入'))

        # 6. 风险控制
        # elif ma5[-1] < ma20[-1] and ma5[-2] >= ma20[-2]:  # 死叉
        #     signals.append(khSell(context, stock_code, ratio=1.0, reason='死叉卖出'))

    return signals

def khPreMarket(context: Dict) -> List[Dict]:
    """盘前处理函数（可选）"""
    # 每日9:25执行
    # 更新股票池
    # 计算当日指标
    # 预埋单设置
    return []

def khPostMarket(context: Dict) -> List[Dict]:
    """盘后处理函数（可选）"""
    # 每日15:05执行
    # 当日交易统计
    # 持仓复盘
    # 数据保存
    return []
```

### 核心API函数详解

#### 1. 数据获取函数
```python
# 时间相关
current_date = khGet(context, 'date_str')        # "2024-01-15"
current_time = khGet(context, 'time_str')        # "09:30:00"
datetime_str = khGet(context, 'datetime_str')    # "2024-01-15 09:30:00"

# 价格数据
current_price = khPrice(context, '000001.SZ')    # 当前收盘价
open_price = khPrice(context, '000001.SZ', 'open')  # 开盘价
high_price = khPrice(context, '000001.SZ', 'high')  # 最高价
low_price = khPrice(context, '000001.SZ', 'low')    # 最低价
volume = khPrice(context, '000001.SZ', 'volume')    # 成交量

# 账户信息
available_cash = khGet(context, 'cash')           # 可用资金
total_asset = khGet(context, 'total_asset')      # 总资产
market_value = khGet(context, 'market_value')    # 持仓市值

# 股票池和持仓
stock_list = khGet(context, 'stocks')            # 股票池列表
has_position = khHas(context, '000001.SZ')       # 是否持有该股票
```

#### 2. 历史数据获取
```python
# 获取单个股票历史数据
hist_data = khHistory(
    symbol_list=['000001.SZ'],
    fields=['time', 'open', 'high', 'low', 'close', 'volume'],
    bar_count=30,
    fre_step='1d'
)

# 获取多只股票数据
multi_hist = khHistory(
    symbol_list=['000001.SZ', '600036.SH'],
    fields=['close'],
    bar_count=60,
    fre_step='1d'
)

# 数据结构
for stock_code, df in hist_data.items():
    if df is not None:
        close_prices = df['close'].values  # 收盘价数组
        dates = df['time'].values          # 时间数组
```

#### 3. 信号生成函数
```python
# 买入信号
buy_signal = khBuy(
    data=context,
    stock_code='000001.SZ',
    ratio=0.3,                           # 使用30%资金
    reason='RSI超卖买入'
)

# 卖出信号
sell_signal = khSell(
    data=context,
    stock_code='000001.SZ',
    ratio=1.0,                           # 全部卖出
    reason='止盈卖出'
)

# 自定义信号
custom_signal = {
    'code': '000001.SZ',
    'action': 'buy',
    'price': 10.50,
    'volume': 1000,
    'reason': '自定义买入信号'
}
```

#### 4. 技术指标计算
```python
from MyTT import MA, EMA, RSI, MACD, KDJ, BOLL

# 移动平均线
ma5 = MA(close_prices, 5)
ma20 = MA(close_prices, 20)

# 指数移动平均线
ema12 = EMA(close_prices, 12)
ema26 = EMA(close_prices, 26)

# RSI指标
rsi = RSI(close_prices, 14)

# MACD指标
macd_line, signal_line, histogram = MACD(close_prices)

# KDJ指标
k, d, j = KDJ(high_prices, low_prices, close_prices)

# 布林带
upper, middle, lower = BOLL(close_prices, 20)
```

### 高级策略开发技巧

#### 1. 多时间框架分析
```python
def khHandlebar(context):
    signals = []

    # 获取不同周期的数据
    daily_data = khHistory(['000001.SZ'], ['close'], 30, '1d')
    weekly_data = khHistory(['000001.SZ'], ['close'], 12, '1w')

    # 日线趋势判断
    daily_ma20 = MA(daily_data['000001.SZ']['close'].values, 20)

    # 周线趋势确认
    weekly_ma5 = MA(weekly_data['000001.SZ']['close'].values, 5)

    # 多周期信号确认
    current_price = khPrice(context, '000001.SZ')
    if current_price > daily_ma20[-1] and current_price > weekly_ma5[-1]:
        signals.append(khBuy(context, '000001.SZ', ratio=0.5, reason='多周期共振买入'))

    return signals
```

#### 2. 风险管理集成
```python
def init(stock_list, context):
    # 设置全局风控参数
    global g_max_position, g_stop_loss, g_take_profit
    g_max_position = 0.8      # 最大总仓位
    g_stop_loss = 0.05        # 止损比例
    g_take_profit = 0.15      # 止盈比例

def khHandlebar(context):
    signals = []

    # 检查总仓位
    total_market_value = khGet(context, 'market_value')
    total_asset = khGet(context, 'total_asset')
    current_position_ratio = total_market_value / total_asset

    if current_position_ratio >= g_max_position:
        return signals  # 仓位已满，不开新仓

    for stock_code in khGet(context, 'stocks'):
        if khHas(context, stock_code):
            # 止盈止损检查
            position_info = context['__positions__'].get(stock_code, {})
            profit_ratio = position_info.get('profit_ratio', 0)

            if profit_ratio <= -g_stop_loss:
                signals.append(khSell(context, stock_code, ratio=1.0, reason='止损'))
            elif profit_ratio >= g_take_profit:
                signals.append(khSell(context, stock_code, ratio=1.0, reason='止盈'))

    return signals
```

#### 3. 动态仓位管理
```python
def calculate_position_size(context, stock_code, confidence_score=0.5):
    """基于信心度和波动率计算仓位大小"""
    # 获取历史波动率
    hist_data = khHistory([stock_code], ['close'], 20, '1d')
    returns = hist_data[stock_code]['close'].pct_change().dropna()
    volatility = returns.std() * (252 ** 0.5)  # 年化波动率

    # 基础仓位
    base_position = 0.2

    # 根据波动率调整仓位
    volatility_adjustment = max(0.5, min(1.5, 0.3 / volatility))

    # 根据信心度调整
    confidence_adjustment = confidence_score

    # 最终仓位比例
    final_position = base_position * volatility_adjustment * confidence_adjustment

    return min(final_position, 0.3)  # 单只股票最大30%
```

## 📊 策略性能优化建议

### 1. 数据获取优化
- 合理设置历史数据获取范围，避免过度请求
- 使用全局变量缓存计算结果
- 在`init`函数中预加载常用数据

### 2. 指标计算优化
- 使用numpy向量化计算替代循环
- 避免重复计算相同指标
- 合理设置指标参数，平衡性能和效果

### 3. 内存管理
- 及时释放不再使用的大数据对象
- 使用生成器处理大数据集
- 监控内存使用情况

### 4. 信号生成优化
- 合并多个小单为大单，减少交易次数
- 设置信号过滤条件，避免频繁交易
- 使用价格区间委托，提高成交概率

## 🔍 策略调试和测试

### 1. 日志使用
```python
import logging

def khHandlebar(context):
    logging.info(f"策略开始执行，当前时间: {khGet(context, 'datetime_str')}")

    for stock_code in khGet(context, 'stocks'):
        current_price = khPrice(context, stock_code)
        logging.debug(f"{stock_code} 当前价格: {current_price}")

        # 策略逻辑...

        if should_buy:
            logging.info(f"生成买入信号: {stock_code}")

    return signals
```

### 2. 回测验证
- 使用不同时间区间进行回测
- 测试不同市场环境下的表现
- 关注最大回撤和夏普比率

### 3. 参数优化
- 使用网格搜索优化参数
- 进行样本外测试验证
- 避免过度拟合历史数据

---

*策略开发是一个持续迭代的过程，建议从简单的策略开始，逐步增加复杂度和功能。*