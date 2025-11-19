# khFrame模块 - 策略执行引擎核心

## 📋 模块概述

**文件**: `khFrame.py` (2666行)
**功能**: 量化策略执行引擎，负责策略生命周期管理、事件驱动、数据处理和交易执行
**核心作用**: 连接策略代码与底层数据/交易接口的桥梁
**依赖**: xtquant, pandas, numpy, threading

## 🏗️ 核心架构

### 主要类结构
```python
class KhQuantFramework:
    """看海量化交易框架核心类"""

    def __init__(self, config):
        self.config = config
        self.data_manager = DataManager()
        self.signal_manager = SignalManager()
        self.risk_manager = RiskManager()
        self.portfolio_manager = PortfolioManager()

    # 核心执行方法
    def initialize_strategy(self)          # 策略初始化
    def run_backtest(self)                 # 执行回测
    def process_bar_data(self)             # 处理K线数据
    def execute_signals(self, signals)     # 执行交易信号
    def update_portfolio_state(self)       # 更新投资组合状态

class BacktestEngine:
    """回测执行引擎"""

    def __init__(self, framework):
        self.framework = framework
        self.progress_callback = None

    def run(self, start_date, end_date):
        """执行回测"""

class EventManager:
    """事件管理器"""

    def __init__(self):
        self.event_handlers = {}

    def register_handler(self, event_type, handler):
        """注册事件处理器"""

    def emit_event(self, event_type, data):
        """发送事件"""
```

## 🔧 核心功能模块

### 1. 策略生命周期管理

#### 策略初始化
```python
class StrategyManager:
    """策略管理器"""

    def __init__(self, strategy_path, config):
        self.strategy_path = strategy_path
        self.config = config
        self.strategy_module = None
        self.strategy_context = {}

    def load_strategy(self):
        """加载策略模块"""
        try:
            spec = importlib.util.spec_from_file_location("strategy", self.strategy_path)
            self.strategy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.strategy_module)

            # 验证必需函数
            self.validate_strategy_interface()

            logging.info(f"策略加载成功: {self.strategy_path}")

        except Exception as e:
            logging.error(f"策略加载失败: {str(e)}")
            raise StrategyLoadError(f"无法加载策略: {str(e)}")

    def validate_strategy_interface(self):
        """验证策略接口"""
        required_functions = ['init', 'khHandlebar']

        for func_name in required_functions:
            if not hasattr(self.strategy_module, func_name):
                raise StrategyValidationError(f"策略缺少必需函数: {func_name}")

        # 检查可选函数
        self.has_pre_market = hasattr(self.strategy_module, 'khPreMarket')
        self.has_post_market = hasattr(self.strategy_module, 'khPostMarket')

    def initialize_strategy(self, stock_list, initial_context):
        """初始化策略"""
        try:
            # 构建初始化上下文
            init_context = self.build_init_context(initial_context)

            # 调用策略初始化函数
            if hasattr(self.strategy_module, 'init'):
                self.strategy_module.init(stock_list, init_context)

            # 保存策略状态
            self.strategy_context = init_context

            logging.info("策略初始化完成")

        except Exception as e:
            logging.error(f"策略初始化失败: {str(e)}")
            raise StrategyInitError(f"策略初始化失败: {str(e)}")

    def build_init_context(self, base_context):
        """构建初始化上下文"""
        context = base_context.copy()

        # 添加框架信息
        context['__framework__'] = {
            'version': self.get_framework_version(),
            'config': self.config,
            'data_manager': self.data_manager
        }

        # 添加时间信息
        context['__current_time__'] = self.get_current_time_info()

        # 添加账户信息
        context['__account__'] = self.get_account_info()

        # 添加持仓信息
        context['__positions__'] = {}

        # 添加股票池信息
        context['__stock_list__'] = self.config.get_stock_list()

        return context
```

