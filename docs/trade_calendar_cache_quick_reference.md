# 交易日历LRU缓存 - 快速参考指南

## 一分钟上手

### 基本使用（无需修改现有代码）

```python
from khQTTools import is_trade_day, get_trade_days_count

# 自动使用缓存，无需任何改动
if is_trade_day("2024-01-15"):
    print("是交易日")

count = get_trade_days_count("2024-01-01", "2024-01-31")
```

### 查看缓存统计

```python
from khQTTools import get_trade_calendar_cache_info

info = get_trade_calendar_cache_info()
print(f"命中次数: {info['is_trade_day_hits']}")
print(f"未命中次数: {info['is_trade_day_misses']}")
print(f"缓存大小: {info['is_trade_day_size']}")
```

### 清理缓存（假期调整后）

```python
from khQTTools import clear_trade_calendar_cache

clear_trade_calendar_cache()  # 清空所有缓存
```

## 性能提升

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 单次查询 | ~1ms | ~0.1ms | 10x |
| 回测1年 | ~250ms | ~2.5ms | 100x |
| 重复查询 | ~1ms | ~0.01ms | 100x |

## 缓存配置

```python
from constants import TradeCalendar

# 缓存大小配置
TradeCalendar.CACHE_IS_TRADE_DAY_MAXSIZE  # 4096 (单日缓存)
TradeCalendar.CACHE_GET_TRADE_DAYS_COUNT_MAXSIZE  # 512 (期间缓存)

# 性能目标
TradeCalendar.CACHE_TARGET_HIT_RATE  # 0.8 (80%命中率)
TradeCalendar.CACHE_TARGET_RESPONSE_TIME_MS  # 1.0ms (响应时间)
```

## 注意事项

### 需要清理缓存的情况

1. **假期调整**: 国务院发布新的假期安排
2. **临时休市**: 交易所发布临时休市通知
3. **系统更新**: 更新holidays库版本

### 多线程使用

```python
# lru_cache在Python 3.7+中是线程安全的
# 可以在多线程环境中直接使用，无需额外处理
```

## 常见问题

**Q: 会影响现有代码吗？**
A: 不会。API完全保持不变，内部自动优化。

**Q: 内存占用大吗？**
A: 很小，总内存占用 < 1MB。

**Q: 如何查看缓存效果？**
A: 使用`get_trade_calendar_cache_info()`查看统计信息。

**Q: 缓存会过期吗？**
A: 交易日历相对固定，一般不需要手动清理。

## 完整示例

```python
from khQTTools import (
    is_trade_day,
    get_trade_days_count,
    get_trade_calendar_cache_info,
    clear_trade_calendar_cache
)

# 1. 基本使用
print(is_trade_day("2024-01-15"))  # True

# 2. 批量查询（自动缓存）
dates = ["2024-01-15", "2024-01-16", "2024-01-17"]
results = [is_trade_day(d) for d in dates]

# 3. 计算交易日数量
count = get_trade_days_count("2024-01-01", "2024-01-31")
print(f"1月交易日: {count}天")

# 4. 查看缓存效果
info = get_trade_calendar_cache_info()
hit_rate = info['is_trade_day_hits'] / (
    info['is_trade_day_hits'] + info['is_trade_day_misses']
)
print(f"缓存命中率: {hit_rate * 100:.1f}%")

# 5. 清理缓存（可选）
# clear_trade_calendar_cache()
```

## 相关文档

- **详细实施报告**: `TRADE_CALENDAR_CACHE_IMPLEMENTATION.md`
- **性能基准文档**: `docs/trade_calendar_cache_benchmark.md`
- **测试文件**: `tests/test_trade_calendar_cache.py`

## 技术支持

如有问题，请查看：
1. 实施报告中的注意事项
2. 性能基准文档中的详细说明
3. 测试文件中的使用示例

---

**版本**: 1.0
**更新日期**: 2026-02-09
