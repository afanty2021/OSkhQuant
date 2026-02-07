# KHQuant 测试计划

## 概述

本文档详细说明了看海量化交易系统(KHQuant)的测试策略，目标达到90%+的代码覆盖率。

## 测试目标

- **代码覆盖率**: 90%+
- **测试框架**: pytest
- **覆盖率工具**: pytest-cov
- **代码质量**: 遵循AAA模式(Arrange-Act-Assert)

## 项目现状

### 已有测试
- `test_khRisk.py` - 风险管理模块测试(已实现)
- `test_khSecurity.py` - 安全验证模块测试(已实现)
- `test_logging_config.py` - 日志配置测试(已实现)

### 待测试的核心模块

#### 1. 策略执行层(高优先级)
- **khFrame.py** (2666行) - 策略执行引擎核心
- **khQTTools.py** (2309行) - 量化工具集和API
- **khTrade.py** (624行) - 交易管理和执行
- **khQuantImport.py** (521行) - 统一导入模块

#### 2. 数据管理层(中优先级)
- **miniQMT_data_parser.py** (1274行) - MiniQMT数据解析
- **khConfig.py** (4364行) - 配置管理

#### 3. 分析工具层(中优先级)
- **MyTT.py** (624行) - 技术指标计算库

#### 4. 工具模块(低优先级)
- **constants.py** - 常量定义

## 模块测试详情

### 1. khQuantImport.py 测试计划

#### 测试范围
- `TimeInfo` 类 - 时间信息解析
- `StockDataParser` 类 - 股票数据解析
- `PositionParser` 类 - 持仓数据解析
- `StockPoolParser` 类 - 股票池解析
- `StrategyContext` 类 - 策略上下文
- 便捷函数: `khGet`, `khPrice`, `khHas`, `parse_context`
- 辅助函数: `_is_valid_value`, `_get_tick_compatible_field`

#### 测试用例

**TimeInfo 类测试**
```python
- test_date_str_property - 测试日期字符串获取
- test_date_num_property - 测试数字日期获取
- test_time_str_property - 测试时间字符串获取
- test_datetime_str_property - 测试完整日期时间获取
- test_datetime_num_property - 测试数字日期时间获取
- test_datetime_obj_property - 测试datetime对象获取
- test_timestamp_property - 测试时间戳获取
- test_empty_data - 测试空数据处理
- test_missing_fields - 测试缺失字段处理
```

**StockDataParser 类测试**
```python
- test_get_price_normal - 测试正常价格获取
- test_get_price_kline_data - 测试K线数据价格获取
- test_get_price_tick_data - 测试Tick数据价格获取
- test_get_close - 测试收盘价获取
- test_get_open - 测试开盘价获取
- test_get_high - 测试最高价获取
- test_get_low - 测试最低价获取
- test_get_volume - 测试成交量获取
- test_pandas_series_handling - 测试pandas Series处理
- test_array_handling - 测试数组类型处理
- test_nan_handling - 测试NaN值处理
- test_missing_stock - 测试缺失股票代码
```

**PositionParser 类测试**
```python
- test_has_position - 测试持仓检查
- test_has_no_position - 测试无持仓情况
- test_get_volume - 测试获取持仓数量
- test_get_cost - 测试获取持仓成本
- test_get_all_positions - 测试获取所有持仓
- test_empty_positions - 测试空持仓字典
```

**StockPoolParser 类测试**
```python
- test_get_all_stocks - 测试获取所有股票
- test_pool_size - 测试股票池大小
- test_contains_stock - 测试股票包含检查
- test_first_stock - 测试获取第一个股票
- test_empty_pool - 测试空股票池
```

**StrategyContext 类测试**
```python
- test_buy_signal - 测试买入信号生成
- test_sell_signal - 测试卖出信号生成
- test_buy_signal_invalid_price - 测试无效价格买入信号
- test_sell_signal_invalid_price - 测试无效价格卖出信号
- test_context_initialization - 测试上下文初始化
```

**便捷函数测试**
```python
- test_khGet_date - 测试获取日期
- test_khGet_time - 测试获取时间
- test_khGet_datetime - 测试获取完整时间
- test_khGet_cash - 测试获取现金
- test_khGet_stocks - 测试获取股票列表
- test_khGet_positions - 测试获取持仓
- test_khPrice_normal - 测试正常价格获取
- test_khPrice_pandas_series - 测试pandas Series价格
- test_khPrice_nan - 测试NaN价格处理
- test_khHas_true - 测试存在持仓
- test_khHas_false - 测试无持仓
- test_parse_context - 测试上下文解析
```

