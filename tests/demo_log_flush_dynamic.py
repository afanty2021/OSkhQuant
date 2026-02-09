"""
日志Flush动态调整机制演示脚本

演示动态调整机制如何根据日志缓冲区大小自动调整刷新间隔
"""

import time
from unittest.mock import Mock


class LogFlushDemo:
    """日志Flush动态调整演示"""

    def __init__(self):
        # 初始化参数（与实际GUI相同）
        self._flush_intervals = {
            'high_load': 1000,    # 高负载: 1秒
            'medium_load': 2000,  # 中负载: 2秒
            'low_load': 5000      # 低负载: 5秒
        }
        self._load_thresholds = {
            'high': 10000,  # 高负载阈值：10000条日志
            'medium': 1000  # 中负载阈值：1000条日志
        }
        self._flush_interval_stable_count = 0
        self._flush_stable_threshold = 3  # 需要连续3次检测到相同负载级别才切换间隔
        self._current_load_level = 'low'  # 当前负载级别：low, medium, high

        # 模拟日志缓冲区
        self.log_entries = []
        self.delayed_logs = []

        # 模拟定时器
        self.current_interval = 5000
        self.interval_changes = []  # 记录间隔变化历史

    def get_log_buffer_size(self):
        """获取当前日志缓冲区总大小"""
        size = len(self.log_entries) + len(self.delayed_logs)
        return size

    def get_log_load_level(self, buffer_size):
        """根据日志缓冲区大小确定负载级别"""
        if buffer_size > self._load_thresholds['high']:
            return 'high'
        elif buffer_size > self._load_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def adjust_flush_interval(self):
        """根据日志量动态调整刷新间隔（带防抖机制）"""
        buffer_size = self.get_log_buffer_size()
        current_level = self.get_log_load_level(buffer_size)

        # 防抖机制：只有连续检测到相同负载级别才切换间隔
        if current_level != self._current_load_level:
            self._flush_interval_stable_count += 1
            if self._flush_interval_stable_count >= self._flush_stable_threshold:
                # 确认负载级别变化，切换间隔
                new_interval = self._flush_intervals[f'{current_level}_load']
                if new_interval != self.current_interval:
                    self.current_interval = new_interval
                    change_record = {
                        'from': self._current_load_level,
                        'to': current_level,
                        'old_interval': self.current_interval,
                        'new_interval': new_interval,
                        'buffer_size': buffer_size
                    }
                    self.interval_changes.append(change_record)
                    print(f"[动态调整] 刷新间隔切换: {self._current_load_level} -> {current_level} "
                          f"({change_record['old_interval']}ms -> {new_interval}ms, "
                          f"缓冲区: {buffer_size}条)")
                self._current_load_level = current_level
                self._flush_interval_stable_count = 0
        else:
            # 负载级别稳定，重置计数器
            self._flush_interval_stable_count = 0

        return current_level, buffer_size

    def simulate_flush_cycle(self, cycle_num):
        """模拟一个Flush周期"""
        level, size = self.adjust_flush_interval()
        print(f"周期 #{cycle_num}: 负载级别={level}, 缓冲区={size}条, "
              f"刷新间隔={self.current_interval}ms")

    def demo_scenario_1_stable_low_load(self):
        """演示场景1：稳定的低负载"""
        print("\n" + "="*60)
        print("场景1：稳定的低负载（日志量 < 1000）")
        print("="*60)

        self.log_entries = list(range(500))
        for i in range(1, 6):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        print(f"\n结果：保持 {self.current_interval}ms 刷新间隔（低负载）")

    def demo_scenario_2_load_increase(self):
        """演示场景2：负载逐渐增加"""
        print("\n" + "="*60)
        print("场景2：负载逐渐增加（低 -> 中 -> 高）")
        print("="*60)

        # 重置状态
        self.log_entries = []
        self.delayed_logs = []
        self._current_load_level = 'low'
        self._flush_interval_stable_count = 0
        self.current_interval = 5000

        # 阶段1：低负载
        self.log_entries = list(range(500))
        for i in range(1, 4):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        # 阶段2：增加到中负载（需要连续3次检测）
        self.log_entries = list(range(2000))
        print(f"\n[事件] 日志量增加到 {len(self.log_entries)} 条（中负载）")
        for i in range(4, 10):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        # 阶段3：增加到高负载
        self.log_entries = list(range(12000))
        print(f"\n[事件] 日志量增加到 {len(self.log_entries)} 条（高负载）")
        for i in range(10, 16):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        print(f"\n最终结果：{self.current_interval}ms 刷新间隔（高负载）")
        print(f"间隔变化次数：{len(self.interval_changes)}")

    def demo_scenario_3_load_fluctuation(self):
        """演示场景3：负载波动（防抖机制）"""
        print("\n" + "="*60)
        print("场景3：负载波动（测试防抖机制）")
        print("="*60)

        # 重置状态
        self.log_entries = []
        self.delayed_logs = []
        self._current_load_level = 'low'
        self._flush_interval_stable_count = 0
        self.current_interval = 5000
        self.interval_changes = []

        # 周期1-3：低负载
        self.log_entries = list(range(500))
        for i in range(1, 4):
            self.simulate_flush_cycle(i)

        # 周期4：突然增加到中负载
        self.log_entries = list(range(2000))
        print(f"\n[事件] 日志量突然增加到 {len(self.log_entries)} 条")
        self.simulate_flush_cycle(4)
        print(f"稳定计数：{self._flush_interval_stable_count}/3")

        # 周期5：又回到低负载（触发防抖）
        self.log_entries = list(range(500))
        print(f"\n[事件] 日志量回落到 {len(self.log_entries)} 条")
        self.simulate_flush_cycle(5)
        print(f"稳定计数：{self._flush_interval_stable_count}/3 (重置)")
        print(f"说明：负载波动导致计数器重置，避免频繁切换")

        # 周期6-10：保持中负载
        self.log_entries = list(range(2000))
        for i in range(6, 11):
            self.simulate_flush_cycle(i)
            if i <= 8:
                print(f"稳定计数：{self._flush_interval_stable_count}/3")

        print(f"\n最终结果：{self.current_interval}ms 刷新间隔")
        print(f"间隔变化次数：{len(self.interval_changes)}")

    def demo_scenario_4_gradual_decrease(self):
        """演示场景4：负载逐渐降低"""
        print("\n" + "="*60)
        print("场景4：负载逐渐降低（高 -> 中 -> 低）")
        print("="*60)

        # 重置状态
        self.log_entries = []
        self.delayed_logs = []
        self._current_load_level = 'high'
        self._flush_interval_stable_count = 0
        self.current_interval = 1000
        self.interval_changes = []

        # 阶段1：高负载
        self.log_entries = list(range(12000))
        for i in range(1, 4):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        # 阶段2：降低到中负载
        self.log_entries = list(range(3000))
        print(f"\n[事件] 日志量降低到 {len(self.log_entries)} 条（中负载）")
        for i in range(4, 10):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        # 阶段3：降低到低负载
        self.log_entries = list(range(500))
        print(f"\n[事件] 日志量降低到 {len(self.log_entries)} 条（低负载）")
        for i in range(10, 16):
            self.simulate_flush_cycle(i)
            time.sleep(0.1)

        print(f"\n最终结果：{self.current_interval}ms 刷新间隔（低负载）")
        print(f"间隔变化次数：{len(self.interval_changes)}")

    def print_summary(self):
        """打印演示总结"""
        print("\n" + "="*60)
        print("演示总结")
        print("="*60)
        print(f"\n负载阈值配置：")
        print(f"  - 高负载: > {self._load_thresholds['high']} 条日志")
        print(f"  - 中负载: > {self._load_thresholds['medium']} 条日志")
        print(f"  - 低负载: <= {self._load_thresholds['medium']} 条日志")

        print(f"\n刷新间隔配置：")
        print(f"  - 高负载: {self._flush_intervals['high_load']} ms (1秒)")
        print(f"  - 中负载: {self._flush_intervals['medium_load']} ms (2秒)")
        print(f"  - 低负载: {self._flush_intervals['low_load']} ms (5秒)")

        print(f"\n防抖机制：")
        print(f"  - 稳定阈值: {self._flush_stable_threshold} 次")
        print(f"  - 说明: 需要连续{self._flush_stable_threshold}次检测到相同负载级别才切换间隔")

        print(f"\n性能优势：")
        print(f"  - 高负载时更频繁刷新，避免内存积压")
        print(f"  - 低负载时降低刷新频率，减少系统开销")
        print(f"  - 防抖机制避免频繁切换，保持系统稳定")
        print("="*60 + "\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("日志Flush动态调整机制演示")
    print("="*60)

    demo = LogFlushDemo()

    # 运行各种演示场景
    demo.demo_scenario_1_stable_low_load()
    demo.demo_scenario_2_load_increase()
    demo.demo_scenario_3_load_fluctuation()
    demo.demo_scenario_4_gradual_decrease()

    # 打印总结
    demo.print_summary()


if __name__ == '__main__':
    main()
