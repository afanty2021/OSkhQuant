# 看海量化交易系统 (OsKhQuant) 代码优化方案

**文档版本**: v1.1
**生成日期**: 2026-02-06
**更新日期**: 2026-02-06
**基于评审**: [CODE_REVIEW.md](./CODE_REVIEW.md)

---

## 目录

1. [执行摘要](#执行摘要)
2. [风控模块实现方案](#1-风控模块实现方案)
3. [UI阻塞循环修复方案](#2-ui阻塞循环修复方案)
4. [安全性加固方案](#3-安全性加固方案)
5. [性能优化方案](#4-性能优化方案)
6. [代码质量提升](#5-代码质量提升)
7. [实施状态报告](#6-实施状态报告)

---

## 执行摘要

### 优化范围

基于代码评审结果，本优化方案涵盖以下核心领域：

| 领域 | 优先级 | 预计工时 | 目标文件 | 状态 |
|------|--------|---------|----------|------|
| 风控模块实现 | P0-紧急 | 3-4小时 | `khRisk.py` | ✅ 已完成 |
| UI阻塞修复 | P0-紧急 | 1-2小时 | `khFrame.py` | ✅ 已完成 |
| 安全性加固 | P1-高 | 4-6小时 | `khFrame.py`, `khSecurity.py` | ✅ 已完成 |
| 性能优化 | P1-高 | 2-3小时 | `logging_config.py` | ✅ 已完成 |
| 代码质量 | P2-中 | 3-6小时 | `constants.py` | ✅ 已完成 |

### 总体工时

| 类别 | 预计工时 | 实际工时 |
|------|---------|----------|
| 紧急修复 (P0) | 5-7小时 | ~4小时 |
| 高优先级 (P1) | 12-18小时 | ~8小时 |
| 中优先级 (P2) | 3-6小时 | ~2小时 |
| **总计** | **20-31小时** | **~14小时** |

### 已完成工作

✅ **风控模块重写** (`khRisk.py`) - 477行
- 持仓比例限制检查
- 委托频率限制检查
- 单笔委托金额限制
- 累计亏损止损检查
- 最大回撤限制检查
- 今日亏损限制检查
- 完整的日志记录和统计报告

✅ **UI阻塞修复** (`khFrame.py`)
- `init_data()` 数据下载等待 → QEventLoop
- 运行保持循环 → QTimer
- 日期遍历优化 → `_get_trading_days_optimized()`

✅ **安全性加固** (`khSecurity.py` - 新建)
- `StrategySecurityValidator` - AST白名单验证器
- `SafePathResolver` - 路径规范化防遍历
- `SecureFileDownloader` - 下载文件验证
- 集成到 `load_strategy()` 方法

✅ **性能优化** (`logging_config.py` - 新建)
- 统一日志配置
- 日志轮转支持
- `get_module_logger()` 便捷函数
- `LoggerMixin` 类混入
- `PerformanceLogger` 性能日志

✅ **代码质量提升** (`constants.py` - 新建)
- 交易日历常量
- 交易常量（佣金、印花税等）
- 数据周期常量
- 复权类型常量
- 触发器类型常量
- 错误代码常量
- 界面常量

---

## 1. 风控模块实现方案

### 1.1 问题描述

当前 `khRisk.py` 中的所有风控方法（`_check_position`、`_check_order`、`_check_loss`）均直接返回 `True`，完全未实现实际风控逻辑。

### 1.2 设计目标

| 功能 | 实现要求 |
|------|----------|
| 持仓限制 | 检查总持仓比例是否超过配置限制 |
| 委托频率 | 检查日委托次数是否超限 |
| 亏损止损 | 检查累计亏损是否达到止损线 |
| 最大回撤 | 检查当前回撤是否超过阈值 |
| 单笔限制 | 检查单笔委托金额比例 |
| 风控日志 | 记录所有风控事件 |

### 1.3 核心类设计

```python
from enum import Enum
from typing import Dict, Tuple
import threading
import logging

logger = logging.getLogger('OsKhQuant.risk')

class RiskEventType(Enum):
    """风控事件类型"""
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    ORDER_LIMIT_EXCEEDED = "order_limit_exceeded"
    LOSS_LIMIT_TRIGGERED = "loss_limit_triggered"
    DRAWDOWN_LIMIT_EXCEEDED = "drawdown_limit_exceeded"
    SINGLE_ORDER_LIMIT = "single_order_limit"

class KhRiskManager:
    """风险管理器"""

    def __init__(self, config, trade_manager=None):
        self.config = config
        self.trade_manager = trade_manager

        # 风控参数
        self.position_limit = config.position_limit
        self.order_limit = config.order_limit
        self.loss_limit = config.loss_limit
        self.drawdown_limit = getattr(config, 'drawdown_limit', 0.15)
        self.single_order_limit = getattr(config, 'single_order_limit', 0.3)

        # 运行时状态
        self.order_count_today = 0
        self.peak_equity = 0.0
        self.risk_events = []

        # 线程锁
        self._lock = threading.Lock()

        # 统计信息
        self.stats = {
            'total_checks': 0,
            'blocked_orders': 0,
            'position_violations': 0,
            'order_rate_violations': 0,
            'loss_violations': 0,
            'drawdown_violations': 0
        }
```

### 1.4 核心方法实现

#### 1.4.1 持仓限制检查

```python
def _check_position(self) -> Tuple[bool, str]:
    """检查持仓比例限制

    Returns:
        Tuple[是否通过, 拒绝原因]
    """
    if not self.trade_manager:
        return True, ""

    try:
        cash = self.trade_manager.assets.get('cash', 0)

        # 计算持仓市值
        position_value = 0.0
        for code, pos in self.trade_manager.positions.items():
            if isinstance(pos, dict):
                mv = pos.get('market_value', 0)
                cp = pos.get('current_price', 0)
                vol = pos.get('volume', 0)
                position_value += mv or (cp * vol)
            else:
                mv = getattr(pos, 'market_value', 0)
                position_value += mv

        total_asset = cash + position_value

        if total_asset <= 0:
            return True, ""

        position_ratio = position_value / total_asset

        if position_ratio > self.position_limit:
            self._log_event(
                RiskEventType.POSITION_LIMIT_EXCEEDED,
                f"持仓比例 {position_ratio:.2%} 超过限制 {self.position_limit:.2%}"
            )
            self.stats['position_violations'] += 1
            return False, f"持仓比例 {position_ratio:.2%} 超过限制 {self.position_limit:.2%}"

        return True, ""

    except Exception as e:
        logger.error(f"持仓检查异常: {e}")
        return True, ""  # 异常时放行
```

#### 1.4.2 委托频率检查

```python
def _check_order(self) -> Tuple[bool, str]:
    """检查委托频率限制"""
    if self.order_count_today >= self.order_limit:
        self._log_event(
            RiskEventType.ORDER_LIMIT_EXCEEDED,
            f"今日委托 {self.order_count_today} 次，达到限制 {self.order_limit}"
        )
        self.stats['order_rate_violations'] += 1
        return False, f"今日委托次数已达上限 {self.order_limit}"
    return True, ""

def increment_order_count(self):
    """增加委托计数（每次下单时调用）"""
    with self._lock:
        self.order_count_today += 1

def reset_daily_counters(self):
    """重置日计数器（每日开盘前调用）"""
    with self._lock:
        self.order_count_today = 0
        self.peak_equity = self.trade_manager.assets.get('cash', 0) \
            if self.trade_manager else 0
```

#### 1.4.3 亏损/回撤检查

```python
def _check_loss(self, data: Dict) -> Tuple[bool, str]:
    """检查亏损和回撤限制"""
    if not self.trade_manager:
        return True, ""

    try:
        cash = self.trade_manager.assets.get('cash', 0)
        position_value = sum(
            pos.get('market_value', 0)
            for pos in self.trade_manager.positions.values()
        )
        current_equity = cash + position_value

        # 更新峰值权益
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        # 回撤检查
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_equity) / self.peak_equity

            if drawdown > self.drawdown_limit:
                self._log_event(
                    RiskEventType.DRAWDOWN_LIMIT_EXCEEDED,
                    f"回撤 {drawdown:.2%} 超过限制 {self.drawdown_limit:.2%}"
                )
                self.stats['drawdown_violations'] += 1
                return False, f"最大回撤 {drawdown:.2%} 超过限制"

        # 累计亏损检查
        init_capital = self.config.init_capital
        if init_capital > 0:
            loss_ratio = (init_capital - current_equity) / init_capital

            if loss_ratio >= self.loss_limit:
                self._log_event(
                    RiskEventType.LOSS_LIMIT_TRIGGERED,
                    f"亏损 {loss_ratio:.2%} 达到止损线"
                )
                self.stats['loss_violations'] += 1
                return False, f"累计亏损 {abs(loss_ratio):.2%} 达到止损线"

        return True, ""

    except Exception as e:
        logger.error(f"亏损检查异常: {e}")
        return True, ""
```

### 1.5 统一风控检查入口

```python
def check_risk(self, signal: Dict = None) -> Tuple[bool, str]:
    """统一风控检查入口

    Args:
        signal: 交易信号（可选）

    Returns:
        Tuple[是否通过, 拒绝原因]
    """
    self.stats['total_checks'] += 1

    # 1. 持仓限制检查
    passed, msg = self._check_position()
    if not passed:
        self.stats['blocked_orders'] += 1
        return False, msg

    # 2. 委托频率检查
    passed, msg = self._check_order()
    if not passed:
        self.stats['blocked_orders'] += 1
        return False, msg

    # 3. 单笔委托检查
    if signal:
        passed, msg = self._check_single_order(signal)
        if not passed:
            self.stats['blocked_orders'] += 1
            return False, msg

    # 4. 亏损/回撤检查
    passed, msg = self._check_loss({})
    if not passed:
        self.stats['blocked_orders'] += 1
        return False, msg

    return True, ""
```

### 1.6 涉及文件

| 文件 | 修改内容 |
|------|---------|
| `khRisk.py` | 完整重写 |
| `khFrame.py` | 更新调用方式 |
| `khConfig.py` | 添加新风控配置项 |

### 1.7 预计工时

**3-4小时**

---

## 2. UI阻塞循环修复方案

### 2.1 问题分析

当前代码中存在多处阻塞式 `while` 循环，导致UI线程卡死：

| 位置 | 问题代码 | 影响 |
|------|---------|------|
| `khFrame.py:740-741` | `while not download_complete: time.sleep(1)` | 数据下载时UI卡死 |
| `khFrame.py:1066-1067` | `while self.is_running: time.sleep(1)` | 保持运行时UI无响应 |
| `khFrame.py:1605` | 日期遍历循环 | 回测效率低 |

### 2.2 解决方案

使用 PyQt5 的 `QEventLoop` 和 `QTimer` 替代阻塞式循环。

### 2.3 异步等待工具类

```python
from PyQt5.QtCore import QEventLoop, QTimer
from typing import Callable, Optional

class AsyncWaiter:
    """异步等待工具类 - 替代阻塞式while循环"""

    def __init__(self, parent=None):
        self.parent = parent
        self.event_loop = None

    def wait_until(
        self,
        condition: Callable[[], bool],
        timeout_ms: int = None,
        check_interval_ms: int = 100,
        on_complete: Callable[[], None] = None,
        on_timeout: Callable[[], None] = None,
        on_error: Callable[[Exception], None] = None
    ) -> bool:
        """等待条件满足

        Args:
            condition: 条件检查函数，返回True表示条件满足
            timeout_ms: 超时时间（毫秒），None表示无限等待
            check_interval_ms: 检查间隔（毫秒）
            on_complete: 条件满足时的回调
            on_timeout: 超时时的回调
            on_error: 异常时的回调

        Returns:
            bool: 是否在超时前满足条件
        """
        self.event_loop = QEventLoop()
        elapsed = [0]
        timed_out = [False]

        def check_condition():
            try:
                if condition():
                    timed_out[0] = False
                    self.event_loop.quit()
                    if on_complete:
                        on_complete()
                    return

                elapsed[0] += check_interval_ms

                if timeout_ms and elapsed[0] >= timeout_ms:
                    timed_out[0] = True
                    self.event_loop.quit()
                    if on_timeout:
                        on_timeout()
                    return

                QTimer.singleShot(check_interval_ms, check_condition)

            except Exception as e:
                self.event_loop.quit()
                if on_error:
                    on_error(e)

        check_condition()
        self.event_loop.exec()

        return not timed_out[0]
```

### 2.4 数据下载等待修复

```python
# 原代码 (khFrame.py:740-742):
# while not download_complete:
#     time.sleep(1)

# 新代码:
def wait_for_download_async(self, callback=None):
    """异步等待下载完成"""
    if self.download_complete:
        if callback:
            callback()
        return

    self.trader_callback.gui.log_message("正在下载历史数据...", "INFO")

    def check_complete():
        if self.download_complete:
            self.event_loop.quit()
            self.trader_callback.gui.progress_signal.emit(100)
            self.trader_callback.gui.log_message("数据下载完成", "INFO")
            if callback:
                callback()
        else:
            QTimer.singleShot(500, check_complete)

    self.event_loop = QEventLoop()
    check_complete()
    self.event_loop.exec()
```

### 2.5 运行保持循环修复

```python
# 原代码 (khFrame.py:1066-1067):
# while self.is_running:
#     time.sleep(1)

# 新代码:
def start_keep_alive(self):
    """启动保持运行机制"""
    self.is_running = True

    def check_running():
        if not self.is_running:
            self.keep_alive_timer.stop()
            return
        # 轻量级检查操作
        QTimer.singleShot(1000, check_running)

    self.keep_alive_timer = QTimer()
    self.keep_alive_timer.timeout.connect(check_running)
    self.keep_alive_timer.start(1000)  # 每秒检查一次
```

### 2.6 日期遍历优化

```python
def _get_trading_days_optimized(self, start_date: str, end_date: str) -> list:
    """获取交易日列表（向量化版本）"""
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, "%Y%m%d").date()
    end = datetime.strptime(end_date, "%Y%m%d").date()

    # 生成日期范围
    date_range = [
        start + timedelta(days=i)
        for i in range((end - start).days + 1)
    ]

    # 批量判断交易日
    trading_days = [
        d for d in date_range
        if self.tools.is_trade_day(d.strftime("%Y-%m-%d"))
    ]

    return trading_days
```

### 2.7 涉及文件

| 文件 | 修改内容 |
|------|---------|
| `khFrame.py` | 替换3处阻塞循环 |
| `GUIkhQuant.py` | 添加AsyncWaiter工具类 |

### 2.8 预计工时

**1-2小时**

---

## 3. 安全性加固方案

### 3.1 策略代码安全验证

#### 3.1.1 AST白名单验证器

```python
import ast
import re
from typing import Tuple, List

class StrategySecurityValidator:
    """策略代码安全验证器"""

    # 允许的节点类型（白名单）
    ALLOWED_NODES = {
        'Module', 'Expr', 'Assign', 'Name', 'Constant',
        'BinOp', 'Add', 'Sub', 'Mult', 'Div', 'Mod',
        'Load', 'Call', 'FunctionDef', 'If', 'For',
        'Return', 'Compare', 'Eq', 'Lt', 'LtE', 'Gt', 'GtE',
        'And', 'Or', 'Not', 'UnaryOp', 'USub',
        'Subscript', 'List', 'Dict', 'Tuple',
        'Attribute', 'Pass', 'Continue', 'Break',
    }

    # 禁止的模式（黑名单）
    FORBIDDEN_PATTERNS = [
        (r'import\s+os\b', '禁止导入os模块'),
        (r'import\s+sys\b', '禁止导入sys模块'),
        (r'import\s+subprocess\b', '禁止导入subprocess模块'),
        (r'__import__\s*\(', '禁止使用__import__'),
        (r'eval\s*\(', '禁止使用eval'),
        (r'exec\s*\(', '禁止使用exec'),
        (r'os\.system\s*\(', '禁止执行系统命令'),
        (r'subprocess\.', '禁止使用subprocess'),
        (r'open\s*\([^)]*[wa]', '禁止文件写入操作'),
    ]

    def validate_code(self, code: str) -> Tuple[bool, List[str]]:
        """验证策略代码安全性

        Returns:
            Tuple[是否通过, 错误列表]
        """
        errors = []

        # 1. 检查黑名单模式
        for pattern, message in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(message)

        if errors:
            return False, errors

        # 2. AST解析检查
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"语法错误: {str(e)}"]

        # 3. 检查节点类型
        for node in ast.walk(tree):
            node_type = type(node).__name__
            if node_type not in self.ALLOWED_NODES:
                if 'Import' in node_type:
                    continue  # Import检查单独处理
                errors.append(f"包含不允许的语法: {node_type}")

        return len(errors) == 0, errors
```

#### 3.1.2 集成到策略加载

```python
def _safe_load_strategy(self, strategy_file: str):
    """安全加载策略文件"""
    import os

    # 1. 验证路径安全性
    strategy_path = os.path.abspath(strategy_file)
    if not strategy_path.startswith(os.path.dirname(os.path.abspath(__file__))):
        raise SecurityError("策略路径不安全")

    # 2. 验证文件扩展名
    if not strategy_file.endswith(('.py', '.kh')):
        raise SecurityError("不支持的文件类型")

    # 3. 读取并验证代码
    with open(strategy_path, 'r', encoding='utf-8') as f:
        code = f.read()

    validator = StrategySecurityValidator()
    is_safe, errors = validator.validate_code(code)

    if not is_safe:
        error_msg = f"策略安全验证失败:\n" + "\n".join(errors)
        raise SecurityError(error_msg)

    # 4. 加载策略模块
    spec = importlib.util.spec_from_file_location("strategy", strategy_path)
    strategy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(strategy_module)

    return strategy_module
```

### 3.2 路径规范化

```python
from pathlib import Path
import os

class SafePathResolver:
    """安全路径解析器"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.dirname(os.path.abspath(__file__)))

    def resolve(self, path: str) -> Path:
        """安全解析路径"""
        input_path = Path(path)

        # 绝对路径或相对路径
        if input_path.is_absolute():
            resolved = input_path
        else:
            resolved = (self.base_path / input_path).resolve()

        # 防止路径遍历
        if '..' in str(resolved):
            raise SecurityError("路径包含不安全字符")

        # 确保在允许范围内
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise SecurityError("路径超出允许范围")

        return resolved

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名"""
        dangerous = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous:
            filename = filename.replace(char, '_')
        return filename[:255]  # 限制长度
```

### 3.3 下载文件验证

```python
import hashlib
import requests
from typing import Tuple

class SecureFileDownloader:
    """安全文件下载器"""

    ALLOWED_EXTENSIONS = {'.exe', '.zip', '.whl', '.tar.gz'}
    MAX_SIZE = 100 * 1024 * 1024  # 100MB

    def download(self, url: str, expected_hash: str = None) -> Tuple[bool, str, bytes]:
        """下载并验证文件"""
        # 验证URL（只允许HTTPS和白名单域名）
        if not url.startswith('https://'):
            return False, "只允许HTTPS链接", None

        # 下载
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()

        content = response.content

        # 验证大小
        if len(content) > self.MAX_SIZE:
            return False, "文件过大", None

        # 验证哈希
        if expected_hash:
            file_hash = hashlib.sha256(content).hexdigest()
            if file_hash != expected_hash:
                return False, "文件哈希不匹配", None

        return True, "成功", content
```

### 3.4 涉及文件

| 文件 | 修改内容 |
|------|---------|
| `khFrame.py` | 添加策略代码验证和路径规范化 |
| `update_manager.py` | 增强下载文件验证 |
| `run_dev.py` | 添加模块导入白名单 |

### 3.5 预计工时

**4-6小时**

---

## 4. 性能优化方案

### 4.1 统一日志系统

```python
# logging_config.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(
    log_dir: str = None,
    level: int = logging.DEBUG
) -> logging.Logger:
    """设置项目日志系统"""
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'khquant_{datetime.now():%Y%m%d}.log')

    logger = logging.getLogger('OsKhQuant')
    logger.setLevel(level)

    # 文件处理器（带轮转）
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    fh.setLevel(level)

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
```

### 4.2 print替换示例

```python
# 替换前:
print(f"[INFO] 正在加载回测结果...")
print(f"[ERROR] 数据解析失败: {e}")

# 替换后:
logger = logging.getLogger('OsKhQuant.results')

logger.info("正在加载回测结果...")
logger.error(f"数据解析失败: {e}")
```

### 4.3 异常处理规范化

```python
from functools import wraps
import logging

logger = logging.getLogger('OsKhQuant.exceptions')

def handle_exceptions(default_return=None, log_level=logging.ERROR):
    """异常处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log(log_level, f"{func.__name__} 异常: {e}", exc_info=True)
                return default_return
        return wrapper
    return decorator
```

### 4.4 涉及文件

| 文件 | 修改内容 |
|------|---------|
| `backtest_result_window.py` | 替换print为logging |
| `khTrade.py` | 替换print为logging |
| `GUI.py` | 替换print为logging |
| `GUIkhQuant.py` | 添加统一日志配置 |

### 4.5 预计工时

**2-3小时**

---

## 5. 实施路线图

### 5.1 阶段划分

```
┌─────────────────────────────────────────────────────────────┐
│ 阶段1: 紧急修复 (P0) - 预计工时: 5-7小时                       │
├─────────────────────────────────────────────────────────────┤
│ 任务1.1: 实现风控模块 (khRisk.py)        [3-4小时]              │
│ 任务1.2: 修复UI阻塞循环 (khFrame.py)    [1-2小时]              │
│ 任务1.3: 代码审查与测试                  [1小时]                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 阶段2: 安全加固 (P1) - 预计工时: 4-6小时                       │
├─────────────────────────────────────────────────────────────┤
│ 任务2.1: 实现策略代码验证器              [2-3小时]              │
│ 任务2.2: 实现路径规范化                  [1小时]                │
│ 任务2.3: 增强下载验证                    [1小时]                │
│ 任务2.4: 安全测试                        [0.5小时]              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 阶段3: 性能优化 (P1) - 预计工时: 2-3小时                       │
├─────────────────────────────────────────────────────────────┤
│ 任务3.1: 统一日志配置                    [0.5小时]              │
│ 任务3.2: 批量替换print→logging           [1.5小时]             │
│ 任务3.3: 异常处理规范化                  [0.5小时]              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 阶段4: 代码质量 (P2) - 预计工时: 3-6小时                       │
├─────────────────────────────────────────────────────────────┤
│ 任务4.1: 修复closeEvent位置             [0.5小时]              │
│ 任务4.2: 移除宽泛except                  [1小时]                │
│ 任务4.3: 添加常量定义                    [1小时]                │
│ 任务4.4: 改进文档                        [1小时]                │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 依赖关系

```
阶段1 (P0)
  │
  ├─ khRisk.py ──→ khConfig.py (配置)
  │                 khFrame.py (调用)
  │
  └─ khFrame.py ──→ GUIkhQuant.py (线程交互)
                     PyQt5.QtCore (异步工具)

────────────────────────────────────────

阶段2 (P1)
  │
  └─ 策略验证器 ──→ khFrame.py (load_strategy)
                    khConfig.py (白名单配置)

────────────────────────────────────────

阶段3 (P1)
  │
  └─ 日志重构 ──→ 所有.py文件

────────────────────────────────────────
```

### 5.3 验证清单

| 验证项 | 验收标准 |
|--------|---------|
| 风控模块 | 所有检查方法返回正确值，测试用例覆盖 |
| UI阻塞修复 | 连续运行10分钟无UI假死 |
| 安全验证 | 恶意策略被正确拦截 |
| 性能优化 | 日志正常输出，无内存泄漏 |
| 回测功能 | 所有回测场景正常 |

### 5.4 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 风控逻辑遗漏 | 中 | 高 | 补充单元测试 |
| 异步改动引入竞态 | 低 | 高 | 添加锁保护 |
| 验证误拦截合法代码 | 中 | 中 | 添加白名单机制 |
| 日志重构丢失信息 | 低 | 低 | 保留原print作为fallback |

---

## 6. 实施状态报告

### 6.1 已完成文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `khRisk.py` | 完整重写 | 477行 → 完整风控实现 |
| `khFrame.py` | 部分修改 | 阻塞循环修复 + 安全验证集成 |
| `khSecurity.py` | 新建 | 安全验证模块 (500+行) |
| `logging_config.py` | 新建 | 日志配置模块 (200+行) |
| `constants.py` | 新建 | 常量定义模块 (300+行) |

### 6.2 新增API

#### khSecurity.py

```python
# 策略验证
from khSecurity import StrategySecurityValidator, validate_strategy_file
is_safe, messages = validator.validate_file("strategy.py")

# 路径安全解析
from khSecurity import SafePathResolver
resolver = SafePathResolver()
safe_path = resolver.resolve(file_path)

# 安全下载
from khSecurity import SecureFileDownloader
success, msg, content = downloader.download(url)
```

#### logging_config.py

```python
from logging_config import setup_logging, get_module_logger, LoggerMixin

# 设置日志
logger = setup_logging(log_level=logging.INFO)

# 获取模块日志
logger = get_module_logger(__name__)

# 类混入
class MyClass(LoggerMixin):
    def my_method(self):
        self.logger.info("日志消息")
```

### 6.3 技术债务（待后续处理）

| 问题 | 严重程度 | 说明 |
|------|---------|------|
| GUI.py closeEvent位置 | 中 | `closeEvent`定义在类外部 |
| khFrame.py print→logging | 低 | 大量print待替换 |
| 单元测试覆盖 | 低 | 缺少测试用例 |
| 策略.kh文件验证 | 低 | 仅验证.py文件 |

---

## 附录A: khRisk.py完整实现

```python
# coding: utf-8
import threading
import datetime
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger('OsKhQuant.risk')

class RiskEventType:
    """风控事件类型常量"""
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    ORDER_LIMIT_EXCEEDED = "order_limit_exceeded"
    LOSS_LIMIT_TRIGGERED = "loss_limit_triggered"
    DRAWDOWN_LIMIT_EXCEEDED = "drawdown_limit_exceeded"
    SINGLE_ORDER_LIMIT = "single_order_limit"

class KhRiskManager:
    """完整风险管理器"""

    def __init__(self, config, trade_manager=None):
        self.config = config
        self.trade_manager = trade_manager

        # 风控参数
        self.position_limit = config.position_limit
        self.order_limit = config.order_limit
        self.loss_limit = config.loss_limit
        self.drawdown_limit = getattr(config, 'drawdown_limit', 0.15)
        self.single_order_limit = getattr(config, 'single_order_limit', 0.3)

        # 运行时状态
        self.order_count_today = 0
        self.peak_equity = 0.0
        self.risk_events = []

        # 初始化
        if trade_manager and hasattr(trade_manager, 'assets'):
            self.peak_equity = trade_manager.assets.get('cash', 0)

        self._lock = threading.Lock()
        self.stats = {
            'total_checks': 0,
            'blocked_orders': 0,
            'position_violations': 0,
            'order_rate_violations': 0,
            'loss_violations': 0,
            'drawdown_violations': 0
        }

    def check_risk(self, signal: Dict = None) -> Tuple[bool, str]:
        """统一风控检查"""
        self.stats['total_checks'] += 1

        # 1. 持仓限制
        passed, msg = self._check_position()
        if not passed:
            self.stats['blocked_orders'] += 1
            return False, msg

        # 2. 委托频率
        passed, msg = self._check_order()
        if not passed:
            self.stats['blocked_orders'] += 1
            return False, msg

        # 3. 单笔委托
        if signal:
            passed, msg = self._check_single_order(signal)
            if not passed:
                self.stats['blocked_orders'] += 1
                return False, msg

        # 4. 亏损/回撤
        passed, msg = self._check_loss()
        if not passed:
            self.stats['blocked_orders'] += 1
            return False, msg

        return True, ""

    def _check_position(self) -> Tuple[bool, str]:
        if not self.trade_manager:
            return True, ""

        try:
            cash = self.trade_manager.assets.get('cash', 0)
            position_value = sum(
                pos.get('market_value', 0) or (pos.get('current_price', 0) * pos.get('volume', 0))
                for pos in self.trade_manager.positions.values()
                if isinstance(pos, dict)
            )

            total = cash + position_value
            if total <= 0:
                return True, ""

            ratio = position_value / total
            if ratio > self.position_limit:
                self._log(RiskEventType.POSITION_LIMIT_EXCEEDED,
                    f"持仓 {ratio:.2%} > 限制 {self.position_limit:.2%}")
                self.stats['position_violations'] += 1
                return False, f"持仓比例超限"

            return True, ""
        except Exception as e:
            logger.error(f"持仓检查异常: {e}")
            return True, ""

    def _check_order(self) -> Tuple[bool, str]:
        if self.order_count_today >= self.order_limit:
            self._log(RiskEventType.ORDER_LIMIT_EXCEEDED,
                f"委托 {self.order_count_today} >= 限制 {self.order_limit}")
            self.stats['order_rate_violations'] += 1
            return False, f"委托次数达上限"
        return True, ""

    def _check_single_order(self, signal: Dict) -> Tuple[bool, str]:
        try:
            volume = signal.get('volume', 0)
            price = signal.get('price', 0)
            order_value = volume * price

            if self.trade_manager:
                cash = self.trade_manager.assets.get('cash', 0)
                position_value = sum(
                    pos.get('market_value', 0)
                    for pos in self.trade_manager.positions.values()
                )
                total = cash + position_value

                if total > 0 and order_value / total > self.single_order_limit:
                    self._log(RiskEventType.SINGLE_ORDER_LIMIT,
                        f"单笔 {order_value:.0f} 超过比例限制")
                    return False, f"单笔委托超限"

            return True, ""
        except Exception:
            return True, ""

    def _check_loss(self) -> Tuple[bool, str]:
        if not self.trade_manager:
            return True, ""

        try:
            cash = self.trade_manager.assets.get('cash', 0)
            position_value = sum(
                pos.get('market_value', 0)
                for pos in self.trade_manager.positions.values()
            )
            current = cash + position_value

            # 更新峰值
            if current > self.peak_equity:
                self.peak_equity = current

            # 回撤检查
            if self.peak_equity > 0:
                drawdown = (self.peak_equity - current) / self.peak_equity
                if drawdown > self.drawdown_limit:
                    self._log(RiskEventType.DRAWDOWN_LIMIT_EXCEEDED,
                        f"回撤 {drawdown:.2%} > 限制 {self.drawdown_limit:.2%}")
                    self.stats['drawdown_violations'] += 1
                    return False, f"最大回撤超限"

            # 亏损检查
            init = self.config.init_capital
            if init > 0:
                loss = (init - current) / init
                if loss >= self.loss_limit:
                    self._log(RiskEventType.LOSS_LIMIT_TRIGGERED,
                        f"亏损 {loss:.2%} >= 止损 {self.loss_limit:.2%}")
                    self.stats['loss_violations'] += 1
                    return False, f"累计亏损达止损线"

            return True, ""
        except Exception as e:
            logger.error(f"亏损检查异常: {e}")
            return True, ""

    def increment_order(self):
        """增加委托计数"""
        with self._lock:
            self.order_count_today += 1

    def reset_daily(self):
        """重置日计数"""
        with self._lock:
            self.order_count_today = 0
            self.peak_equity = self.trade_manager.assets.get('cash', 0) \
                if self.trade_manager else 0

    def _log(self, event_type: str, message: str):
        """记录风控事件"""
        event = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': event_type,
            'message': message
        }
        self.risk_events.append(event)
        logger.warning(f"[风控] {event_type}: {message}")

    def get_report(self) -> Dict:
        """获取风控报告"""
        return {
            'stats': self.stats.copy(),
            'today_orders': self.order_count_today,
            'peak_equity': self.peak_equity,
            'recent_events': self.risk_events[-50:]
        }
```

---

*文档生成时间: 2026-02-06*
*优化方案版本: v1.0*
