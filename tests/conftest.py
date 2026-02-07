# coding: utf-8
"""
测试配置和共享Fixtures

提供测试所需的共享fixtures、配置和工具函数。
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import tempfile
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# 数据Fixtures
# ============================================================================

@pytest.fixture
def sample_stock_data():
    """提供示例股票数据"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    data = {
        'date': dates,
        'open': np.random.uniform(10, 20, 100),
        'high': np.random.uniform(15, 25, 100),
        'low': np.random.uniform(8, 15, 100),
        'close': np.random.uniform(10, 20, 100),
        'volume': np.random.randint(1000000, 10000000, 100),
        'amount': np.random.uniform(10000000, 100000000, 100),
    }

    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def sample_tick_data():
    """提供示例Tick数据"""
    return {
        '000001.SZ': {
            'lastPrice': 10.50,
            'askPrice1': 10.51,
            'bidPrice1': 10.50,
            'askVolume1': 1000,
            'bidVolume1': 2000,
            'volume': 5000000,
            'amount': 52500000,
            'time': '2024-01-01 09:30:00',
        }
    }


@pytest.fixture
def sample_context_data():
    """提供示例策略上下文数据"""
    return {
        '__current_time__': {
            'date': '2024-01-01',
            'time': '09:30:00',
            'timestamp': 1704067200,
        },
        '__stock_list__': ['000001.SZ', '000002.SZ', '510300.SH'],
        '__positions__': {
            '000001.SZ': {
                'volume': 1000,
                'avg_price': 10.50,
                'current_price': 10.55,
            }
        },
        '__account__': {
            'cash': 50000.0,
            'market_value': 10550.0,
            'total_asset': 60550.0,
        },
        '000001.SZ': {
            'open': 10.45,
            'high': 10.60,
            'low': 10.40,
            'close': 10.55,
            'volume': 100000,
        },
        '000002.SZ': {
            'open': 15.20,
            'high': 15.35,
            'low': 15.15,
            'close': 15.30,
            'volume': 80000,
        },
        '510300.SH': {
            'open': 3.850,
            'high': 3.870,
            'low': 3.840,
            'close': 3.865,
            'volume': 500000,
        },
    }


@pytest.fixture
def sample_price_series():
    """提供示例价格序列"""
    np.random.seed(42)
    return pd.Series(np.random.uniform(10, 20, 100))


@pytest.fixture
def sample_ohlc_data():
    """提供示例OHLC数据"""
    np.random.seed(42)
    n = 100

    close = np.random.uniform(10, 20, n)
    high = close * (1 + np.random.uniform(0, 0.02, n))
    low = close * (1 - np.random.uniform(0, 0.02, n))
    open_ = close * (1 + np.random.uniform(-0.01, 0.01, n))
    volume = np.random.randint(1000000, 10000000, n)

    return {
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
    }


# ============================================================================
# 配置Fixtures
# ============================================================================

@pytest.fixture
def mock_config():
    """提供模拟配置对象"""
    class MockConfig:
        def __init__(self):
            self.config_dict = {
                'backtest': {
                    'trade_cost': {
                        'min_commission': 5.0,
                        'commission_rate': 0.0003,
                        'stamp_tax_rate': 0.001,
                        'flow_fee': 0.1,
                        'slippage': {
                            'type': 'ratio',
                            'tick_size': 0.01,
                            'tick_count': 2,
                            'ratio': 0.001,
                        }
                    }
                },
                'risk': {
                    'position_limit': 0.95,
                    'order_limit': 100,
                    'loss_limit': 0.1,
                    'drawdown_limit': 0.15,
                    'single_order_limit': 0.3,
                    'daily_loss_limit': 0.05,
                    'init_capital': 1000000,
                }
            }

        def get(self, key, default=None):
            keys = key.split('.')
            value = self.config_dict
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            return value if value is not None else default

    return MockConfig()