#### 策略执行控制
```python
class StrategyExecutor:
    """策略执行器"""

    def __init__(self, strategy_manager, data_manager):
        self.strategy_manager = strategy_manager
        self.data_manager = data_manager
        self.execution_state = 'stopped'
        self.current_datetime = None

    def execute_handlebar(self, current_data):
        """执行策略主逻辑"""
        if self.execution_state != 'running':
            return []

        try:
            # 更新当前时间
            self.current_datetime = current_data['__current_time__']

            # 构建策略上下文
            context = self.build_strategy_context(current_data)

            # 执行策略函数
            signals = self.strategy_manager.strategy_module.khHandlebar(context)

            # 验证信号格式
            validated_signals = self.validate_signals(signals)

            # 记录执行日志
            self.log_execution(context, validated_signals)

            return validated_signals

        except Exception as e:
            logging.error(f"策略执行失败: {str(e)}", exc_info=True)
            return []

    def execute_pre_market(self, current_data):
        """执行盘前处理"""
        if not self.strategy_manager.has_pre_market:
            return []

        try:
            context = self.build_strategy_context(current_data)
            signals = self.strategy_manager.strategy_module.khPreMarket(context)
            return self.validate_signals(signals)

        except Exception as e:
            logging.error(f"盘前处理失败: {str(e)}")
            return []

    def execute_post_market(self, current_data):
        """执行盘后处理"""
        if not self.strategy_manager.has_post_market:
            return []

        try:
            context = self.build_strategy_context(current_data)
            signals = self.strategy_manager.strategy_module.khPostMarket(context)
            return self.validate_signals(signals)

        except Exception as e:
            logging.error(f"盘后处理失败: {str(e)}")
            return []

    def build_strategy_context(self, current_data):
        """构建策略执行上下文"""
        context = current_data.copy()

        # 添加当前行情数据
        stock_list = self.config.get_stock_list()
        for stock_code in stock_list:
            stock_data = self.data_manager.get_current_data(stock_code, self.current_datetime)
            if stock_data is not None:
                context[stock_code] = stock_data

        # 添加账户信息
        context['__account__'] = self.portfolio_manager.get_account_info()

        # 添加持仓信息
        context['__positions__'] = self.portfolio_manager.get_positions()

        # 添加框架信息
        context['__framework__'] = {
            'config': self.config,
            'data_manager': self.data_manager
        }

        return context

    def validate_signals(self, signals):
        """验证交易信号格式"""
        validated_signals = []

        if not isinstance(signals, list):
            logging.warning("策略返回的信号不是列表格式")
            return []

        for signal in signals:
            if self.validate_single_signal(signal):
                validated_signals.append(signal)
            else:
                logging.warning(f"无效的交易信号: {signal}")

        return validated_signals

    def validate_single_signal(self, signal):
        """验证单个交易信号"""
        required_fields = ['code', 'action', 'price', 'volume']

        if not isinstance(signal, dict):
            return False

        # 检查必需字段
        for field in required_fields:
            if field not in signal:
                logging.warning(f"交易信号缺少必需字段: {field}")
                return False

        # 验证字段值
        if not self.validate_signal_values(signal):
            return False

        return True

    def validate_signal_values(self, signal):
        """验证信号值的有效性"""
        try:
            # 验证股票代码格式
            stock_code = signal['code']
            if not re.match(r'^\d{6}\.(SH|SZ)$', stock_code):
                logging.warning(f"无效的股票代码格式: {stock_code}")
                return False

            # 验证交易动作
            action = signal['action']
            if action not in ['buy', 'sell']:
                logging.warning(f"无效的交易动作: {action}")
                return False

            # 验证价格
            price = float(signal['price'])
            if price <= 0:
                logging.warning(f"无效的价格: {price}")
                return False

            # 验证数量（必须是100的整数倍）
            volume = int(signal['volume'])
            if volume <= 0 or volume % 100 != 0:
                logging.warning(f"无效的交易数量: {volume}")
                return False

            return True

        except (ValueError, TypeError) as e:
            logging.warning(f"交易信号值验证失败: {str(e)}")
            return False
```

### 2. 数据管理引擎

