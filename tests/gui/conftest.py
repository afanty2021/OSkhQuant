# coding: utf-8
"""
GUI测试配置和共享Fixtures

提供PyQt5 GUI测试所需的共享fixtures和配置。
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import tempfile

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# PyQt5导入 - 用于GUI测试
try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


# ============================================================================
# QApplication Fixture
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    """
    创建QApplication实例（会话级别）

    这是使用pytest-qt进行GUI测试的必需fixture。
    """
    if not PYQT5_AVAILABLE:
        pytest.skip("PyQt5未安装，跳过GUI测试")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # 清理
    app.quit()


# ============================================================================
# GUI测试基类Fixtures
# ============================================================================

@pytest.fixture
def qtbot(qapp, qtbot):
    """
    扩展qtbot fixture，添加额外的辅助方法

    使用pytest-qt提供的qtbot，并添加自定义辅助方法。
    """
    # 原始qtbot已经由pytest-qt提供
    original_add_widget = qtbot.addWidget

    def add_widget_with_tracking(widget):
        """添加widget并跟踪其生命周期"""
        original_add_widget(widget)
        # 可以添加额外的跟踪逻辑
        return widget

    qtbot.addWidget = add_widget_with_tracking

    yield qtbot


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_config_manager():
    """Mock配置管理器"""
    config = {
        'backtest': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'init_capital': 1000000,
            'trade_cost': {
                'min_commission': 5.0,
                'commission_rate': 0.0003,
                'stamp_tax_rate': 0.001,
            }
        },
        'data': {
            'data_dir': './data',
            'cache_dir': './cache',
        },
        'gui': {
            'theme': 'default',
            'log_level': 'INFO',
        }
    }

    mock = Mock()
    mock.get = lambda key, default=None: config.get(key, default)
    mock.set = Mock()
    mock.save = Mock()
    mock.config = config

    return mock


@pytest.fixture
def mock_xtdata():
    """Mock xtdata模块"""
    mock = MagicMock()

    # Mock数据获取函数
    mock.get_market_data_ex = Mock(return_value=None)
    mock.get_full_tick = Mock(return_value={})
    mock.download_history_data_ex = Mock(return_value=None)

    # Mock订阅函数
    mock.subscribe_quote = Mock(return_value=None)
    mock.unsubscribe_quote = Mock(return_value=None)

    # Mock交易相关
    mock.get_trading_dates = Mock(return_value=['20240101', '20240102'])
    mock.get_instrument_type = Mock(return_value=1)

    return mock


@pytest.fixture
def mock_frame():
    """Mock khFrame策略执行框架"""
    mock = Mock()
    mock.running = False
    mock.paused = False
    mock.current_strategy = None
    mock.account = {
        'cash': 100000.0,
        'market_value': 50000.0,
        'total_asset': 150000.0,
    }
    mock.positions = {}
    mock.orders = []

    # Mock方法
    mock.start_backtest = Mock()
    mock.stop_backtest = Mock()
    mock.pause_backtest = Mock()
    mock.load_strategy = Mock(return_value=True)
    mock.get_backtest_result = Mock(return_value={})

    return mock


@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / 'data'
        data_dir.mkdir()
        yield data_dir


@pytest.fixture
def sample_strategy_file(temp_data_dir):
    """创建示例策略文件"""
    strategy_content = '''# coding: utf-8
"""
示例测试策略
"""

from khQuantImport import *

def init(stock_list, context):
    """策略初始化"""
    pass

def khHandlebar(context):
    """主策略逻辑"""
    signals = []
    # 简单的买入逻辑
    stock_code = khGet(context, 'first_stock')
    if stock_code and not khHas(context, stock_code):
        price = khPrice(context, stock_code)
        signals = generate_signal(
            context, stock_code, price, 0.5, 'buy',
            '测试买入'
        )
    return signals

def khPreMarket(context):
    """盘前处理"""
    return []

def khPostMarket(context):
    """盘后处理"""
    return []
'''

    strategy_file = temp_data_dir / 'test_strategy.py'
    strategy_file.write_text(strategy_content, encoding='utf-8')
    return strategy_file


# ============================================================================
# 测试数据Fixtures
# ============================================================================

@pytest.fixture
def sample_stock_list():
    """示例股票池"""
    return ['000001.SZ', '000002.SZ', '600000.SH', '600036.SH']


@pytest.fixture
def sample_backtest_result():
    """示例回测结果"""
    return {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'init_capital': 1000000,
        'final_capital': 1150000,
        'total_return': 0.15,
        'annual_return': 0.15,
        'max_drawdown': -0.08,
        'sharpe_ratio': 1.5,
        'win_rate': 0.6,
        'total_trades': 100,
        'profit_trades': 60,
        'loss_trades': 40,
        'trades': [
            {
                'date': '2024-01-02',
                'stock': '000001.SZ',
                'action': 'buy',
                'price': 10.50,
                'volume': 1000,
                'amount': 10500.0,
            },
            {
                'date': '2024-01-05',
                'stock': '000001.SZ',
                'action': 'sell',
                'price': 11.00,
                'volume': 1000,
                'amount': 11000.0,
                'pnl': 500.0,
            }
        ],
        'daily_pnl': [
            {'date': '2024-01-01', 'pnl': 0.0, 'return': 0.0},
            {'date': '2024-01-02', 'pnl': 500.0, 'return': 0.0005},
        ],
        'equity_curve': [
            {'date': '2024-01-01', 'equity': 1000000},
            {'date': '2024-01-02', 'equity': 1000500},
        ],
    }


@pytest.fixture
def sample_data_files(temp_data_dir):
    """创建示例数据文件"""
    # 创建一些示例数据文件
    data_files = {}

    # 创建股票数据文件
    stock_file = temp_data_dir / '000001.SZ.csv'
    stock_file.write_text('''date,open,high,low,close,volume
2024-01-01,10.0,10.5,9.8,10.3,1000000
2024-01-02,10.3,10.8,10.1,10.6,1200000
''')
    data_files['stock'] = stock_file

    # 创建tick数据文件
    tick_file = temp_data_dir / 'tick_000001.SZ.csv'
    tick_file.write_text('''time,lastPrice,volume,amount
09:30:00,10.30,1000,10300
09:30:01,10.31,2000,20620
''')
    data_files['tick'] = tick_file

    return data_files


# ============================================================================
# 辅助函数Fixtures
# ============================================================================

@pytest.fixture
def wait_signal(qtbot):
    """
    等待信号的辅助函数

    使用示例:
        signal = widget.some_signal
        wait_signal(signal).connect(lambda: ...)
    """
    def _wait(signal, timeout=1000):
        return qtbot.wait_signal(signal, timeout)
    return _wait


@pytest.fixture
def wait_until(qtbot):
    """
    等待条件满足的辅助函数

    使用示例:
        wait_until(lambda: widget.isVisible(), timeout=1000)
    """
    def _wait(condition, timeout=1000):
        qtbot.wait_until(condition, timeout)
    return _wait


# ============================================================================
# QWidget查找辅助
# ============================================================================

@pytest.fixture
def find_widget():
    """
    查找QWidget的辅助函数

    按对象名称或类型查找子widget
    """
    def _find(parent, name=None, widget_type=None):
        """
        查找子widget

        Args:
            parent: 父widget
            name: 对象名称（可选）
            widget_type: widget类型（可选）
        """
        if name:
            widget = parent.findChild(QWidget, name)
            return widget
        elif widget_type:
            widgets = parent.findChildren(widget_type)
            return widgets[0] if widgets else None
        else:
            return None

    return _find


@pytest.fixture
def trigger_action():
    """
    触发QAction的辅助函数
    """
    def _trigger(widget, action_name):
        """
        触发指定名称的action

        Args:
            widget: 包含action的widget
            action_name: action的名称
        """
        for action in widget.findChildren(QWidget):
            if hasattr(action, 'text') and action.text() == action_name:
                action.trigger()
                return True
        return False

    return _trigger


# ============================================================================
# GUI测试标记
# ============================================================================

def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests"
    )
    config.addinivalue_line(
        "markers", "slow_gui: marks tests as slow GUI tests"
    )
    config.addinivalue_line(
        "markers", "integration_gui: marks tests as GUI integration tests"
    )


# ============================================================================
# 跳过条件
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """修改测试收集，添加跳过条件"""
    if not PYQT5_AVAILABLE:
        skip_gui = pytest.mark.skip(reason="PyQt5未安装")
        for item in items:
            if item.get_closest_marker("gui"):
                item.add_marker(skip_gui)