@pytest.fixture
def temp_config_file():
    """提供临时配置文件"""
    config_data = {
        'backtest': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'init_capital': 1000000,
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # 清理
    if os.path.exists(temp_path):
        os.remove(temp_path)


# ============================================================================
# 股票池Fixtures
# ============================================================================

@pytest.fixture
def stock_pool_etf():
    """提供ETF股票池"""
    return ['510300.SH', '510500.SH', '159915.SZ', '159919.SZ']


@pytest.fixture
def stock_pool_mixed():
    """提供混合股票池"""
    return ['000001.SZ', '000002.SZ', '510300.SH', '159915.SZ']


@pytest.fixture
def stock_pool_stock():
    """提供纯股票池"""
    return ['000001.SZ', '000002.SZ', '600000.SH', '600036.SH']


# ============================================================================
# 交易Fixtures
# ============================================================================

@pytest.fixture
def sample_signals():
    """提供示例交易信号"""
    return [
        {
            'stock': '000001.SZ',
            'action': 'buy',
            'price': 10.50,
            'volume': 1000,
            'reason': 'RSI超卖',
        },
        {
            'stock': '000002.SZ',
            'action': 'sell',
            'price': 15.30,
            'volume': 500,
            'reason': '止盈',
        }
    ]


@pytest.fixture
def sample_positions():
    """提供示例持仓"""
    return {
        '000001.SZ': {
            'volume': 1000,
            'avg_price': 10.50,
            'current_price': 10.55,
            'market_value': 10550.0,
            'pnl': 50.0,
            'pnl_ratio': 0.00476,
        },
        '510300.SH': {
            'volume': 2000,
            'avg_price': 3.850,
            'current_price': 3.865,
            'market_value': 7730.0,
            'pnl': 30.0,
            'pnl_ratio': 0.00390,
        }
    }


# ============================================================================
# 技术指标Fixtures
# ============================================================================

@pytest.fixture
def macd_params():
    """提供MACD参数"""
    return {'SHORT': 12, 'LONG': 26, 'M': 9}


@pytest.fixture
def kdj_params():
    """提供KDJ参数"""
    return {'N': 9, 'M1': 3, 'M2': 3}


@pytest.fixture
def rsi_params():
    """提供RSI参数"""
    return {'N': 14}


@pytest.fixture
def boll_params():
    """提供布林带参数"""
    return {'N': 20, 'P': 2}


# ============================================================================
# 时间Fixtures
# ============================================================================

@pytest.fixture
def trade_dates():
    """提供交易日列表"""
    return pd.date_range('2024-01-01', '2024-12-31', freq='B')  # B = 工作日


@pytest.fixture
def current_trade_time():
    """提供当前交易时间"""
    return datetime(2024, 1, 1, 9, 30, 0)


# ============================================================================
# 工具函数Fixtures
# ============================================================================

@pytest.fixture
def make_trade_manager():
    """创建交易管理器的工厂函数"""
    from khTrade import KhTradeManager

    def _make(config=None):
        if config is None:
            config = mock_config()
        return KhTradeManager(config)

    return _make


@pytest.fixture
def make_risk_manager():
    """创建风险管理器的工厂函数"""
    from khRisk import KhRiskManager

    def _make(config=None, trade_manager=None):
        if config is None:
            config = mock_config()
        return KhRiskManager(config, trade_manager=trade_manager)

    return _make


# ============================================================================
# 跳过和标记
# ============================================================================

def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ============================================================================
# 测试钩子
# ============================================================================

@pytest.fixture(autouse=True)
def reset_global_state():
    """每个测试后重置全局状态"""
    yield
    # 清理全局缓存
    if hasattr(sys.modules.get('khQTTools', None), '_t0_etf_cache'):
        import khQTTools
        khQTTools._t0_etf_cache = None


# ============================================================================
# 断言辅助函数
# ============================================================================

@pytest.fixture
def assert_series_equal():
    """提供Series相等断言"""
    def _assert(s1, s2, **kwargs):
        pd.testing.assert_series_equal(s1, s2, **kwargs)
    return _assert


@pytest.fixture
def assert_frame_equal():
    """提供DataFrame相等断言"""
    def _assert(df1, df2, **kwargs):
        pd.testing.assert_frame_equal(df1, df2, **kwargs)
    return _assert


# ============================================================================
# Mock辅助函数
# ============================================================================

@pytest.fixture
def mock_xtdata():
    """Mock xtdata模块"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.get_market_data_ex.return_value = None
    mock.subscribe_quote.return_value = None
    return mock


@pytest.fixture
def mock_xttrader():
    """Mock xttrader模块"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.order_stock_async.return_value = None
    return mock
