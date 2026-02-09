# coding: utf-8
from logging_config import get_module_logger
"""
提醒管理器模块
提供声音提醒和微信推送的统一管理

@author: OsKhQuant
@version: 1.0
"""

# 日志系统
logger = get_module_logger(__name__)

# ===== 标准库导入 =====
import os
import json
import time
import threading
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# ===== 第三方库导入 =====
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# =============================================================================
# 提醒类型常量
# =============================================================================

class AlertType:
    """提醒类型常量"""
    SOUND = "sound"
    WECHAT = "wechat"


class AlertDirection:
    """买卖方向常量"""
    BUY = "buy"
    SELL = "sell"


# =============================================================================
# 声音提醒器
# =============================================================================

class SoundAlert:
    """
    声音提醒器

    使用Windows系统winsound库实现蜂鸣声提醒
    """

    def __init__(self, sound_file: Optional[str] = None):
        """
        初始化声音提醒器

        Args:
            sound_file: 自定义声音文件路径（可选）
        """
        self.logger = logging.getLogger("khAlertManager")
        self.sound_file = sound_file
        self.enabled = True

        # 频率设置（Hz）
        self.buy_freq = 800      # 买入提示音频率
        self.sell_freq = 600     # 卖出提示音频率
        self.alert_duration = 500  # 声音持续时间（毫秒）

        if not HAS_WINSOUND:
            self.logger.warning("winsound库不可用，声音提醒功能将受限")
        elif sound_file and not os.path.exists(sound_file):
            self.logger.warning(f"声音文件不存在: {sound_file}，将使用系统蜂鸣声")

        # 保留原始sound_file值（即使文件不存在也保留路径）
        self.sound_file = sound_file

    def play(self, direction: str, stock_code: str = "", price: float = 0.0):
        """
        播放提示音

        Args:
            direction: 买卖方向（'buy' 或 'sell'）
            stock_code: 股票代码
            price: 触发价格
        """
        if not self.enabled:
            return

        if not HAS_WINSOUND:
            self.logger.warning("winsound库不可用，无法播放声音")
            return

        try:
            # 根据买卖方向选择不同频率
            if direction.lower() == AlertDirection.BUY:
                freq = self.buy_freq
                message = f"【买入提醒】{stock_code} @ {price:.2f}"
            else:
                freq = self.sell_freq
                message = f"【卖出提醒】{stock_code} @ {price:.2f}"

            # 播放蜂鸣声
            winsound.Beep(freq, self.alert_duration)
            self.logger.info(message)

        except Exception as e:
            self.logger.error(f"播放声音失败: {e}")

    def play_alert(self, alert_type: str = "general"):
        """
        播放通用警报声

        Args:
            alert_type: 警报类型（'general'、'warning'、'error'）
        """
        if not self.enabled or not HAS_WINSOUND:
            return

        try:
            if alert_type == "warning":
                # 警告：两短一长
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(800, 200)
                time.sleep(0.1)
                winsound.Beep(1000, 400)
            elif alert_type == "error":
                # 错误：低频持续
                winsound.Beep(400, 800)
            else:
                # 一般提醒：单声
                winsound.Beep(1000, 300)

        except Exception as e:
            self.logger.error(f"播放警报声失败: {e}")


# =============================================================================
# 微信推送器
# =============================================================================