### 2. MyTT.py 测试计划

#### 测试范围
**0级核心工具函数** (45个函数)
- 基础数学函数: `RD`, `RET`, `ABS`, `LN`, `POW`, `SQRT`, `SIN`, `COS`, `TAN`
- 序列操作函数: `MAX`, `MIN`, `IF`, `REF`, `DIFF`, `STD`, `SUM`, `CONST`
- 极值函数: `HHV`, `LLV`, `HHVBARS`, `LLVBARS`
- 移动平均: `MA`, `EMA`, `SMA`, `WMA`, `DMA`
- 统计函数: `AVEDEV`, `SLOPE`, `FORCAST`, `LAST`

**1级应用函数** (12个函数)
- `COUNT`, `EVERY`, `EXIST`, `FILTER`, `BARSLAST`, `BARSLASTCOUNT`
- `BARSSINCEN`, `CROSS`, `LONGCROSS`, `VALUEWHEN`, `BETWEEN`, `TOPRANGE`, `LOWRANGE`

**2级技术指标** (30+个函数)
- 趋势指标: `MACD`, `TRIX`, `DFMA`, `MTM`, `EXPMA`, `DPO`
- 动量指标: `RSI`, `WR`, `BIAS`, `CCI`, `CR`, `ROC`
- 波动指标: `BOLL`, `ATR`, `KTN`
- 量能指标: `VR`, `OBV`, `MFI`, `EMV`, `BRAR`
- 压力支撑: `TAQ`, `XSII`, `ASI`
- 其他指标: `KDJ`, `PSY`, `BBI`, `DMI`, `SAR`, `TDX_SAR`

**扩展函数**
- `DSMA`, `SUMBARSFAST`, `HHV` (动态), `LLV` (动态)

#### 测试用例

**基础数学函数测试**
```python
- test_RD_rounding - 测试四舍五入
- test_RET_last_value - 测试返回序列末尾值
- test_ABS_absolute - 测试绝对值
- test_LN_logarithm - 测试自然对数
- test_POW_power - 测试幂运算
- test_SQRT_square_root - 测试平方根
- test_SIN_cosine_tangent - 测试三角函数
- test_MAX_maximum - 测试序列最大值
- test_MIN_minimum - 测试序列最小值
- test IF_conditional - 测试条件判断
```

**序列操作测试**
```python
- test_REF_shift - 测试序列后移
- test_DIFF_difference - 测试差分
- test_STD_standard_deviation - 测试标准差
- test_SUM_cumulation - 测试累计和
- test_CONST_constant - 测试常量扩展
```

**极值函数测试**
```python
- test_HHV_fixed_period - 测试固定周期最高值
- test_HHV_dynamic_period - 测试动态周期最高值
- test_LLV_fixed_period - 测试固定周期最低值
- test_LLV_dynamic_period - 测试动态周期最低值
- test_HHVBARS - 测试最高值位置
- test_LLVBARS - 测试最低值位置
```

**移动平均测试**
```python
- test_MA_simple_moving_average - 测试简单移动平均
- test_EMA_exponential_moving_average - 测试指数移动平均
- test_SMA_smoothed_moving_average - 测试平滑移动平均
- test_WMA_weighted_moving_average - 测试加权移动平均
- test_DMA_dynamic_moving_average - 测试动态移动平均
- test_DMA_sequence_alpha - 测试序列平滑因子
```