#### 数据获取和处理
```python
class DataManager:
    """数据管理器"""

    def __init__(self, config):
        self.config = config
        self.cache = DataCache()
        self.data_sources = self.initialize_data_sources()

    def initialize_data_sources(self):
        """初始化数据源"""
        sources = {}

        # MiniQMT数据源
        if self.config.has_miniqmt():
            sources['miniqmt'] = MiniQMTDataSource(self.config.get_minqmt_config())

        # 本地数据源
        sources['local'] = LocalDataSource(self.config.get_local_data_path())

        return sources

    def get_historical_data(self, stock_codes, fields, bar_count, frequency, end_time=None):
        """获取历史数据"""
        try:
            # 检查缓存
            cache_key = self.generate_cache_key(stock_codes, fields, bar_count, frequency, end_time)
            cached_data = self.cache.get(cache_key)

            if cached_data is not None:
                logging.debug("使用缓存的历史数据")
                return cached_data

            # 从数据源获取数据
            data = {}
            for stock_code in stock_codes:
                stock_data = self.get_single_stock_data(
                    stock_code, fields, bar_count, frequency, end_time
                )
                if stock_data is not None:
                    data[stock_code] = stock_data

            # 缓存数据
            self.cache.set(cache_key, data, ttl=3600)  # 缓存1小时

            return data

        except Exception as e:
            logging.error(f"获取历史数据失败: {str(e)}")
            return {}

    def get_single_stock_data(self, stock_code, fields, bar_count, frequency, end_time=None):
        """获取单只股票数据"""
        data_sources_priority = ['miniqmt', 'local']  # 优先级顺序

        for source_name in data_sources_priority:
            if source_name not in self.data_sources:
                continue

            try:
                source = self.data_sources[source_name]
                data = source.get_data(stock_code, fields, bar_count, frequency, end_time)

                if data is not None and len(data) > 0:
                    logging.debug(f"从{source_name}获取到{stock_code}数据: {len(data)}条")
                    return data

            except Exception as e:
                logging.warning(f"从{source_name}获取{stock_code}数据失败: {str(e)}")
                continue

        logging.warning(f"无法从任何数据源获取{stock_code}的数据")
        return None

    def get_current_data(self, stock_code, datetime):
        """获取当前时刻的数据"""
        for source_name, source in self.data_sources.items():
            try:
                current_data = source.get_current_data(stock_code, datetime)
                if current_data is not None:
                    return current_data
            except Exception as e:
                logging.debug(f"从{source_name}获取{stock_code}当前数据失败: {str(e)}")

        return None
```

#### 数据缓存管理
```python
class DataCache:
    """数据缓存管理器"""

    def __init__(self, max_size=1000, default_ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times = {}

    def get(self, key):
        """获取缓存数据"""
        if key not in self.cache:
            return None

        # 检查是否过期
        cache_item = self.cache[key]
        if self.is_expired(cache_item):
            self.remove(key)
            return None

        # 更新访问时间
        self.access_times[key] = time.time()
        return cache_item['data']

    def set(self, key, data, ttl=None):
        """设置缓存数据"""
        # 如果缓存已满，删除最久未访问的数据
        if len(self.cache) >= self.max_size:
            self.evict_lru()

        cache_item = {
            'data': data,
            'created_time': time.time(),
            'ttl': ttl or self.default_ttl
        }

        self.cache[key] = cache_item
        self.access_times[key] = time.time()

    def is_expired(self, cache_item):
        """检查缓存是否过期"""
        return time.time() - cache_item['created_time'] > cache_item['ttl']

    def evict_lru(self):
        """删除最久未访问的缓存项"""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.remove(lru_key)

    def remove(self, key):
        """删除缓存项"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
```

### 3. 回测执行引擎