class WeChatAlert:
    """
    微信推送器

    使用Server酱（sct.ftqq.com）API实现微信推送
    """

    def __init__(self, send_key: Optional[str] = None):
        """
        初始化微信推送器

        Args:
            send_key: Server酱的SendKey
        """
        self.logger = logging.getLogger("khAlertManager")
        self.send_key = send_key
        self.enabled = send_key is not None and send_key.strip() != ""

        if not HAS_REQUESTS:
            self.logger.warning("requests库不可用，微信推送功能将受限")
            self.enabled = False

        if self.enabled:
            self.base_url = f"https://sct.ftqq.com/{send_key}.send"
        else:
            self.base_url = None

    def push(self, title: str, content: str, stock_code: str = "",
             direction: str = "", price: float = 0.0, reason: str = ""):
        """
        发送微信推送

        Args:
            title: 推送标题
            content: 推送内容
            stock_code: 股票代码
            direction: 买卖方向
            price: 触发价格
            reason: 触发原因
        """
        if not self.enabled:
            self.logger.debug("微信推送未启用")
            return

        if not HAS_REQUESTS:
            self.logger.warning("requests库不可用，无法发送微信推送")
            return

        # 构建详细消息
        details = []
        if stock_code:
            details.append(f"股票: {stock_code}")
        if direction:
            details.append(f"操作: {'买入' if direction.lower() == 'buy' else '卖出'}")
        if price > 0:
            details.append(f"价格: {price:.2f}")
        if reason:
            details.append(f"原因: {reason}")

        # 完整内容
        full_content = f"{content}\n\n" + "\n".join(details) if details else content

        try:
            # 异步发送请求
            def _send_request():
                try:
                    data = {
                        "title": title,
                        "desp": full_content
                    }
                    response = requests.post(self.base_url, data=data, timeout=10)
                    result = response.json()

                    if result.get("code") == 0 or result.get("success"):
                        self.logger.info(f"微信推送成功: {title}")
                    else:
                        self.logger.error(f"微信推送失败: {result.get('message', result)}")

                except requests.exceptions.Timeout:
                    self.logger.error("微信推送请求超时")
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"微信推送请求失败: {e}")

            # 在新线程中发送，避免阻塞
            threading.Thread(target=_send_request, daemon=True).start()

        except Exception as e:
            self.logger.error(f"发送微信推送异常: {e}")

    def push_signal(self, signal: Dict):
        """
        根据交易信号推送微信消息

        Args:
            signal: 交易信号字典，包含 stock_code, direction, price, reason 等字段
        """
        if not self.enabled:
            return

        stock_code = signal.get("stock_code", "")
        direction = signal.get("direction", "")
        price = signal.get("price", 0.0)
        reason = signal.get("reason", "")

        # 方向文字
        direction_text = "买入" if direction.lower() == "buy" else "卖出"

        # 构建标题
        title = f"【{direction_text}信号提醒】{stock_code}"

        # 构建内容
        content = f"触发{direction_text}信号，请及时处理"

        self.push(title, content, stock_code, direction, price, reason)


# =============================================================================
# 提醒管理器
# =============================================================================