**技术指标测试**
```python
# MACD
- test_MACD_calculation - 测试MACD计算
- test_MACD_default_params - 测试默认参数
- test_MACD_custom_params - 测试自定义参数

# KDJ
- test_KDJ_calculation - 测试KDJ计算
- test_KDJ_range - 测试KDJ值范围

# RSI
- test_RSI_calculation - 测试RSI计算
- test_RSI_range - 测试RSI值范围(0-100)
- test_RSI_period - 测试不同周期

# BOLL
- test_BOLL_calculation - 测试布林带计算
- test_BOLL_bands - 测试上中下轨关系

# 其他指标
- test_BIAS_calculation - 测试乖离率
- test_ATR_calculation - 测试真实波幅
- test_CCI_calculation - 测试顺势指标
- test_WR_calculation - 测试威廉指标
- test_PSY_calculation - 测试心理线
- test_VR_calculation - 测试成交量变异率
- test_CR_calculation - 测试价格动量指标
- test_EMV_calculation - 测试简易波动指标
- test_MFI_calculation - 测试资金流量指标
- test_BRAR_calculation - 测试ARBR情绪指标
- test_OBV_calculation - 测试能量潮
- test_DMI_calculation - 测试趋向指标
- test_SAR_calculation - 测试抛物转向
- test_TDX_SAR_calculation - 测试通达信SAR
- test_DPO_calculation - 测试区间震荡线
- test_MTM_calculation - 测试动量指标
- test_MASS_calculation - 测试梅斯线
- test_ROC_calculation - 测试变动率指标
- test_TRI_calculation - 测试三重指数平滑移动平均
- test_ASI_calculation - 测试振动升降指标
- test_XSII_calculation - 测试薛斯通道II
- test_TAQ_calculation - 测试唐奇安通道
- test_KTN_calculation - 测试肯特纳通道
```

**边界条件测试**
```python
- test_empty_series - 测试空序列
- test_single_value_series - 测试单值序列
- test_nan_handling - 测试NaN处理
- test_inf_handling - 测试无穷大处理
- test_negative_values - 测试负值处理
- test_zero_values - 测试零值处理
```

### 3. khQTTools.py 测试计划

#### 测试范围
- ETF判断: `is_etf`, `determine_pool_type`
- T+0交易: `load_t0_etf_list`, `is_t0_etf`, `check_t0_support`, `get_t0_details`
- 价格处理: `format_price`, `round_price`, `get_price_decimals`
- 时间工具: `is_trade_time`, `is_trade_day`, `get_trade_days_count`
- KhQuTools类 - 核心量化工具集

#### 测试用例

**ETF判断测试**
```python
- test_is_etf_shanghai - 测试上海ETF判断(51/52/53/55/56/58开头)
- test_is_etf_shenzhen - 测试深圳ETF判断(159开头)
- test_is_etf_lof_exclusion - 测试LOF排除(50/16开头)
- test_is_etf_mixed_code - 测试混合代码
- test_determine_pool_type_stock_only - 测试纯股票池
- test_determine_pool_type_etf_only - 测试纯ETF池
- test_determine_pool_type_mixed - 测试混合池
- test_determine_pool_type_empty - 测试空列表
```

**T+0交易测试**
```python
- test_load_t0_etf_list - 测试T0 ETF列表加载
- test_is_t0_etf_true - 测试T0 ETF判断(True)
- test_is_t0_etf_false - 测试非T0 ETF判断(False)
- test_check_t0_support_all_t0 - 测试全T0支持
- test_check_t0_support_no_t0 - 测试无T0支持
- test_check_t0_support_mixed - 测试混合支持
- test_get_t0_details - 测试T0详细信息获取
```

**价格处理测试**
```python
- test_format_price_stock - 测试股票价格格式化(2位小数)
- test_format_price_etf - 测试ETF价格格式化(3位小数)
- test_round_price_up - 测试向上取整
- test_round_price_down - 测试向下取整
- test_get_price_decimals_stock - 测试获取股票价格精度
- test_get_price_decimals_etf - 测试获取ETF价格精度
```

**时间工具测试**
```python
- test_is_trade_time_morning - 测试上午交易时间
- test_is_trade_time_afternoon - 测试下午交易时间
- test_is_trade_time_lunch_break - 测试午休时间
- test_is_trade_time_non_trading - 测试非交易时间
- test_is_trade_day_weekday - 测试工作日判断
- test_is_trade_day_weekend - 测试周末判断
- test_is_trade_day_holiday - 测试节假日判断
- test_get_trade_days_count - 测试交易日计数
```

**KhQuTools类测试**
```python
- test_initialization - 测试初始化
- test_generate_signal_buy - 测试生成买入信号
- test_generate_signal_sell - 测试生成卖出信号
- test_calculate_max_buy_volume - 测试计算最大买入量
- test_khMA_calculation - 测试项目均线计算
```

### 4. khTrade.py 测试计划

#### 测试范围
- `KhTradeManager` 类 - 交易管理器核心
- 交易成本计算: 佣金、印花税、过户费、滑点
- 订单处理: 买入、卖出、持仓管理
- T+0模式支持

#### 测试用例