#### 回测主循环
```python
class BacktestEngine:
    """回测执行引擎"""

    def __init__(self, framework, config):
        self.framework = framework
        self.config = config
        self.progress_callback = None
        self.log_callback = None

    def run_backtest(self, start_date, end_date):
        """运行回测"""
        try:
            logging.info(f"开始回测: {start_date} 至 {end_date}")

            # 初始化回测环境
            self.initialize_backtest()

            # 获取交易日期列表
            trading_days = self.get_trading_days(start_date, end_date)

            # 执行回测主循环
            results = self.run_backtest_loop(trading_days)

            # 生成回测报告
            report = self.generate_backtest_report(results)

            logging.info("回测执行完成")
            return report

        except Exception as e:
            logging.error(f"回测执行失败: {str(e)}", exc_info=True)
            raise

    def run_backtest_loop(self, trading_days):
        """执行回测主循环"""
        total_days = len(trading_days)
        results = []

        for i, trading_day in enumerate(trading_days):
            try:
                # 更新进度
                progress = (i + 1) / total_days
                self.update_progress(progress, trading_day)

                # 执行盘前处理
                pre_market_signals = self.execute_pre_market(trading_day)

                # 获取当日数据
                daily_data = self.get_daily_data(trading_day)

                # 按时间顺序处理数据
                for timestamp, bar_data in daily_data.items():
                    # 执行策略主逻辑
                    signals = self.execute_handlebar(bar_data)

                    # 执行交易信号
                    self.execute_signals(signals, timestamp)

                # 执行盘后处理
                post_market_signals = self.execute_post_market(trading_day)

                # 记录当日结果
                daily_result = self.record_daily_state(trading_day)
                results.append(daily_result)

            except Exception as e:
                logging.error(f"处理交易日{trading_day}时出错: {str(e)}")
                continue

        return results

    def execute_handlebar(self, bar_data):
        """执行策略主逻辑"""
        try:
            # 根据触发类型决定执行频率
            trigger_type = self.config.get_trigger_type()

            if trigger_type == 'tick':
                return self.execute_on_every_tick(bar_data)
            elif trigger_type == 'bar':
                return self.execute_on_bar_close(bar_data)
            elif trigger_type == 'time':
                return self.execute_on_custom_time(bar_data)
            else:
                logging.warning(f"未知的触发类型: {trigger_type}")
                return []

        except Exception as e:
            logging.error(f"执行策略主逻辑失败: {str(e)}")
            return []

    def execute_signals(self, signals, timestamp):
        """执行交易信号"""
        for signal in signals:
            try:
                # 风险检查
                if not self.risk_manager.validate_signal(signal):
                    logging.warning(f"信号未通过风险检查: {signal}")
                    continue

                # 执行交易
                trade_result = self.portfolio_manager.execute_signal(signal, timestamp)

                # 记录交易
                self.record_trade(signal, trade_result, timestamp)

                logging.info(f"执行交易: {signal}")

            except Exception as e:
                logging.error(f"执行交易信号失败: {signal}, 错误: {str(e)}")

    def record_trade(self, signal, trade_result, timestamp):
        """记录交易信息"""
        trade_record = {
            'timestamp': timestamp,
            'signal': signal,
            'result': trade_result,
            'commission': trade_result.get('commission', 0),
            'slippage': trade_result.get('slippage', 0),
            'status': trade_result.get('status', 'failed')
        }

        # 添加到交易记录
        self.framework.add_trade_record(trade_record)
```

#### 成本计算和滑点模拟
```python
class CostCalculator:
    """交易成本计算器"""

    def __init__(self, config):
        self.config = config
        self.min_commission = config.get('min_commission', 5.0)
        self.commission_rate = config.get('commission_rate', 0.0003)
        self.stamp_tax_rate = config.get('stamp_tax_rate', 0.0005)
        self.flow_fee = config.get('flow_fee', 0.0)

    def calculate_commission(self, amount):
        """计算佣金"""
        commission = amount * self.commission_rate
        return max(commission, self.min_commission)

    def calculate_stamp_tax(self, amount, is_sell):
        """计算印花税（仅卖出收取）"""
        if is_sell:
            return amount * self.stamp_tax_rate
        return 0.0

    def calculate_total_cost(self, price, volume, is_sell=False):
        """计算总交易成本"""
        amount = price * volume

        commission = self.calculate_commission(amount)
        stamp_tax = self.calculate_stamp_tax(amount, is_sell)
        total_cost = commission + stamp_tax + self.flow_fee

        return {
            'commission': commission,
            'stamp_tax': stamp_tax,
            'flow_fee': self.flow_fee,
            'total_cost': total_cost,
            'cost_rate': total_cost / amount if amount > 0 else 0
        }

class SlippageSimulator:
    """滑点模拟器"""

    def __init__(self, config):
        self.config = config
        self.slippage_type = config.get('slippage_type', 'ratio')
        self.slippage_value = config.get('slippage_value', 0.001)

    def apply_slippage(self, price, volume, action):
        """应用滑点"""
        if self.slippage_type == 'ratio':
            return self.apply_ratio_slippage(price, action)
        elif self.slippage_type == 'tick':
            return self.apply_tick_slippage(price, action)
        else:
            return price

    def apply_ratio_slippage(self, price, action):
        """按比例应用滑点"""
        slippage_amount = price * self.slippage_value / 2  # 双边滑点

        if action == 'buy':
            # 买入时价格上浮
            adjusted_price = price * (1 + self.slippage_value / 2)
        else:
            # 卖出时价格下浮
            adjusted_price = price * (1 - self.slippage_value / 2)

        # 价格取整到分
        return round(adjusted_price, 2)

    def apply_tick_slippage(self, price, action):
        """按最小变动价位应用滑点"""
        min_tick = 0.01  # A股最小变动价位
        tick_count = int(self.slippage_value)

        if action == 'buy':
            return price + tick_count * min_tick
        else:
            return price - tick_count * min_tick
```

