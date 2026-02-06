# coding: utf-8
"""
风险管理模块

提供完整的风险管理功能：
- 持仓比例限制检查
- 委托频率限制检查
- 单笔委托金额限制
- 累计亏损止损检查
- 最大回撤限制检查
- 风控事件日志记录

@author: OsKhQuant
@version: 1.0
"""

import threading
import datetime
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger('OsKhQuant.risk')


class RiskEventType:
    """风控事件类型常量"""
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    ORDER_LIMIT_EXCEEDED = "order_limit_exceeded"
    LOSS_LIMIT_TRIGGERED = "loss_limit_triggered"
    DRAWDOWN_LIMIT_EXCEEDED = "drawdown_limit_exceeded"
    SINGLE_ORDER_LIMIT = "single_order_limit"
    DAILY_LOSS_LIMIT = "daily_loss_limit"


class KhRiskManager:
    """风险管理器

    提供完整的风险管理功能，包括持仓限制、委托频率限制、
    亏损止损和回撤限制等。

    Attributes:
        config: 配置对象，包含风控参数
        trade_manager: 交易管理器实例（可选）
        position_limit: 持仓比例限制 (0.0-1.0)
        order_limit: 日委托次数限制
        loss_limit: 累计亏损止损比例
        drawdown_limit: 最大回撤限制
        single_order_limit: 单笔委托金额比例限制
    """

    def __init__(self, config, trade_manager=None):
        """初始化风险管理器

        Args:
            config: 配置对象，必须包含以下属性：
                - position_limit: 持仓比例限制 (默认0.95)
                - order_limit: 日委托次数限制 (默认100)
                - loss_limit: 累计亏损止损比例 (默认0.1)
                - init_capital: 初始资金 (默认1000000)
            trade_manager: 交易管理器实例（可选）
        """
        self.config = config
        self.trade_manager = trade_manager

        # 风控参数 - 从配置读取，添加默认值保护
        self.position_limit = getattr(config, 'position_limit', 0.95)
        self.order_limit = getattr(config, 'order_limit', 100)
        self.loss_limit = getattr(config, 'loss_limit', 0.1)
        self.drawdown_limit = getattr(config, 'drawdown_limit', 0.15)
        self.single_order_limit = getattr(config, 'single_order_limit', 0.3)
        self.daily_loss_limit = getattr(config, 'daily_loss_limit', 0.05)

        # 运行时状态
        self.order_count_today = 0
        self.daily_pnl = 0.0  # 今日盈亏
        self.peak_equity = 0.0
        self.risk_events: List[Dict] = []

        # 初始化峰值权益
        if trade_manager and hasattr(trade_manager, 'assets'):
            cash = trade_manager.assets.get('cash', 0) if isinstance(trade_manager.assets, dict) else 0
            self.peak_equity = cash

        # 线程锁 - 保护并发访问
        self._lock = threading.Lock()

        # 统计信息
        self.stats = {
            'total_checks': 0,
            'blocked_orders': 0,
            'position_violations': 0,
            'order_rate_violations': 0,
            'loss_violations': 0,
            'drawdown_violations': 0,
            'single_order_violations': 0,
            'daily_loss_violations': 0
        }

        logger.info(f"风控模块初始化完成 - 持仓限制:{self.position_limit:.0%}, "
                   f"委托限制:{self.order_limit}, 止损:{self.loss_limit:.0%}, "
                   f"回撤:{self.drawdown_limit:.0%}")

    def check_risk(self, signal: Dict = None) -> Tuple[bool, str]:
        """统一风控检查入口

        对交易信号进行全面的风控检查，包括持仓限制、委托频率、
        单笔委托和亏损回撤等。

        Args:
            signal: 交易信号字典，可包含：
                - action: 动作 ('buy'/'sell')
                - code: 股票代码
                - volume: 数量
                - price: 价格

        Returns:
            Tuple[是否通过, 拒绝原因]
        """
        self.stats['total_checks'] += 1

        # 1. 持仓限制检查
        passed, msg = self._check_position()
        if not passed:
            self._log_blocked("POSITION_LIMIT", msg)
            return False, msg

        # 2. 委托频率检查
        passed, msg = self._check_order()
        if not passed:
            self._log_blocked("ORDER_LIMIT", msg)
            return False, msg

        # 3. 单笔委托检查
        if signal:
            passed, msg = self._check_single_order(signal)
            if not passed:
                self._log_blocked("SINGLE_ORDER", msg)
                return False, msg

        # 4. 亏损/回撤检查
        passed, msg = self._check_loss()
        if not passed:
            self._log_blocked("LOSS_LIMIT", msg)
            return False, msg

        return True, ""

    def _check_position(self) -> Tuple[bool, str]:
        """检查持仓比例限制

        计算当前总持仓比例，与配置的限制进行比较。

        Returns:
            Tuple[是否通过, 拒绝原因]
        """
        if not self.trade_manager:
            return True, ""

        try:
            # 获取现金
            cash = 0
            if hasattr(self.trade_manager, 'assets'):
                assets = self.trade_manager.assets
                if isinstance(assets, dict):
                    cash = assets.get('cash', 0)
                elif hasattr(assets, 'cash'):
                    cash = assets.cash

            # 计算持仓市值
            position_value = 0.0
            if hasattr(self.trade_manager, 'positions'):
                positions = self.trade_manager.positions
                if isinstance(positions, dict):
                    for code, pos in positions.items():
                        if isinstance(pos, dict):
                            mv = pos.get('market_value', 0)
                            cp = pos.get('current_price', 0)
                            vol = pos.get('volume', 0)
                            position_value += mv or (cp * vol)
                        else:
                            # 对象属性访问
                            mv = getattr(pos, 'market_value', 0)
                            position_value += mv

            total_asset = cash + position_value

            if total_asset <= 0:
                return True, ""

            position_ratio = position_value / total_asset

            if position_ratio > self.position_limit:
                self.stats['position_violations'] += 1
                self._log_event(
                    RiskEventType.POSITION_LIMIT_EXCEEDED,
                    f"持仓比例 {position_ratio:.2%} 超过限制 {self.position_limit:.2%}"
                )
                return False, f"持仓比例 {position_ratio:.2%} 超过限制 {self.position_limit:.2%}"

            return True, ""

        except Exception as e:
            logger.error(f"持仓检查异常: {e}", exc_info=True)
            return True, ""  # 异常时放行，避免阻塞交易

    def _check_order(self) -> Tuple[bool, str]:
        """检查委托频率限制

        检查今日委托次数是否超过限制。

        Returns:
            Tuple[是否通过, 拒绝原因]
        """
        if self.order_count_today >= self.order_limit:
            self.stats['order_rate_violations'] += 1
            self._log_event(
                RiskEventType.ORDER_LIMIT_EXCEEDED,
                f"今日委托 {self.order_count_today} 次，达到限制 {self.order_limit}"
            )
            return False, f"今日委托次数已达上限 {self.order_limit}"
        return True, ""

    def _check_single_order(self, signal: Dict) -> Tuple[bool, str]:
        """检查单笔委托金额限制

        Args:
            signal: 交易信号字典

        Returns:
            Tuple[是否通过, 拒绝原因]
        """
        try:
            # 提取信号参数
            volume = signal.get('volume', 0)
            price = signal.get('price', 0)
            order_value = volume * price

            if order_value <= 0:
                return True, ""

            if self.trade_manager and hasattr(self.trade_manager, 'assets'):
                # 获取总资产
                assets = self.trade_manager.assets
                cash = 0
                position_value = 0.0

                if isinstance(assets, dict):
                    cash = assets.get('cash', 0)
                    if hasattr(self.trade_manager, 'positions'):
                        for pos in self.trade_manager.positions.values():
                            if isinstance(pos, dict):
                                mv = pos.get('market_value', 0)
                                position_value += mv or 0

                total_asset = cash + position_value

                if total_asset > 0:
                    order_ratio = order_value / total_asset

                    if order_ratio > self.single_order_limit:
                        self.stats['single_order_violations'] += 1
                        self._log_event(
                            RiskEventType.SINGLE_ORDER_LIMIT,
                            f"单笔委托 {order_value:.2f} 占比 {order_ratio:.2%} "
                            f"超过限制 {self.single_order_limit:.2%}"
                        )
                        return False, f"单笔委托金额 {order_value:.2f} 超过资产比例限制"

            return True, ""

        except Exception as e:
            logger.error(f"单笔委托检查异常: {e}", exc_info=True)
            return True, ""

    def _check_loss(self) -> Tuple[bool, str]:
        """检查亏损和回撤限制

        检查累计亏损和最大回撤是否超过限制。

        Returns:
            Tuple[是否通过, 拒绝原因]
        """
        if not self.trade_manager:
            return True, ""

        try:
            # 计算当前权益
            cash = 0
            position_value = 0.0

            if hasattr(self.trade_manager, 'assets'):
                assets = self.trade_manager.assets
                if isinstance(assets, dict):
                    cash = assets.get('cash', 0)

            if hasattr(self.trade_manager, 'positions'):
                positions = self.trade_manager.positions
                if isinstance(positions, dict):
                    for pos in positions.values():
                        if isinstance(pos, dict):
                            mv = pos.get('market_value', 0)
                            position_value += mv or 0

            current_equity = cash + position_value

            # 更新峰值权益
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity

            # 回撤检查
            if self.peak_equity > 0:
                drawdown = (self.peak_equity - current_equity) / self.peak_equity

                if drawdown > self.drawdown_limit:
                    self.stats['drawdown_violations'] += 1
                    self._log_event(
                        RiskEventType.DRAWDOWN_LIMIT_EXCEEDED,
                        f"当前回撤 {drawdown:.2%} 超过限制 {self.drawdown_limit:.2%}"
                    )
                    return False, f"最大回撤 {drawdown:.2%} 超过限制 {self.drawdown_limit:.2%}"

            # 累计亏损检查
            init_capital = getattr(self.config, 'init_capital', 1000000)
            if init_capital > 0:
                loss_ratio = (init_capital - current_equity) / init_capital

                if loss_ratio >= self.loss_limit:
                    self.stats['loss_violations'] += 1
                    self._log_event(
                        RiskEventType.LOSS_LIMIT_TRIGGERED,
                        f"累计亏损 {loss_ratio:.2%} 达到止损线 {self.loss_limit:.2%}"
                    )
                    return False, f"累计亏损 {abs(loss_ratio):.2%} 达到止损线 {self.loss_limit:.2%}"

            # 今日亏损检查
            if self.daily_pnl < 0:
                init_equity = self.peak_equity if self.peak_equity > 0 else init_capital
                daily_loss_ratio = abs(self.daily_pnl) / init_equity if init_equity > 0 else 0

                if daily_loss_ratio >= self.daily_loss_limit:
                    self.stats['daily_loss_violations'] += 1
                    self._log_event(
                        RiskEventType.DAILY_LOSS_LIMIT,
                        f"今日亏损 {daily_loss_ratio:.2%} 超过限制 {self.daily_loss_limit:.2%}"
                    )
                    return False, f"今日亏损超限"

            return True, ""

        except Exception as e:
            logger.error(f"亏损检查异常: {e}", exc_info=True)
            return True, ""

    def increment_order_count(self, count: int = 1):
        """增加委托计数

        Args:
            count: 增加次数，默认为1
        """
        with self._lock:
            self.order_count_today += count
            self.stats['blocked_orders'] += 1

    def update_daily_pnl(self, pnl: float):
        """更新今日盈亏

        Args:
            pnl: 本次交易的盈亏
        """
        with self._lock:
            self.daily_pnl += pnl

    def reset_daily_counters(self):
        """重置日计数器

        在每日开盘前调用，重置所有日级别的计数器。
        """
        with self._lock:
            self.order_count_today = 0
            self.daily_pnl = 0.0

            # 更新峰值权益为当前权益
            if self.trade_manager and hasattr(self.trade_manager, 'assets'):
                assets = self.trade_manager.assets
                if isinstance(assets, dict):
                    cash = assets.get('cash', 0)
                    position_value = sum(
                        pos.get('market_value', 0)
                        for pos in getattr(self.trade_manager, 'positions', {}).values()
                    )
                    self.peak_equity = cash + position_value
                elif hasattr(assets, 'cash'):
                    self.peak_equity = assets.cash

            logger.info("风控日计数器已重置")

    def _log_event(self, event_type: str, message: str):
        """记录风控事件

        Args:
            event_type: 事件类型
            message: 事件消息
        """
        event = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': event_type,
            'message': message,
            'stats': self.stats.copy()
        }
        self.risk_events.append(event)

        # 保留最近100条事件
        if len(self.risk_events) > 100:
            self.risk_events = self.risk_events[-100:]

        logger.warning(f"[风控拦截] {event_type}: {message}")

    def _log_blocked(self, limit_type: str, message: str):
        """记录被拦截的交易

        Args:
            limit_type: 限制类型
            message: 拦截原因
        """
        self.stats['blocked_orders'] += 1
        logger.info(f"[风控] 交易被拦截 - {limit_type}: {message}")

    def get_risk_report(self) -> Dict:
        """获取风控报告

        Returns:
            Dict: 包含风控统计和事件日志的报告
        """
        with self._lock:
            return {
                'timestamp': datetime.datetime.now().isoformat(),
                'stats': self.stats.copy(),
                'runtime': {
                    'order_count_today': self.order_count_today,
                    'daily_pnl': self.daily_pnl,
                    'peak_equity': self.peak_equity
                },
                'config': {
                    'position_limit': self.position_limit,
                    'order_limit': self.order_limit,
                    'loss_limit': self.loss_limit,
                    'drawdown_limit': self.drawdown_limit,
                    'single_order_limit': self.single_order_limit,
                    'daily_loss_limit': self.daily_loss_limit
                },
                'recent_events': self.risk_events[-50:]  # 最近50条
            }

    def get_blocked_count(self) -> int:
        """获取被拦截的交易数量

        Returns:
            int: 被拦截的交易总数
        """
        return self.stats['blocked_orders']

    def get_violations_summary(self) -> Dict:
        """获取违规统计摘要

        Returns:
            Dict: 各类型违规次数统计
        """
        return {
            'position_violations': self.stats['position_violations'],
            'order_rate_violations': self.stats['order_rate_violations'],
            'loss_violations': self.stats['loss_violations'],
            'drawdown_violations': self.stats['drawdown_violations'],
            'single_order_violations': self.stats['single_order_violations'],
            'daily_loss_violations': self.stats['daily_loss_violations'],
            'total_blocked': self.stats['blocked_orders']
        }