**初始化测试**
```python
- test_initialization - 测试初始化
- test_set_price_decimals - 测试设置价格精度
- test_set_t0_mode_enabled - 测试启用T+0模式
- test_set_t0_mode_disabled - 测试禁用T+0模式
```

**滑点计算测试**
```python
- test_calculate_slippage_buy_tick_mode - 测试买入滑点(tick模式)
- test_calculate_slippage_sell_tick_mode - 测试卖出滑点(tick模式)
- test_calculate_slippage_buy_ratio_mode - 测试买入滑点(比例模式)
- test_calculate_slippage_sell_ratio_mode - 测试卖出滑点(比例模式)
- test_calculate_slippage_no_slippage - 测试无滑点情况
```

**成本计算测试**
```python
- test_calculate_commission_normal - 测试正常佣金计算
- test_calculate_commission_minimum - 测试最低佣金
- test_calculate_commission_zero_volume - 测试零交易量佣金
- test_calculate_stamp_tax_sell - 测试卖出印花税
- test_calculate_stamp_tax_buy - 测试买入无印花税
- test_calculate_transfer_fee_shanghai - 测试沪市过户费
- test_calculate_transfer_fee_shenzhen - 测试深市无过户费
- test_calculate_flow_fee - 测试流量费
- test_calculate_trade_cost_buy - 测试买入总成本
- test_calculate_trade_cost_sell - 测试卖出总成本
```

**订单处理测试**
```python
- test_process_signals_buy - 测试处理买入信号
- test_process_signals_sell - 测试处理卖出信号
- test_process_signals_empty - 测试空信号列表
- test_insufficient_funds - 测试资金不足
- test_insufficient_position - 测试持仓不足
- test_t0_buy_sell_same_day - 测试T+0同日买卖
- test_t1_buy_next_day_sell - 测试T+1次日卖出
```

### 5. constants.py 测试计划

#### 测试范围
- `TradeCalendar` - 交易日历常量
- `Trading` - 交易常量
- `DataPeriod` - 数据周期常量
- `DividendType` - 复权类型常量
- `OrderDirection` - 交易方向常量
- `LogLevel` - 日志级别常量
- `FilePath` - 文件路径常量
- `FileSize` - 文件大小常量
- `TimeConstant` - 时间常量
- `Status` - 状态常量
- `ErrorCode` - 错误代码常量
- `UI` - 界面常量

#### 测试用例
```python
- test_trade_calendar_constants - 测试交易日历常量值
- test_trading_constants - 测试交易常量值
- test_data_period_mapping - 测试数据周期映射
- test_dividend_type_mapping - 测试复权类型映射
- test_order_direction_mapping - 测试交易方向映射
- test_log_level_mapping - 测试日志级别映射
- test_file_path_constants - 测试文件路径常量
- test_file_size_calculation - 测试文件大小计算
- test_time_format_constants - 测试时间格式常量
- test_status_constants - 测试状态常量
- test_error_code_ranges - 测试错误代码范围
- test_ui_constants - 测试界面常量
- test_trading_hours_tuple - 测试交易时间元组
- test_default_risk_config - 测试默认风险配置
```

### 6. khConfig.py 测试计划

#### 测试范围
- `KhConfig` 类 - 配置管理器
- 配置加载和保存
- 配置验证和默认值
- 多环境配置支持

#### 测试用例
```python
- test_load_config - 测试配置加载
- test_save_config - 测试配置保存
- test_get_value - 测试获取配置值
- test_set_value - 测试设置配置值
- test_default_values - 测试默认值
- test_config_validation - 测试配置验证
- test_missing_config_file - 测试缺失配置文件
- test_invalid_config_format - 测试无效配置格式
- test_merge_config - 测试配置合并
```

### 7. khFrame.py 测试计划

#### 测试范围
- `TriggerBase` - 触发器基类
- `TickTrigger` - Tick触发器
- `KLineTrigger` - K线触发器
- `CustomTimeTrigger` - 自定义时间触发器
- `KhQuantFramework` - 量化框架核心

#### 测试用例
```python
# 触发器测试
- test_tick_trigger_should_trigger - 测试Tick触发器
- test_kline_trigger_1m - 测试1分钟K线触发
- test_kline_trigger_5m - 测试5分钟K线触发
- test_kline_trigger_1d - 测试日K线触发
- test_custom_time_trigger - 测试自定义时间触发

# 框架核心测试
- test_framework_initialization - 测试框架初始化
- test_framework_load_strategy - 测试加载策略
- test_framework_run_strategy - 测试运行策略
- test_framework_stop - 测试停止框架
- test_framework_data_subscription - 测试数据订阅
- test_framework_event_handling - 测试事件处理
```