### 4. 投资组合管理

#### 账户和持仓管理
```python
class PortfolioManager:
    """投资组合管理器"""

    def __init__(self, initial_capital, cost_calculator, slippage_simulator):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.cost_calculator = cost_calculator
        self.slippage_simulator = slippage_simulator

        self.positions = {}  # 持仓信息
        self.cash = initial_capital  # 可用现金
        self.frozen_cash = 0  # 冻结资金
        self.trade_records = []  # 交易记录

    def execute_signal(self, signal, timestamp):
        """执行交易信号"""
        try:
            if signal['action'] == 'buy':
                return self.execute_buy(signal, timestamp)
            elif signal['action'] == 'sell':
                return self.execute_sell(signal, timestamp)
            else:
                raise ValueError(f"未知的交易动作: {signal['action']}")

        except Exception as e:
            logging.error(f"执行交易信号失败: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

    def execute_buy(self, signal, timestamp):
        """执行买入交易"""
        stock_code = signal['code']
        order_price = signal['price']
        order_volume = signal['volume']

        # 应用滑点
        execution_price = self.slippage_simulator.apply_slippage(order_price, order_volume, 'buy')

        # 计算交易金额和成本
        trade_amount = execution_price * order_volume
        cost_info = self.cost_calculator.calculate_total_cost(execution_price, order_volume)
        total_cost = trade_amount + cost_info['total_cost']

        # 检查可用资金
        if self.cash < total_cost:
            return {
                'status': 'failed',
                'error': f'可用资金不足: 需要{total_cost:.2f}, 可用{self.cash:.2f}'
            }

        # 冻结资金
        self.frozen_cash += total_cost
        self.cash -= total_cost

        # 更新持仓
        if stock_code in self.positions:
            position = self.positions[stock_code]
            # 计算新的平均成本
            total_volume = position['volume'] + order_volume
            total_cost_basis = position['avg_price'] * position['volume'] + trade_amount
            new_avg_price = total_cost_basis / total_volume

            position['volume'] = total_volume
            position['avg_price'] = new_avg_price
        else:
            self.positions[stock_code] = {
                'volume': order_volume,
                'avg_price': execution_price,
                'first_buy_time': timestamp
            }

        # 解冻资金
        self.frozen_cash -= total_cost

        # 记录交易
        trade_record = {
            'timestamp': timestamp,
            'stock_code': stock_code,
            'action': 'buy',
            'price': execution_price,
            'volume': order_volume,
            'amount': trade_amount,
            'cost': cost_info,
            'status': 'executed'
        }

        self.trade_records.append(trade_record)

        return {
            'status': 'executed',
            'execution_price': execution_price,
            'cost': cost_info,
            'trade_id': len(self.trade_records)
        }

    def execute_sell(self, signal, timestamp):
        """执行卖出交易"""
        stock_code = signal['code']
        order_price = signal['price']
        order_volume = signal['volume']

        # 检查持仓
        if stock_code not in self.positions:
            return {'status': 'failed', 'error': '无持仓可卖'}

        position = self.positions[stock_code]
        if position['volume'] < order_volume:
            return {
                'status': 'failed',
                'error': f'持仓不足: 持有{position["volume"]}, 要卖{order_volume}'
            }

        # 应用滑点
        execution_price = self.slippage_simulator.apply_slippage(order_price, order_volume, 'sell')

        # 计算交易金额和成本
        trade_amount = execution_price * order_volume
        cost_info = self.cost_calculator.calculate_total_cost(execution_price, order_volume, is_sell=True)
        net_amount = trade_amount - cost_info['total_cost']

        # 更新持仓
        remaining_volume = position['volume'] - order_volume
        if remaining_volume == 0:
            del self.positions[stock_code]
        else:
            position['volume'] = remaining_volume

        # 增加可用现金
        self.cash += net_amount

        # 记录交易
        trade_record = {
            'timestamp': timestamp,
            'stock_code': stock_code,
            'action': 'sell',
            'price': execution_price,
            'volume': order_volume,
            'amount': trade_amount,
            'cost': cost_info,
            'realized_pnl': self.calculate_realized_pnl(trade_record),
            'status': 'executed'
        }

        self.trade_records.append(trade_record)

        return {
            'status': 'executed',
            'execution_price': execution_price,
            'cost': cost_info,
            'net_amount': net_amount,
            'trade_id': len(self.trade_records)
        }

    def get_account_info(self):
        """获取账户信息"""
        market_value = self.calculate_market_value()
        total_asset = self.cash + market_value

        return {
            'cash': self.cash,
            'frozen_cash': self.frozen_cash,
            'market_value': market_value,
            'total_asset': total_asset,
            'position_count': len(self.positions)
        }

    def get_positions(self):
        """获取持仓信息"""
        positions = {}
        current_prices = self.get_current_prices()

        for stock_code, position in self.positions.items():
            current_price = current_prices.get(stock_code, position['avg_price'])
            market_value = current_price * position['volume']
            cost_basis = position['avg_price'] * position['volume']
            unrealized_pnl = market_value - cost_basis
            unrealized_pnl_ratio = unrealized_pnl / cost_basis if cost_basis > 0 else 0

            positions[stock_code] = {
                'volume': position['volume'],
                'avg_price': position['avg_price'],
                'current_price': current_price,
                'market_value': market_value,
                'cost_basis': cost_basis,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_ratio': unrealized_pnl_ratio
            }

        return positions
```

