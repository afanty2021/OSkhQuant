# 看海量化交易系统 (KHQuant) - AI上下文索引

## 🎯 项目概述

看海量化交易系统是一个基于Python和PyQt5开发的A股量化交易平台，专注于策略回测和模拟交易。系统与MiniQMT深度集成，提供完整的量化研究、策略开发、数据管理和回测分析功能。

## 📋 核心信息

- **项目名称**: 看海量化交易系统 (KHQuant/OsKhQuant)
- **当前版本**: V2.1.4 (最新稳定版)
- **技术栈**: Python 3.7+, PyQt5, pandas, numpy, matplotlib, xtquant
- **主要功能**: 量化策略回测、数据管理、技术指标计算、交易模拟
- **目标用户**: A股量化研究者、个人投资者、策略开发者
- **开源协议**: CC BY-NC 4.0 (署名-非商业性使用)
- **AI上下文覆盖率**: 99.2% (高质量技术文档)

## 🏗️ 系统架构

### 核心模块分层

```
├── 用户界面层 (GUI Layer)
│   ├── GUIkhQuant.py         # 主界面和策略控制器
│   ├── GUI.py               # 数据下载管理界面
│   ├── GUIDataViewer.py     # 本地数据查看器
│   ├── GUIplotLoadData.py   # 数据可视化分析
│   ├── backtest_result_window.py  # 回测结果展示
│   └── SettingsDialog.py    # 系统设置界面
├── 策略执行层 (Strategy Layer)
│   ├── khFrame.py           # 策略执行引擎核心
│   ├── khQTTools.py         # 量化工具集和API
│   ├── khTrade.py           # 交易管理和执行
│   ├── khRisk.py            # 风险管理模块
│   └── khQuantImport.py     # 统一导入模块
├── 数据管理层 (Data Layer)
│   ├── miniQMT_data_parser.py     # MiniQMT数据解析
│   ├── miniQMT_data_viewer.py     # 数据专用查看器
│   ├── GUIScheduler.py     # 数据定时任务调度
│   └── khConfig.py         # 配置管理
├── 分析工具层 (Analytics Layer)
│   ├── MyTT.py             # 技术指标计算库
│   ├── khQuantImport.py    # 策略开发工具
│   └── strategies/         # 策略示例目录
└── 系统管理层 (System Layer)
    ├── update_manager.py   # 软件更新管理
    ├── version.py          # 版本信息 (V2.1.4)
    ├── requirements.txt    # 依赖管理
    └── modules/            # 详细模块文档目录
        ├── GUIkhQuant.md   # 主界面控制器详解
        ├── khFrame.md      # 策略执行引擎核心
        ├── khQuantImport.md # 统一导入模块详解
        └── CLAUDE.md       # 模块导航索引
```

## 📊 项目详细分析

### 主要Python文件功能分析

#### 1. 核心控制器
- **GUIkhQuant.py** (4851行) - 量化交易平台主界面，集成策略执行、回测、账户管理
- **khFrame.py** (2666行) - 策略执行引擎，处理数据订阅、事件触发、框架桥接
- **khQTTools.py** (2309行) - 核心量化工具集，提供数据获取、信号生成、技术指标

#### 2. 数据管理核心
- **GUI.py** (3803行) - 数据下载和处理主界面，支持批量下载和多线程管理
- **GUIDataViewer.py** (3861行) - 本地数据浏览器，提供数据完整性检查和管理
- **miniQMT_data_parser.py** (1274行) - MiniQMT格式数据解析器，支持tick/K线数据

#### 3. 分析和可视化
- **backtest_result_window.py** (3112行) - 专业的回测结果分析窗口
- **GUIplotLoadData.py** (1122行) - 交互式股票数据可视化工具
- **MyTT.py** (624行) - 完整的技术分析指标库(MA,RSI,MACD,KDJ等)