class KhAlertManager:
    """
    统一提醒管理器

    协调声音提醒和微信推送，支持信号去重
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化提醒管理器

        Args:
            config: 配置字典，包含以下字段:
                - sound_enabled: 是否启用声音提醒（默认True）
                - wechat_enabled: 是否启用微信推送（默认False）
                - wechat_key: Server酱SendKey
                - dedup_interval: 去重时间间隔（秒，默认60）
                - sound_file: 自定义声音文件路径
        """
        self.logger = logging.getLogger("khAlertManager")

        # 默认配置
        self.config = config or {}
        self.sound_enabled = self.config.get("sound_enabled", True)
        self.wechat_enabled = self.config.get("wechat_enabled", False)
        self.dedup_interval = self.config.get("dedup_interval", 60)

        # 初始化子管理器
        self.sound_alert = SoundAlert(self.config.get("sound_file"))
        self.sound_alert.enabled = self.sound_enabled

        self.wechat_alert = WeChatAlert(self.config.get("wechat_key"))
        self.wechat_alert.enabled = self.wechat_enabled

        # 去重缓存: {stock_code: {direction: last_time}}
        self.dedup_cache: Dict[str, Dict[str, float]] = {}

        # 信号统计
        self.signal_count = 0
        self.sound_count = 0
        self.wechat_count = 0

        self.logger.info("提醒管理器初始化完成")

    def _check_dedup(self, stock_code: str, direction: str) -> bool:
        """
        检查信号是否需要去重

        Args:
            stock_code: 股票代码
            direction: 买卖方向

        Returns:
            True表示信号应被抑制（重复），False表示正常处理
        """
        current_time = time.time()

        if stock_code not in self.dedup_cache:
            self.dedup_cache[stock_code] = {}
            return False

        last_time = self.dedup_cache[stock_code].get(direction, 0)

        if current_time - last_time < self.dedup_interval:
            self.logger.debug(f"信号去重: {stock_code} {direction} 在{self.dedup_interval}秒内重复")
            return True

        return False

    def _update_dedup(self, stock_code: str, direction: str):
        """更新去重缓存时间"""
        current_time = time.time()
        if stock_code not in self.dedup_cache:
            self.dedup_cache[stock_code] = {}
        self.dedup_cache[stock_code][direction] = current_time

    def clear_dedup_cache(self, stock_code: Optional[str] = None):
        """
        清除去重缓存

        Args:
            stock_code: 指定股票代码，为None则清除所有
        """
        if stock_code:
            if stock_code in self.dedup_cache:
                del self.dedup_cache[stock_code]
        else:
            self.dedup_cache.clear()

    def on_signal(self, signal: Dict) -> bool:
        """
        处理交易信号并触发提醒

        Args:
            signal: 交易信号字典，包含:
                - stock_code: 股票代码
                - direction: 买卖方向（'buy' 或 'sell'）
                - price: 触发价格
                - reason: 触发原因
                - skip_dedup: 是否跳过去重检查（可选）

        Returns:
            True表示信号已处理，False表示被去重
        """
        # 解析信号
        stock_code = signal.get("stock_code", "")
        direction = signal.get("direction", "")
        price = signal.get("price", 0.0)
        reason = signal.get("reason", "")

        # 去重检查
        if not signal.get("skip_dedup", False):
            if self._check_dedup(stock_code, direction):
                self.logger.info(f"信号被去重: {stock_code} {direction}")
                return False

        # 更新去重时间
        self._update_dedup(stock_code, direction)

        # 增加计数
        self.signal_count += 1

        # 触发声音提醒
        if self.sound_enabled and self.sound_alert:
            self.sound_alert.play(direction, stock_code, price)
            self.sound_count += 1

        # 触发微信推送
        if self.wechat_enabled and self.wechat_alert:
            self.wechat_alert.push_signal(signal)
            self.wechat_count += 1

        self.logger.info(f"信号提醒已触发: {stock_code} {direction} @ {price}")

        return True

    def play_custom_alert(self, alert_type: str = "general"):
        """播放自定义警报声"""
        if self.sound_enabled and self.sound_alert:
            self.sound_alert.play_alert(alert_type)

    def update_config(self, config: Dict[str, Any]):
        """
        更新配置

        Args:
            config: 新的配置字典
        """
        old_sound = self.sound_enabled
        old_wechat = self.wechat_enabled

        self.config.update(config)
        self.sound_enabled = self.config.get("sound_enabled", True)
        self.wechat_enabled = self.config.get("wechat_enabled", False)
        self.dedup_interval = self.config.get("dedup_interval", 60)

        # 更新子管理器
        if self.sound_alert:
            self.sound_alert.enabled = self.sound_enabled

        if self.wechat_alert:
            wechat_key = self.config.get("wechat_key")
            self.wechat_alert.send_key = wechat_key
            self.wechat_alert.enabled = self.wechat_enabled and wechat_key

        # 记录配置变更
        if old_sound != self.sound_enabled:
            self.logger.info(f"声音提醒已{'启用' if self.sound_enabled else '禁用'}")
        if old_wechat != self.wechat_enabled:
            self.logger.info(f"微信推送已{'启用' if self.wechat_enabled else '禁用'}")

    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息

        Returns:
            包含计数信息的字典
        """
        return {
            "total_signals": self.signal_count,
            "sound_alerts": self.sound_count,
            "wechat_alerts": self.wechat_count
        }

    def reset_stats(self):
        """重置统计信息"""
        self.signal_count = 0
        self.sound_count = 0
        self.wechat_count = 0


# =============================================================================
# 便捷函数
# =============================================================================

def create_alert_manager(config: Optional[Dict] = None) -> KhAlertManager:
    """
    创建提醒管理器的便捷函数

    Args:
        config: 配置字典

    Returns:
        KhAlertManager实例
    """
    return KhAlertManager(config)


def test_alert_system():
    """测试提醒系统（仅用于调试）"""
    logger.info("=== 测试提醒管理器 ===")

    # 测试配置
    config = {
        "sound_enabled": True,
        "wechat_enabled": False,  # 设置为True并填入Key以测试微信
        "wechat_key": "",
        "dedup_interval": 5  # 短时间用于测试
    }

    # 创建管理器
    mgr = KhAlertManager(config)

    # 测试信号1 - 应该正常触发
    signal1 = {
        "stock_code": "000001.SZ",
        "direction": "buy",
        "price": 10.50,
        "reason": "测试买入信号"
    }
    result1 = mgr.on_signal(signal1)
    logger.info(f"信号1触发结果: {result1}")

    # 测试信号2 - 相同股票相同方向，应该被去重
    time.sleep(1)
    signal2 = {
        "stock_code": "000001.SZ",
        "direction": "buy",
        "price": 10.52,
        "reason": "测试买入信号2"
    }
    result2 = mgr.on_signal(signal2)
    logger.info(f"信号2触发结果（应为False）: {result2}")

    # 测试信号3 - 不同方向，应该正常触发
    signal3 = {
        "stock_code": "000001.SZ",
        "direction": "sell",
        "price": 10.55,
        "reason": "测试卖出信号"
    }
    result3 = mgr.on_signal(signal3)
    logger.info(f"信号3触发结果: {result3}")

    # 打印统计
    logger.info(f"\n统计信息: {mgr.get_stats()}")


if __name__ == "__main__":
    test_alert_system()