## 🔄 事件驱动架构

### 事件管理器
```python
class EventManager:
    """事件管理器"""

    def __init__(self):
        self.handlers = {}
        self.event_queue = []
        self.is_processing = False

    def register_handler(self, event_type, handler):
        """注册事件处理器"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def unregister_handler(self, event_type, handler):
        """注销事件处理器"""
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)

    def emit_event(self, event_type, data):
        """发送事件"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }

        self.event_queue.append(event)
        self.process_events()

    def process_events(self):
        """处理事件队列"""
        if self.is_processing:
            return

        self.is_processing = True

        try:
            while self.event_queue:
                event = self.event_queue.pop(0)
                self.process_single_event(event)
        finally:
            self.is_processing = False

    def process_single_event(self, event):
        """处理单个事件"""
        event_type = event['type']
        data = event['data']

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logging.error(f"事件处理器执行失败: {str(e)}")
```

## 📊 性能监控和优化

### 性能统计
```python
class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation):
        """开始计时"""
        self.start_times[operation] = time.time()

    def end_timer(self, operation):
        """结束计时并记录"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.record_metric(operation, duration)
            del self.start_times[operation]

    def record_metric(self, metric_name, value):
        """记录性能指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)

    def get_performance_report(self):
        """获取性能报告"""
        report = {}
        for metric_name, values in self.metrics.items():
            report[metric_name] = {
                'count': len(values),
                'total': sum(values),
                'average': sum(values) / len(values),
                'min': min(values),
                'max': max(values)
            }
        return report
```

---

*khFrame模块是整个量化交易系统的核心引擎，负责策略的加载、执行、数据管理和投资组合管理，为上层GUI和底层数据接口提供了统一的抽象层。*