### 8. miniQMT_data_parser.py 测试计划

#### 测试范围
- Tick数据解析
- K线数据解析
- 数据格式转换
- 数据验证和清洗

#### 测试用例
```python
- test_parse_tick_data - 测试Tick数据解析
- test_parse_kline_data - 测试K线数据解析
- test_parse_invalid_data - 测试无效数据处理
- test_data_format_conversion - 测试数据格式转换
- test_field_mapping - 测试字段映射
- test_missing_fields - 测试缺失字段处理
- test_data_validation - 测试数据验证
```

## 测试执行计划

### 阶段1: 基础测试(第1-2周)
1. 实现 `test_khQuantImport.py` - 核心导入模块
2. 实现 `test_MyTT.py` - 技术指标库
3. 实现 `test_constants.py` - 常量定义

### 阶段2: 核心功能测试(第3-4周)
1. 实现 `test_khQTTools.py` - 量化工具集
2. 实现 `test_khTrade.py` - 交易管理
3. 实现 `test_khConfig.py` - 配置管理

### 阶段3: 集成测试(第5-6周)
1. 实现 `test_khFrame.py` - 策略框架
2. 实现 `test_miniQMT_data_parser.py` - 数据解析
3. 集成测试 - 模块间交互

### 阶段4: 覆盖率优化(第7-8周)
1. 检查覆盖率报告
2. 补充遗漏的测试用例
3. 边界条件和异常测试
4. 性能测试

## 测试命名规范

### 文件命名
- 测试文件: `test_<module_name>.py`
- 例如: `test_khQuantImport.py`, `test_MyTT.py`

### 类命名
- 测试类: `Test<ClassName>`
- 例如: `TestTimeInfo`, `TestStockDataParser`

### 函数命名
- 测试函数: `test_<function_name>_<scenario>`
- 例如: `test_get_price_normal`, `test_get_price_nan`

## 断言和Mock规范

### AAA模式
```python
def test_example():
    # Arrange - 准备测试数据和环境
    test_data = create_test_data()
    mock_obj = Mock()

    # Act - 执行被测试的功能
    result = function_to_test(test_data, mock_obj)

    # Assert - 验证结果
    assert result == expected_value
    mock_obj.method.assert_called_once()
```

### Mock使用
- 使用 `unittest.mock.Mock` 创建模拟对象
- 使用 `unittest.mock.patch` 隔离外部依赖
- 避免使用真实文件系统或网络连接

## 覆盖率目标

| 模块 | 目标覆盖率 | 优先级 |
|------|-----------|--------|
| khQuantImport.py | 95% | 高 |
| MyTT.py | 90% | 高 |
| khQTTools.py | 90% | 高 |
| khTrade.py | 90% | 高 |
| khFrame.py | 85% | 中 |
| khConfig.py | 85% | 中 |
| miniQMT_data_parser.py | 80% | 中 |
| constants.py | 100% | 低 |

## CI/CD集成

### GitHub Actions配置
- 自动运行测试
- 生成覆盖率报告
- 覆盖率低于目标时失败
- 支持多Python版本测试

### 覆盖率报告
- 使用 `pytest-cov` 生成HTML报告
- 报告保存在 `htmlcov/` 目录
- 每次PR自动更新覆盖率

## 测试数据管理

### Fixtures使用
- 在 `conftest.py` 中定义共享fixtures
- 使用参数化测试减少重复代码
- 提供真实的测试数据样本

### 测试数据文件
- 保存在 `tests/fixtures/` 目录
- 包含样本K线数据、Tick数据
- 使用JSON或CSV格式

## 性能测试

### 关键指标
- 单个测试用例执行时间 < 1秒
- 完整测试套件执行时间 < 5分钟
- 内存使用合理(无内存泄漏)

### 性能测试工具
- 使用 `pytest-benchmark` 进行性能测试
- 定期运行性能基准测试

## 文档要求

### 测试文档
- 每个测试模块包含docstring
- 说明测试目的和覆盖范围
- 记录已知限制和问题

### 覆盖率文档
- 定期更新覆盖率报告
- 记录未覆盖代码的原因
- 制定覆盖率提升计划

---

*文档版本: 1.0*
*创建日期: 2026-02-07*
*最后更新: 2026-02-07*
