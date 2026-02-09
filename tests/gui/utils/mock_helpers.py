# coding: utf-8
"""
Mock辅助工具类

提供GUI测试中常用的Mock对象创建方法。
"""

from unittest.mock import Mock, MagicMock, PropertyMock
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, List, Any, Optional
import tempfile
from pathlib import Path


class MockHelpers:
    """Mock测试辅助类"""

    @staticmethod
    def create_mock_config(config_dict: Optional[Dict] = None) -> Mock:
        """
        创建Mock配置对象

        Args:
            config_dict: 配置字典

        Returns:
            Mock配置对象
        """
        if config_dict is None:
            config_dict = {
                'backtest': {
                    'start_date': '2024-01-01',
                    'end_date': '2024-12-31',
                    'init_capital': 1000000,
                },
                'gui': {
                    'theme': 'default',
                    'log_level': 'INFO',
                }
            }

        mock = Mock()
        mock.config = config_dict
        mock.get = lambda key, default=None: config_dict.get(key, default)
        mock.set = Mock()
        mock.save = Mock()
        mock.load = Mock(return_value=config_dict)
        return mock

    @staticmethod
    def create_mock_account() -> Dict:
        """
        创建模拟账户数据

        Returns:
            账户数据字典
        """
        return {
            'cash': 100000.0,
            'market_value': 50000.0,
            'total_asset': 150000.0,
            'available_cash': 95000.0,
            'frozen_cash': 5000.0,
            'pnl': 5000.0,
            'pnl_ratio': 0.0333,
        }

    @staticmethod
    def create_mock_positions() -> Dict:
        """
        创建模拟持仓数据

        Returns:
            持仓数据字典
        """
        return {
            '000001.SZ': {
                'volume': 1000,
                'available_volume': 1000,
                'avg_price': 10.50,
                'current_price': 10.55,
                'market_value': 10550.0,
                'pnl': 50.0,
                'pnl_ratio': 0.00476,
                'cost': 10500.0,
            },
            '510300.SH': {
                'volume': 2000,
                'available_volume': 2000,
                'avg_price': 3.850,
                'current_price': 3.865,
                'market_value': 7730.0,
                'pnl': 30.0,
                'pnl_ratio': 0.00390,
                'cost': 7700.0,
            }
        }

    @staticmethod
    def create_mock_orders() -> List[Dict]:
        """
        创建模拟委托数据

        Returns:
            委托数据列表
        """
        return [
            {
                'order_id': '2024010200001',
                'stock': '000001.SZ',
                'action': 'buy',
                'price': 10.50,
                'volume': 1000,
                'amount': 10500.0,
                'status': 'filled',
                'filled_volume': 1000,
                'filled_amount': 10500.0,
                'time': '2024-01-02 09:30:00',
            },
            {
                'order_id': '2024010200002',
                'stock': '510300.SH',
                'action': 'sell',
                'price': 3.870,
                'volume': 1000,
                'amount': 3870.0,
                'status': 'pending',
                'filled_volume': 0,
                'filled_amount': 0.0,
                'time': '2024-01-02 09:31:00',
            }
        ]

    @staticmethod
    def create_mock_trades() -> List[Dict]:
        """
        创建模拟成交数据

        Returns:
            成交数据列表
        """
        return [
            {
                'trade_id': 'T2024010200001',
                'order_id': '2024010200001',
                'stock': '000001.SZ',
                'action': 'buy',
                'price': 10.50,
                'volume': 1000,
                'amount': 10500.0,
                'commission': 5.0,
                'time': '2024-01-02 09:30:15',
            },
            {
                'trade_id': 'T2024010200002',
                'order_id': '2024010200001',
                'stock': '510300.SH',
                'action': 'sell',
                'price': 3.865,
                'volume': 1000,
                'amount': 3865.0,
                'commission': 5.0,
                'time': '2024-01-02 09:32:20',
            }
        ]

    @staticmethod
    def create_mock_frame() -> Mock:
        """
        创建Mock策略执行框架

        Returns:
            Mock khFrame对象
        """
        mock = Mock()
        mock.running = False
        mock.paused = False
        mock.current_strategy = None
        mock.account = MockHelpers.create_mock_account()
        mock.positions = MockHelpers.create_mock_positions()
        mock.orders = MockHelpers.create_mock_orders()
        mock.trades = MockHelpers.create_mock_trades()

        # Mock方法
        mock.start_backtest = Mock()
        mock.stop_backtest = Mock()
        mock.pause_backtest = Mock()
        mock.resume_backtest = Mock()
        mock.load_strategy = Mock(return_value=True)
        mock.unload_strategy = Mock()
        mock.get_backtest_result = Mock(return_value={})
        mock.get_account = Mock(return_value=mock.account)
        mock.get_positions = Mock(return_value=mock.positions)
        mock.get_orders = Mock(return_value=mock.orders)
        mock.get_trades = Mock(return_value=mock.trades)

        return mock

    @staticmethod
    def create_mock_data_manager() -> Mock:
        """
        创建Mock数据管理器

        Returns:
            Mock数据管理器对象
        """
        mock = Mock()
        mock.download_stock_data = Mock(return_value=True)
        mock.get_local_stock_list = Mock(return_value=['000001.SZ', '000002.SZ'])
        mock.check_data完整性 = Mock(return_value=True)
        mock.get_stock_data = Mock(return_value=None)
        return mock

    @staticmethod
    def create_mock_strategy_file(content: Optional[str] = None) -> Path:
        """
        创建临时策略文件

        Args:
            content: 策略文件内容

        Returns:
            策略文件路径
        """
        if content is None:
            content = '''# coding: utf-8
from khQuantImport import *

def init(stock_list, context):
    pass

def khHandlebar(context):
    signals = []
    stock_code = khGet(context, 'first_stock')
    if stock_code:
        price = khPrice(context, stock_code)
        signals = generate_signal(context, stock_code, price, 0.5, 'buy', '测试')
    return signals
'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(content)
            return Path(f.name)

    @staticmethod
    def create_mock_xtdata() -> Mock:
        """
        创建Mock xtdata模块

        Returns:
            Mock xtdata对象
        """
        mock = MagicMock()

        # Mock数据获取
        mock.get_market_data_ex = Mock(return_value=None)
        mock.get_full_tick = Mock(return_value={})
        mock.get_instrument_type = Mock(return_value=1)

        # Mock订阅
        mock.subscribe_quote = Mock(return_value=None)
        mock.unsubscribe_quote = Mock(return_value=None)

        # Mock下载
        mock.download_history_data_ex = Mock(return_value=None)

        # Mock交易日
        mock.get_trading_dates = Mock(return_value=['20240101', '20240102', '20240103'])

        return mock

    @staticmethod
    def create_mock_backtest_result() -> Dict:
        """
        创建模拟回测结果

        Returns:
            回测结果字典
        """
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

    @staticmethod
    def create_mock_logger():
        """
        创建Mock日志记录器

        Returns:
            Mock logger对象
        """
        mock = Mock()
        mock.debug = Mock()
        mock.info = Mock()
        mock.warning = Mock()
        mock.error = Mock()
        mock.critical = Mock()
        return mock

    @staticmethod
    def create_mock_signal(**kwargs):
        """
        创建模拟交易信号

        Returns:
            交易信号字典
        """
        signal = {
            'stock': kwargs.get('stock', '000001.SZ'),
            'action': kwargs.get('action', 'buy'),
            'price': kwargs.get('price', 10.50),
            'volume': kwargs.get('volume', 1000),
            'amount': kwargs.get('amount', 10500.0),
            'reason': kwargs.get('reason', '测试信号'),
        }
        return signal