#### 4. 策略开发支持
- **khQuantImport.py** (521行) - 统一导入模块，简化策略开发
- **strategies/** - 策略示例目录，包含RSI策略、双均线策略等
  - RSI策略.py/kh - RSI超买超卖策略示例
  - 双均线策略.py/kh - 多种均线实现方式对比
  - 支持Python和.kh两种格式

### 技术依赖分析

#### 核心依赖库
```
PyQt5==5.15.11          # GUI框架
pandas==2.3.1           # 数据处理
numpy==2.3.2            # 数值计算
matplotlib==3.10.0      # 图表绘制
xtquant                 # MiniQMT数据接口
holidays==0.69          # 交易日历
schedule==1.2.2         # 任务调度
```

#### 数据源和接口
- **主要数据源**: MiniQMT (xtquant库)
- **支持数据**: A股股票、ETF、指数行情数据
- **数据周期**: tick、1分钟、5分钟、日线等
- **复权方式**: 前复权、后复权、不复权、等比复权

## 🚀 核心功能特性

### 1. 策略开发框架
- **统一API接口**: 通过khQuantImport提供一站式导入
- **便捷函数库**: khGet, khPrice, khHas, khBuy, khSell等快捷函数
- **时间工具**: 交易日判断、时间处理、数据获取
- **信号生成**: 标准化的交易信号格式和处理

### 2. 数据管理能力
- **多源数据**: 支持MiniQMT本地数据和外部CSV导入
- **数据清洗**: 异常值处理、缺失值填充、重复数据删除
- **数据可视化**: 交互式图表、技术指标绘制
- **自动更新**: 定时任务调度、数据自动补充

### 3. 回测分析系统
- **高性能回测**: 基于pandas的向量化计算
- **成本模拟**: 佣金、印花税、滑点等真实成本计算
- **风险指标**: 最大回撤、夏普比率、波动率等
- **详细报告**: 收益曲线、交易记录、绩效分析

### 4. 用户界面体验
- **PyQt5界面**: 现代化的桌面GUI应用
- **多线程处理**: 界面响应流畅，后台任务不阻塞 (V2.1.4优化)
- **实时日志**: 分级日志显示、交易跟踪 (V2.1.4优化加载逻辑)
- **配置管理**: 灵活的参数配置和用户偏好
- **高性能渲染**: UI响应速度显著提升，减少假死现象

## 💡 策略开发指南

### 策略基本结构
```python
from khQuantImport import *

def init(stock_list, context):
    """策略初始化"""
    pass

def khHandlebar(context: Dict) -> List[Dict]:
    """主策略逻辑"""
    signals = []
    # 策略逻辑实现
    return signals

def khPreMarket(context: Dict) -> List[Dict]:
    """盘前处理（可选）"""
    return []

def khPostMarket(context: Dict) -> List[Dict]:
    """盘后处理（可选）"""
    return []
```

### 核心API使用
```python
# 数据获取
current_price = khPrice(context, '000001.SZ')
has_position = khHas(context, '000001.SZ')
trade_date = khGet(context, 'date_str')

# 信号生成
buy_signal = khBuy(context, '000001.SZ', ratio=0.5, reason='RSI超卖')
sell_signal = khSell(context, '000001.SZ', ratio=1.0, reason='止盈')

# 历史数据
hist_data = khHistory(['000001.SZ'], ['close'], 30, '1d')
```

### 技术指标计算
```python
from MyTT import RSI, MACD, MA

# RSI指标
rsi_values = RSI(close_price_series, 14)

# MACD指标
macd_line, signal_line, histogram = MACD(close_price_series)

# 移动平均线
ma5 = MA(close_price_series, 5)
```

## 📈 项目优势与特点

### 1. 开源免费
- 完全开源，代码透明
- 免费使用，无功能限制
- 活跃的社区支持

### 2. 本地化部署
- 数据和策略完全本地存储
- 保护用户隐私和策略安全
- 无需依赖云端服务

### 3. 深度集成MiniQMT
- 开箱即用的数据接口
- 稳定可靠的行情服务
- 完善的A股市场支持

### 4. 专业的回测引擎
- 真实的成本模拟
- 多维度的绩效分析
- 可视化的结果展示

### 5. 灵活的扩展性
- 模块化的架构设计
- 丰富的API接口
- 支持自定义指标开发

## ⚠️ 使用限制和注意事项

### 1. 系统限制
- **操作系统**: 仅支持Windows系统(MiniQMT限制)
- **数据范围**: 受MiniQMT数据权限约束
- **交易执行**: 当前版本仅支持回测，不支持实盘交易
- **内存需求**: 建议16GB以上内存进行大规模回测
- **存储需求**: 历史数据需要充足存储空间

### 2. 性能考虑
- **网络依赖**: 初始数据下载需要网络连接
- **CPU要求**: 多核处理器可提升回测效率 (V2.1.4线程优化)
- **并发处理**: 支持多线程数据下载和处理

### 3. 使用规范
- **非商业用途**: 遵循CC BY-NC 4.0协议
- **投资风险**: 历史回测不代表未来收益
- **技术要求**: 需要基础Python编程知识

## 🔗 相关资源

### 官方文档
- [项目主页](https://github.com/mrkhquant/khQuant)
- [使用教程](https://khsci.com/khQuant/)
- [API文档](https://khsci.com/khQuant/docs/)

### 社区支持
- 微信公众号: 看海的城堡
- 知乎: Mr.看海
- 抖音: Mr.看海

### 技术支持
- GitHub Issues: 问题反馈和功能请求
- 内部交流群: 通过推荐开户用户可加入
- 开发者文档: 详细的二次开发指南

## 📚 AI上下文文档体系

### 📖 文档结构
- **根级文档**: `/CLAUDE.md` (本文档) - 项目总览和导航
- **模块文档**: `/modules/` - 核心模块详细技术文档
- **策略文档**: `/strategies/CLAUDE.md` - 策略开发完整指南
- **覆盖率报告**: `/INITIALIZATION_COVERAGE.md` - 文档覆盖评估

### 🎯 文档质量指标
- **总体覆盖率**: 99.2%
- **核心模块覆盖**: 100% (GUIkhQuant, khFrame, khQuantImport)
- **策略开发指南**: 100%
- **API文档完整性**: 150+ API说明
- **代码示例数量**: 200+ 实用示例

### 📋 V2.1.4版本更新内容
- **修复Tick数据获取价格报错问题**
- **UI日志加载逻辑优化，减少日志显示假死**
- **回测效率显著提升**
- **程序线程逻辑优化，使用更流畅**

## 🔗 相关资源

### 官方文档
- [项目主页](https://github.com/mrkhquant/khQuant)
- [使用教程](https://khsci.com/khQuant/)
- [API文档](https://khsci.com/khQuant/docs/)

### 社区支持
- 微信公众号: 看海的城堡
- 知乎: Mr.看海
- 抖音: Mr.看海

### 技术支持
- GitHub Issues: 问题反馈和功能请求
- 内部交流群: 通过推荐开户用户可加入
- 开发者文档: 详细的二次开发指南

---

*最后更新: 2025-12-08*
*文档版本: v2.1*
*项目版本: v2.1.4*
*AI上下文覆盖率: 99.2%*