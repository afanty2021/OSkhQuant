# coding: utf-8
"""
实盘交易引擎模块
提供实时行情监控和自动交易功能

@author: OsKhQuant
@version: 1.0
"""

# ===== 标准库导入 =====
import os
import sys
import time
import json
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta

# ===== 第三方库导入 =====
import numpy as np
import pandas as pd
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant import xtconstant

# ===== 项目内部导入 =====
from khAlertManager import KhAlertManager, AlertType, AlertDirection
from khTrade import KhTradeManager
from khQuantImport import (
    parse_context, khGet, khPrice, khHas, khHistory,
    generate_signal, StrategyContext
)
from khQTTools import is_trade_time, is_trade_day


# =============================================================================
# 实时交易引擎
# =============================================================================

class RealtimeTrader:
    """
    实盘交易引擎

    功能：
    - 实时行情订阅（5分钟K线）
    - 策略信号自动生成
    - 自动下单执行
    - 提醒功能集成
    """

    def __init__(self,
                 config: Dict[str, Any],
                 strategy_file: str,
                 alert_manager: Optional[KhAlertManager] = None,
                 user_callback: Optional[Callable] = None):
        """
        初始化实盘交易引擎

        Args:
            config: 配置字典
                - path: MiniQMT用户目录
                - stock_list: 股票池列表
                - period: K线周期（默认'5m'）
                - auto_reconnect: 是否自动重连
            strategy_file: 策略文件路径
            alert_manager: 提醒管理器实例
            user_callback: 用户自定义回调函数
        """
        self.logger = logging.getLogger("RealtimeTrader")
        self.config = config or {}
        self.strategy_file = strategy_file
        self.alert_manager = alert_manager
        self.user_callback = user_callback

        # 交易相关
        self.trader: Optional[XtQuantTrader] = None
        self.trade_manager = KhTradeManager()
        self.session_id = int(time.time())

        # 运行时数据
        self.stock_list = config.get("stock_list", [])
        self.period = config.get("period", "5m")
        self.auto_reconnect = config.get("auto_reconnect", True)

        # 实时数据缓存: {stock_code: {field: value}}
        self.quote_data: Dict[str, Dict] = {}
        self.quote_lock = threading.Lock()

        # 策略函数
        self.init_func = None
        self.handle_func = None
        self.strategy_context: Optional[StrategyContext] = None

        # 运行状态
        self.running = False
        self.last_tick_time = {}

        # 加载策略
        self._load_strategy()

        self.logger.info("实盘交易引擎初始化完成")

    def _load_strategy(self):
        """加载策略文件"""
        if not self.strategy_file or not os.path.exists(self.strategy_file):
            self.logger.warning(f"策略文件不存在: {self.strategy_file}")
            return

        try:
            # 设置路径
            strategy_dir = os.path.dirname(self.strategy_file)
            strategy_name = os.path.splitext(os.path.basename(self.strategy_file))[0]

            if strategy_dir not in sys.path:
                sys.path.insert(0, strategy_dir)

            # 动态导入策略
            import importlib.util
            spec = importlib.util.spec_from_file_location(strategy_name, self.strategy_file)
            strategy_module = importlib.util.module_from_spec(spec)

            if spec.loader:
                spec.loader.exec_module(strategy_module)

            # 获取策略函数
            self.init_func = getattr(strategy_module, 'init', None)
            self.handle_func = getattr(strategy_module, 'khHandlebar', None)

            if self.handle_func:
                self.logger.info(f"策略加载成功: {self.strategy_file}")
            else:
                self.logger.error("策略文件中未找到 khHandlebar 函数")

        except Exception as e:
            self.logger.error(f"加载策略失败: {e}")

    def _init_trader(self):
        """初始化交易接口"""
        try:
            path = self.config.get("path", "")
            self.trader = XtQuantTrader(path, self.session_id)

            callback = _TraderCallback(self)
            self.trader.set_callback(callback)

            if self.trader.start():
                self.logger.info("交易接口启动成功")
                return True
            else:
                self.logger.error("交易接口启动失败")
                return False

        except Exception as e:
            self.logger.error(f"初始化交易接口异常: {e}")
            return False

    def _subscribe_quotes(self):
        """订阅实时行情"""
        if not self.stock_list:
            self.logger.warning("股票池为空")
            return

        try:
            for stock_code in self.stock_list:
                # 订阅5分钟K线
                xtdata.subscribe_quote(
                    stock_code=stock_code,
                    period=self.period,
                    on_push=self._on_quote_callback
                )
                self.logger.debug(f"已订阅: {stock_code} {self.period}")

        except Exception as e:
            self.logger.error(f"订阅行情失败: {e}")

    def _on_quote_callback(self, data: Dict):
        """
        行情回调函数

        Args:
            data: 包含 stock_code, time, open, high, low, close, volume 等字段
        """
        if not self.running:
            return

        try:
            stock_code = data.get("stock_code", "")

            # 更新本地缓存
            with self.quote_lock:
                self.quote_data[stock_code] = data

            # 记录时间
            current_time = time.time()
            self.last_tick_time[stock_code] = current_time

            # 执行策略
            self._run_strategy(stock_code)

        except Exception as e:
            self.logger.error(f"处理行情回调失败: {e}")

    def _build_context(self, stock_code: str) -> Dict:
        """
        构建策略执行上下文

        Args:
            stock_code: 股票代码

        Returns:
            策略上下文字典
        """
        # 获取最新行情
        with self.quote_lock:
            quote = self.quote_data.get(stock_code, {})

        # 获取时间信息
        quote_time = quote.get("time", 0)
        if isinstance(quote_time, (int, float)):
            dt = datetime.fromtimestamp(quote_time / 1000)
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
            date_num = int(dt.strftime("%Y%m%d"))
        else:
            date_str = date_str = datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.now().strftime("%H:%M:%S")
            date_num = int(datetime.now().strftime("%Y%m%d"))

        # 构建上下文
        context = {
            "date_str": date_str,
            "time_str": time_str,
            "datetime_str": f"{date_str} {time_str}",
            "date_num": str(date_num),
            "stock_code": stock_code,
        }

        # 添加价格数据
        for field in ["open", "high", "low", "close", "volume"]:
            context[field] = quote.get(field, 0)

        # 添加账户信息
        if self.trader:
            account_status = self.trader.query_account_status()
            if account_status:
                context["cash"] = account_status.get("cash", 0)
                context["total_asset"] = account_status.get("total_asset", 0)
                context["market_value"] = account_status.get("market_value", 0)

        # 添加股票池
        context["stocks"] = self.stock_list
        context["first_stock"] = self.stock_list[0] if self.stock_list else ""

        # 添加持仓信息
        if self.trader:
            positions = self.trader.query_positions()
            if positions:
                for pos in positions:
                    pos_code = pos.get("stock_code", "")
                    context[f"has_{pos_code}"] = True
                    context[f"position_{pos_code}"] = pos

        # 标记是否为实盘模式
        context["_is_realtime"] = True

        return context

    def _run_strategy(self, stock_code: str):
        """执行策略逻辑"""
        if not self.handle_func:
            return

        try:
            # 构建上下文
            context = self._build_context(stock_code)

            # 执行策略
            signals = self.handle_func(context)

            # 处理信号
            if signals:
                for signal in signals:
                    if isinstance(signal, dict):
                        # 添加提醒
                        if self.alert_manager:
                            self.alert_manager.on_signal(signal)

                        # 自动下单
                        self._place_order(signal)

            # 用户回调
            if self.user_callback:
                self.user_callback(context, signals)

        except Exception as e:
            self.logger.error(f"执行策略失败: {e}")

    def _place_order(self, signal: Dict):
        """
        执行实盘下单

        Args:
            signal: 交易信号字典
        """
        if not self.trader:
            self.logger.warning("交易接口未启动")
            return

        try:
            stock_code = signal.get("stock_code", "")
            direction = signal.get("direction", "")
            price = signal.get("price", 0)
            ratio = signal.get("ratio", 1.0)

            # 转换方向
            if direction.lower() == "buy":
                xt_direction = xtconstant.STOCK_BUY
            else:
                xt_direction = xtconstant.STOCK_SELL

            # 计算数量
            volume = self.trade_manager.calculate_max_buy_volume(
                self.trader, stock_code, price, ratio
            )

            if volume <= 0:
                self.logger.warning(f"无法计算有效交易数量: {stock_code}")
                return

            # 发送委托
            order_id = self.trader.place_order(
                stock_code=stock_code,
                direction=xt_direction,
                order_type=xtconstant.LIMIT,
                price=price,
                volume=int(volume)
            )

            if order_id > 0:
                self.logger.info(f"委托成功: {stock_code} {direction} @ {price} x {volume}")
            else:
                self.logger.error(f"委托失败: {stock_code}")

        except Exception as e:
            self.logger.error(f"下单失败: {e}")

    def start(self) -> bool:
        """
        启动实盘交易引擎

        Returns:
            启动是否成功
        """
        if self.running:
            self.logger.warning("引擎已在运行中")
            return True

        self.logger.info("启动实盘交易引擎...")

        # 初始化交易接口
        if not self._init_trader():
            return False

        # 执行初始化函数
        if self.init_func:
            try:
                init_context = {
                    "stocks": self.stock_list,
                    "_is_realtime": True
                }
                self.init_func(stock_list=self.stock_list, data=init_context)
                self.logger.info("策略初始化完成")
            except Exception as e:
                self.logger.error(f"策略初始化失败: {e}")

        # 订阅行情
        self._subscribe_quotes()

        # 设置运行状态
        self.running = True

        self.logger.info("实盘交易引擎已启动")
        return True

    def stop(self):
        """停止实盘交易引擎"""
        if not self.running:
            return

        self.logger.info("停止实盘交易引擎...")
        self.running = False

        # 取消订阅
        try:
            for stock_code in self.stock_list:
                xtdata.unsubscribe_quote(stock_code, self.period)
        except Exception as e:
            self.logger.error(f"取消订阅失败: {e}")

        # 停止交易接口
        if self.trader:
            self.trader.stop()
            self.trader = None

        self.logger.info("实盘交易引擎已停止")

    def add_stock(self, stock_code: str):
        """添加股票到监控列表"""
        if stock_code not in self.stock_list:
            self.stock_list.append(stock_code)
            if self.running:
                xtdata.subscribe_quote(
                    stock_code=stock_code,
                    period=self.period,
                    on_push=self._on_quote_callback
                )
            self.logger.info(f"添加监控股票: {stock_code}")

    def remove_stock(self, stock_code: str):
        """从监控列表移除股票"""
        if stock_code in self.stock_list:
            self.stock_list.remove(stock_code)
            if self.running:
                xtdata.unsubscribe_quote(stock_code, self.period)
            self.logger.info(f"移除监控股票: {stock_code}")

    def get_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取股票最新行情

        Args:
            stock_code: 股票代码

        Returns:
            行情数据字典
        """
        with self.quote_lock:
            return self.quote_data.get(stock_code)

    def get_all_quotes(self) -> Dict[str, Dict]:
        """获取所有股票最新行情"""
        with self.quote_lock:
            return self.quote_data.copy()


# =============================================================================
# 交易回调类
# =============================================================================

class _TraderCallback(XtQuantTraderCallback):
    """交易回调处理类"""

    def __init__(self, trader: RealtimeTrader):
        self.trader = trader
        self.logger = logging.getLogger("RealtimeTrader")

    def on_disconnected(self):
        """连接断开回调"""
        self.logger.warning("交易连接已断开")
        if self.trader.auto_reconnect:
            self.logger.info("尝试自动重连...")
            self.trader._init_trader()

    def on_account_status(self, status):
        """账户状态回调"""
        self.logger.info(f"账户状态: {status}")

    def on_order_status(self, order):
        """委托状态回调"""
        self.logger.info(f"委托状态更新: {order}")

    def on_trade(self, trade):
        """成交回调"""
        self.logger.info(f"成交记录: {trade}")

    def on_position(self, position):
        """持仓回调"""
        self.logger.debug(f"持仓更新: {position}")

    def on_asset(self, asset):
        """资产回调"""
        self.logger.debug(f"资产更新: {asset}")


# =============================================================================
# 便捷函数
# =============================================================================

def create_realtime_trader(
    config: Dict[str, Any],
    strategy_file: str,
    alert_manager: Optional[KhAlertManager] = None,
    user_callback: Optional[Callable] = None
) -> RealtimeTrader:
    """
    创建实盘交易引擎的便捷函数

    Args:
        config: 配置字典
        strategy_file: 策略文件路径
        alert_manager: 提醒管理器
        user_callback: 用户回调函数

    Returns:
        RealtimeTrader实例
    """
    return RealtimeTrader(config, strategy_file, alert_manager, user_callback)


def test_realtime_trader():
    """测试实盘交易引擎（模拟模式）"""
    print("=== 测试实盘交易引擎 ===")

    # 注意：此测试需要MiniQMT运行环境

    # 配置
    config = {
        "path": "",  # MiniQMT用户目录
        "stock_list": ["000001.SZ", "600036.SH"],
        "period": "5m",
        "auto_reconnect": True
    }

    # 创建提醒管理器（仅声音）
    alert_config = {
        "sound_enabled": True,
        "wechat_enabled": False
    }
    alert_mgr = KhAlertManager(alert_config)

    # 创建交易引擎
    trader = RealtimeTrader(
        config=config,
        strategy_file="",
        alert_manager=alert_mgr
    )

    print(f"股票池: {trader.stock_list}")
    print(f"K线周期: {trader.period}")
    print(f"提醒管理器已配置: {alert_mgr is not None}")


if __name__ == "__main__":
    test_realtime_trader()
