# coding: utf-8
"""
信号辅助工具类

提供PyQt5信号测试的辅助方法。
"""

from PyQt5.QtCore import QObject, pyqtSignal, QSignalSpy
from typing import Any, Callable, List
import time


class SignalHelpers:
    """信号测试辅助类"""

    @staticmethod
    def wait_signal(qtbot, signal, timeout: int = 1000, check_params: bool = False):
        """
        等待信号发射

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要等待的信号
            timeout: 超时时间（毫秒）
            check_params: 是否检查信号参数

        Returns:
            是否成功接收到信号
        """
        try:
            qtbot.wait_signal(signal, timeout=timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def wait_signal_count(qtbot, signal, count: int, timeout: int = 1000):
        """
        等待信号发射指定次数

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要等待的信号
            count: 期望的发射次数
            timeout: 超时时间（毫秒）

        Returns:
            是否成功接收到指定次数的信号
        """
        try:
            with qtbot.wait_signal(signal, timeout=timeout) as blocker:
                pass
            return blocker.signal_count == count
        except Exception:
            return False

    @staticmethod
    def wait_signals(qtbot, signals: List, timeout: int = 1000):
        """
        等待多个信号发射

        Args:
            qtbot: pytest-qt的qtbot fixture
            signals: 要等待的信号列表
            timeout: 超时时间（毫秒）

        Returns:
            是否所有信号都成功接收
        """
        try:
            for signal in signals:
                qtbot.wait_signal(signal, timeout=timeout)
            return True
        except Exception:
            return False

    @staticmethod
    def assert_signal_emitted(qtbot, signal, timeout: int = 1000):
        """
        断言信号被发射

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要检查的信号
            timeout: 超时时间（毫秒）

        Raises:
            AssertionError: 如果信号未发射
        """
        assert SignalHelpers.wait_signal(qtbot, signal, timeout), "信号未发射"

    @staticmethod
    def assert_signal_not_emitted(qtbot, signal, wait_time: int = 500):
        """
        断言信号未被发射

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要检查的信号
            wait_time: 等待时间（毫秒）

        Raises:
            AssertionError: 如果信号被发射
        """
        qtbot.wait(wait_time)
        # 使用信号spy检查
        spy = QSignalSpy(signal)
        qtbot.wait(wait_time)
        assert len(spy) == 0, f"信号不应该被发射，但被发射了 {len(spy)} 次"

    @staticmethod
    def get_signal_args(qtbot, signal, timeout: int = 1000) -> List[Any]:
        """
        获取信号参数

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要获取参数的信号
            timeout: 超时时间（毫秒）

        Returns:
            信号参数列表
        """
        spy = QSignalSpy(signal)
        qtbot.wait_signal(signal, timeout=timeout)
        if len(spy) > 0:
            return list(spy[0])
        return []

    @staticmethod
    def count_signal_emissions(qtbot, signal, wait_time: int = 1000) -> int:
        """
        统计信号发射次数

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要统计的信号
            wait_time: 等待时间（毫秒）

        Returns:
            信号发射次数
        """
        spy = QSignalSpy(signal)
        qtbot.wait(wait_time)
        return len(spy)

    @staticmethod
    def connect_and_wait(qtbot, signal, slot: Callable, timeout: int = 1000):
        """
        连接信号并等待发射

        Args:
            qtbot: pytest-qt的qtbot fixture
            signal: 要连接的信号
            slot: 槽函数
            timeout: 超时时间（毫秒）

        Returns:
            是否成功接收到信号
        """
        signal.connect(slot)
        return SignalHelpers.wait_signal(qtbot, signal, timeout)

    @staticmethod
    def disconnect_after(signal, slot: Callable):
        """
        在槽函数执行后断开信号连接

        Args:
            signal: 要断开的信号
            slot: 槽函数
        """
        def wrapper(*args, **kwargs):
            result = slot(*args, **kwargs)
            signal.disconnect(wrapper)
            return result

        signal.connect(wrapper)

    @staticmethod
    def create_signal_capture():
        """
        创建信号捕获器

        Returns:
            包含捕获数据的可调用对象和获取方法的元组
        """
        captured = []

        def capture(*args, **kwargs):
            captured.append({'args': args, 'kwargs': kwargs})

        def get_captured():
            return captured

        def get_count():
            return len(captured)

        def get_last():
            return captured[-1] if captured else None

        def clear():
            captured.clear()

        return capture, {
            'get': get_captured,
            'count': get_count,
            'last': get_last,
            'clear': clear,
        }

    @staticmethod
    def wait_for_condition(qtbot, condition: Callable, timeout: int = 1000, message: str = "条件未满足"):
        """
        等待条件满足

        Args:
            qtbot: pytest-qt的qtbot fixture
            condition: 条件函数
            timeout: 超时时间（毫秒）
            message: 超时时的错误消息

        Raises:
            AssertionError: 如果条件未满足
        """
        qtbot.wait_until(condition, timeout=timeout)
