# GUIkhQuant模块 - 主界面控制器

## 📋 模块概述

**文件**: `GUIkhQuant.py` (4851行)
**功能**: 量化交易平台的核心主界面，集成策略执行、回测控制、账户管理和数据监控
**框架**: PyQt5
**依赖**: khFrame.py, backtest_result_window.py, SettingsDialog.py

## 🏗️ 核心架构

### 主要类结构
```python
class KhQuantMainWindow(QMainWindow):
    """看海量化交易系统主窗口"""

    def __init__(self):
        # 界面初始化
        # 组件创建和布局
        # 信号连接和事件绑定

    # 核心功能方法
    def load_strategy(self)           # 加载策略文件
    def start_backtest(self)          # 开始回测
    def stop_backtest(self)           # 停止回测
    def save_configuration(self)      # 保存配置
    def load_configuration(self)      # 加载配置
```

### 界面布局结构
```
┌─────────────────────────────────────────────────────────────┐
│                    顶部工具栏 (QToolBar)                      │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│             │             │             │                     │
│ 左侧配置面板 │ 中间驱动面板 │ 右侧日志面板 │ 系统状态和进度条     │
│             │             │             │                     │
│ - 策略配置   │ - 触发方式   │ - 系统日志   │ - 连接状态指示灯     │
│ - 回测参数   │ - 账户信息   │ - 交易日志   │ - 进度条显示        │
│ - 数据设置   │ - 盘前盘后   │ - 错误日志   │ - 状态信息          │
│ - 股票池     │             │             │                     │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## 🔧 核心功能模块

### 1. 顶部工具栏管理
**对应方法**: `setup_toolbar()`

#### 工具栏按钮功能
```python
# 工具栏按钮定义
toolbar_actions = {
    'load_config': {           # 加载配置
        'icon': 'folder_open.png',
        'tooltip': '加载配置文件(.kh)',
        'shortcut': 'Ctrl+O',
        'method': self.load_configuration
    },
    'save_config': {           # 保存配置
        'icon': 'save.png',
        'tooltip': '保存当前配置',
        'shortcut': 'Ctrl+S',
        'method': self.save_configuration
    },
    'save_as_config': {        # 配置另存为
        'icon': 'save_as.png',
        'tooltip': '配置另存为',
        'shortcut': 'Ctrl+Shift+S',
        'method': self.save_configuration_as
    },
    'start_backtest': {        # 开始运行
        'icon': 'play.png',
        'tooltip': '开始策略回测',
        'shortcut': 'F5',
        'method': self.start_backtest
    },
    'stop_backtest': {         # 停止运行
        'icon': 'stop.png',
        'tooltip': '停止策略回测',
        'shortcut': 'Esc',
        'method': self.stop_backtest
    },
    'data_center': {           # 数据中心
        'icon': 'database.png',
        'tooltip': '打开数据中心',
        'method': self.open_data_center
    },
    'settings': {              # 软件设置
        'icon': 'settings.png',
        'tooltip': '打开软件设置',
        'method': self.open_settings
    }
}
```

### 2. 左侧配置面板
**对应类**: `LeftConfigPanel(QWidget)`

#### 策略配置组
```python
class StrategyConfigGroup(QGroupBox):
    """策略配置组件"""

    def __init__(self):
        # 策略文件选择
        self.strategy_file_edit = QLineEdit()
        self.browse_strategy_btn = QPushButton("选择策略文件")

        # 运行模式（固定为回测）
        self.run_mode_combo = QComboBox()
        self.run_mode_combo.addItems(["回测"])

    def load_strategy_file(self):
        """加载策略文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择策略文件", "", "Python文件 (*.py)"
        )
        if file_path:
            self.strategy_file_edit.setText(file_path)
            # 验证策略文件格式
            self.validate_strategy_file(file_path)
```

#### 回测参数配置
```python
class BacktestConfigGroup(QGroupBox):
    """回测参数配置组件"""

    def __init__(self):
        # 基准合约
        self.benchmark_edit = QLineEdit("sh.000300")

        # 交易成本设置
        self.min_commission_spin = QDoubleSpinBox(0.0, 100.0, 1.0, 5.0)  # 最低佣金
        self.commission_rate_spin = QDoubleSpinBox(0.0, 1.0, 0.0001, 0.0003)  # 佣金比例
        self.stamp_tax_spin = QDoubleSpinBox(0.0, 1.0, 0.0001, 0.0005)  # 印花税
        self.flow_fee_spin = QDoubleSpinBox(0.0, 10.0, 0.1, 0.0)  # 流量费

        # 滑点设置
        self.slippage_type_combo = QComboBox()
        self.slippage_type_combo.addItems(["按最小变动价位", "按成交额比例"])
        self.slippage_value_spin = QDoubleSpinBox(0.0, 1.0, 0.001, 0.001)

        # 回测时间
        self.start_date_edit = QDateEdit()
        self.end_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-6))
        self.end_date_edit.setDate(QDate.currentDate())
```

#### 数据设置组
```python
class DataConfigGroup(QGroupBox):
    """数据配置组件"""

    def __init__(self):
        # 复权方式
        self.fq_type_combo = QComboBox()
        self.fq_type_combo.addItems(["不复权", "前复权", "后复权", "等比前复权", "等比后复权"])

        # 周期类型
        self.cycle_combo = QComboBox()
        self.cycle_combo.addItems(["tick", "1m", "5m", "1d"])

        # 数据字段（动态生成）
        self.field_checkboxes = {}
        self.update_data_fields()

    def update_data_fields(self):
        """根据周期类型更新可选数据字段"""
        cycle = self.cycle_combo.currentText()
        fields = self.get_available_fields(cycle)

        # 清除现有复选框
        for checkbox in self.field_checkboxes.values():
            checkbox.deleteLater()
        self.field_checkboxes.clear()

        # 创建新的复选框
        for field in fields:
            checkbox = QCheckBox(field)
            self.field_checkboxes[field] = checkbox
            self.field_layout.addWidget(checkbox)
```

#### 股票池设置
```python
class StockPoolGroup(QGroupBox):
    """股票池配置组件"""

    def __init__(self):
        # 常用指数成分股
        self.index_checkboxes = {}
        indices = [
            ("上证50", "sh.000016"),
            ("沪深300", "sh.000300"),
            ("中证500", "sh.000905"),
            ("创业板指", "sz.399006"),
            ("科创50", "sh.000688")
        ]

        for name, code in indices:
            checkbox = QCheckBox(name)
            checkbox.setProperty("index_code", code)
            self.index_checkboxes[code] = checkbox
            self.index_layout.addWidget(checkbox)

        # 自选清单
        self.custom_list_checkbox = QCheckBox("自选清单")
        self.edit_custom_list_btn = QPushButton("编辑自选清单")

        # 手动管理表格
        self.stock_table = QTableWidget()
        self.setup_stock_table()

        # 操作按钮
        self.add_stock_btn = QPushButton("添加股票")
        self.remove_stock_btn = QPushButton("删除股票")
        self.import_list_btn = QPushButton("导入列表")
        self.clear_list_btn = QPushButton("清空列表")
```

### 3. 中间驱动面板
**对应类**: `MiddleDriverPanel(QWidget)`

#### 触发方式设置
```python
class TriggerConfigGroup(QGroupBox):
    """触发方式配置组件"""

    def __init__(self):
        # 触发类型选择
        self.trigger_type_combo = QComboBox()
        self.trigger_type_combo.addItems(["Tick触发", "K线触发", "自定义时间触发"])

        # K线周期设置（仅在K线触发时显示）
        self.kline_cycle_combo = QComboBox()
        self.kline_cycle_combo.addItems(["1m", "5m"])

        # 自定义时间设置（仅在自定义触发时显示）
        self.time_list_edit = QTextEdit()
        self.time_generator_btn = QPushButton("生成时间点")

        # 连接信号
        self.trigger_type_combo.currentTextChanged.connect(self.on_trigger_type_changed)

    def on_trigger_type_changed(self, trigger_type):
        """触发类型改变时更新界面"""
        if trigger_type == "K线触发":
            self.kline_cycle_widget.show()
            self.custom_time_widget.hide()
        elif trigger_type == "自定义时间触发":
            self.kline_cycle_widget.hide()
            self.custom_time_widget.show()
        else:
            self.kline_cycle_widget.hide()
            self.custom_time_widget.hide()

    def generate_time_points(self):
        """生成自定义时间点"""
        from .time_generator import TimePointGenerator

        generator = TimePointGenerator()
        time_points = generator.generate_regular_interval(
            start_time="09:30:00",
            end_time="15:00:00",
            interval_minutes=10
        )

        self.time_list_edit.setPlainText('\n'.join(time_points))
```

#### 账户信息组
```python
class AccountInfoGroup(QGroupBox):
    """账户信息组件"""

    def __init__(self):
        # 虚拟账户设置
        self.initial_capital_spin = QDoubleSpinBox(10000, 100000000, 10000, 1000000)
        self.min_trade_volume_spin = QSpinBox(100, 1000000, 100, 100)

        # 账户信息显示（只读）
        self.cash_label = QLabel("0.00")
        self.market_value_label = QLabel("0.00")
        self.total_asset_label = QLabel("0.00")
        self.position_count_label = QLabel("0")

        # 更新账户信息
        self.update_account_info()

    def update_account_info(self):
        """更新账户信息显示"""
        account = self.get_current_account()
        if account:
            self.cash_label.setText(f"{account['cash']:,.2f}")
            self.market_value_label.setText(f"{account['market_value']:,.2f}")
            self.total_asset_label.setText(f"{account['total_asset']:,.2f}")
```

#### 盘前盘后设置
```python
class PrePostMarketGroup(QGroupBox):
    """盘前盘后设置组件"""

    def __init__(self):
        # 盘前触发
        self.pre_market_enabled = QCheckBox("触发盘前回调")
        self.pre_market_time = QTimeEdit()
        self.pre_market_time.setTime(QTime(9, 25))

        # 盘后触发
        self.post_market_enabled = QCheckBox("触发盘后回调")
        self.post_market_time = QTimeEdit()
        self.post_market_time.setTime(QTime(15, 5))

        # 连接信号
        self.pre_market_enabled.toggled.connect(self.on_pre_market_toggled)
        self.post_market_enabled.toggled.connect(self.on_post_market_toggled)
```

### 4. 右侧日志面板
**对应类**: `RightLogPanel(QWidget)`

#### 日志显示组件
```python
class LogDisplayWidget(QWidget):
    """日志显示组件"""

    def __init__(self):
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # 设置日志颜色格式
        self.setup_log_formats()

        # 日志过滤复选框
        self.filter_checkboxes = {
            'DEBUG': QCheckBox("DEBUG"),
            'INFO': QCheckBox("INFO"),
            'WARNING': QCheckBox("WARNING"),
            'ERROR': QCheckBox("ERROR"),
            'TRADE': QCheckBox("TRADE")
        }

        # 设置默认勾选状态
        self.filter_checkboxes['DEBUG'].setChecked(False)
        for checkbox in self.filter_checkboxes.values():
            if checkbox.text() != 'DEBUG':
                checkbox.setChecked(True)

    def setup_log_formats(self):
        """设置日志颜色格式"""
        self.text_format = {
            'DEBUG': self.create_format(QColor(128, 128, 255)),  # 浅紫色
            'INFO': self.create_format(QColor(255, 255, 255)),   # 白色
            'WARNING': self.create_format(QColor(255, 165, 0)),   # 橙色
            'ERROR': self.create_format(QColor(255, 0, 0)),       # 红色
            'TRADE': self.create_format(QColor(0, 255, 255))     # 青色
        }

    def append_log(self, message, level='INFO'):
        """添加日志消息"""
        if not self.should_show_log(level):
            return

        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 设置格式
        char_format = self.text_format.get(level, self.text_format['INFO'])
        cursor.setCharFormat(char_format)

        # 添加时间戳和消息
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        cursor.insertText(f"[{timestamp}] [{level}] {message}\n")

        # 自动滚动到底部
        self.log_text.ensureCursorVisible()

        # 限制日志行数，避免内存占用过多
        self.limit_log_lines()
```

#### 日志操作按钮
```python
class LogControlPanel(QWidget):
    """日志控制面板"""

    def __init__(self, parent_log_widget):
        self.parent_log = parent_log_widget

        # 控制按钮
        self.clear_log_btn = QPushButton("清空日志")
        self.save_log_btn = QPushButton("保存日志")
        self.test_log_btn = QPushButton("测试日志")
        self.open_result_btn = QPushButton("打开回测指标")
        self.open_result_btn.setEnabled(False)  # 回测结束后才启用

        # 连接信号
        self.clear_log_btn.clicked.connect(self.parent_log.clear_log)
        self.save_log_btn.clicked.connect(self.parent_log.save_log)
        self.test_log_btn.clicked.connect(self.generate_test_logs)
        self.open_result_btn.clicked.connect(self.open_backtest_result)

    def generate_test_logs(self):
        """生成测试日志"""
        test_logs = [
            ("这是一条DEBUG级别的测试日志", "DEBUG"),
            ("这是一条INFO级别的测试日志", "INFO"),
            ("这是一条WARNING级别的测试日志", "WARNING"),
            ("这是一条ERROR级别的测试日志", "ERROR"),
            ("这是一条TRADE级别的测试日志", "TRADE")
        ]

        for message, level in test_logs:
            self.parent_log.append_log(message, level)
```

### 5. 底部状态栏
**对应方法**: `setup_status_bar()`

```python
def setup_status_bar(self):
    """设置状态栏"""
    self.status_bar = self.statusBar()

    # 左侧状态文本
    self.status_label = QLabel("准备就绪")
    self.status_bar.addWidget(self.status_label)

    # 右侧进度条
    self.progress_bar = QProgressBar()
    self.progress_bar.setVisible(False)
    self.progress_bar.setMaximumWidth(300)
    self.status_bar.addPermanentWidget(self.progress_bar)

    # MiniQMT连接状态指示灯
    self.connection_indicator = QLabel()
    self.connection_indicator.setFixedSize(16, 16)
    self.update_connection_status(False)  # 初始状态为未连接
    self.status_bar.addPermanentWidget(self.connection_indicator)

def update_connection_status(self, connected):
    """更新连接状态指示灯"""
    if connected:
        self.connection_indicator.setStyleSheet(
            "QLabel { background-color: #00ff00; border-radius: 8px; }"
        )
        self.connection_indicator.setToolTip("MiniQMT已连接")
    else:
        self.connection_indicator.setStyleSheet(
            "QLabel { background-color: #ff0000; border-radius: 8px; }"
        )
        self.connection_indicator.setToolTip("MiniQMT未连接")
```

## 🔗 核心业务逻辑

### 1. 策略加载和验证
```python
def load_strategy_file(self):
    """加载并验证策略文件"""
    file_path, _ = QFileDialog.getOpenFileName(
        self, "选择策略文件", "", "Python文件 (*.py)"
    )

    if not file_path:
        return

    try:
        # 1. 文件存在性检查
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"策略文件不存在: {file_path}")

        # 2. 语法检查
        with open(file_path, 'r', encoding='utf-8') as f:
            strategy_code = f.read()

        compile(strategy_code, file_path, 'exec')

        # 3. 必需函数检查
        self.validate_required_functions(file_path)

        # 4. 更新界面
        self.strategy_file_edit.setText(file_path)
        self.log_message(f"策略文件加载成功: {os.path.basename(file_path)}", "INFO")

    except Exception as e:
        self.log_message(f"策略文件加载失败: {str(e)}", "ERROR")
        QMessageBox.critical(self, "加载失败", f"无法加载策略文件:\n{str(e)}")

def validate_required_functions(self, file_path):
    """验证策略文件是否包含必需的函数"""
    required_functions = ['init', 'khHandlebar']

    # 动态导入策略模块检查
    spec = importlib.util.spec_from_file_location("strategy", file_path)
    strategy_module = importlib.util.module_from_spec(spec)

    missing_functions = []
    for func_name in required_functions:
        if not hasattr(strategy_module, func_name):
            missing_functions.append(func_name)

    if missing_functions:
        raise ValueError(f"策略文件缺少必需函数: {', '.join(missing_functions)}")
```

### 2. 回测执行控制
```python
def start_backtest(self):
    """开始回测执行"""
    try:
        # 1. 参数验证
        if not self.validate_backtest_config():
            return

        # 2. 禁用控制按钮
        self.set_running_state(True)

        # 3. 初始化回测框架
        self.initialize_backtest_framework()

        # 4. 启动后台回测线程
        self.backtest_thread = BacktestThread(self.backtest_config)
        self.backtest_thread.log_signal.connect(self.on_backtest_log)
        self.backtest_thread.progress_signal.connect(self.on_backtest_progress)
        self.backtest_thread.finished_signal.connect(self.on_backtest_finished)
        self.backtest_thread.start()

        # 5. 更新状态
        self.status_label.setText("策略运行中...")
        self.log_message("回测开始执行", "INFO")

    except Exception as e:
        self.set_running_state(False)
        self.log_message(f"回测启动失败: {str(e)}", "ERROR")

def stop_backtest(self):
    """停止回测执行"""
    if self.backtest_thread and self.backtest_thread.isRunning():
        self.backtest_thread.stop()
        self.log_message("正在停止回测...", "WARNING")

    self.set_running_state(False)
    self.status_label.setText("回测已停止")

def on_backtest_finished(self, success, result):
    """回测完成回调"""
    self.set_running_state(False)

    if success:
        self.status_label.setText("回测完成")
        self.log_message("回测执行完成", "INFO")

        # 启用查看结果按钮
        self.log_control_panel.open_result_btn.setEnabled(True)

        # 显示回测结果
        self.show_backtest_result(result)
    else:
        self.status_label.setText("回测失败")
        self.log_message(f"回测执行失败: {result}", "ERROR")
```

### 3. 配置文件管理
```python
def save_configuration(self, file_path=None):
    """保存当前配置到.kh文件"""
    if file_path is None:
        # 使用当前配置文件路径
        file_path = self.current_config_file

    if file_path is None:
        # 如果还是没有路径，则另存为
        return self.save_configuration_as()

    try:
        config = {
            'strategy': {
                'file_path': self.strategy_config.strategy_file_edit.text(),
                'run_mode': self.strategy_config.run_mode_combo.currentText()
            },
            'backtest': {
                'benchmark': self.backtest_config.benchmark_edit.text(),
                'start_date': self.backtest_config.start_date_edit.date().toString("yyyy-MM-dd"),
                'end_date': self.backtest_config.end_date_edit.date().toString("yyyy-MM-dd"),
                'trade_cost': {
                    'min_commission': self.backtest_config.min_commission_spin.value(),
                    'commission_rate': self.backtest_config.commission_rate_spin.value(),
                    'stamp_tax': self.backtest_config.stamp_tax_spin.value(),
                    'flow_fee': self.backtest_config.flow_fee_spin.value()
                },
                'slippage': {
                    'type': self.backtest_config.slippage_type_combo.currentIndex(),
                    'value': self.backtest_config.slippage_value_spin.value()
                }
            },
            'data': {
                'fq_type': self.data_config.fq_type_combo.currentText(),
                'cycle_type': self.data_config.cycle_combo.currentText(),
                'fields': self.get_selected_data_fields()
            },
            'stock_pool': {
                'indices': self.get_selected_indices(),
                'custom_list_enabled': self.stock_pool_config.custom_list_checkbox.isChecked(),
                'manual_stocks': self.get_manual_stocks()
            },
            'trigger': {
                'type': self.trigger_config.trigger_type_combo.currentText(),
                'kline_cycle': self.trigger_config.kline_cycle_combo.currentText(),
                'custom_times': self.trigger_config.time_list_edit.toPlainText().split('\n')
            },
            'account': {
                'initial_capital': self.account_config.initial_capital_spin.value(),
                'min_trade_volume': self.account_config.min_trade_volume_spin.value()
            }
        }

        # 保存到JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        self.current_config_file = file_path
        self.log_message(f"配置已保存: {os.path.basename(file_path)}", "INFO")

    except Exception as e:
        self.log_message(f"配置保存失败: {str(e)}", "ERROR")
        QMessageBox.critical(self, "保存失败", f"无法保存配置文件:\n{str(e)}")

def load_configuration(self, file_path):
    """从.kh文件加载配置"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 应用配置到界面
        self.apply_config_to_ui(config)

        self.current_config_file = file_path
        self.log_message(f"配置已加载: {os.path.basename(file_path)}", "INFO")

    except Exception as e:
        self.log_message(f"配置加载失败: {str(e)}", "ERROR")
        QMessageBox.critical(self, "加载失败", f"无法加载配置文件:\n{str(e)}")
```

## 🎨 界面样式和主题

### 样式表设置
```python
def setup_application_style(self):
    """设置应用程序样式"""
    style_sheet = """
    /* 主窗口样式 */
    QMainWindow {
        background-color: #f0f0f0;
    }

    /* 分组框样式 */
    QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }

    /* 按钮样式 */
    QPushButton {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        font-size: 14px;
        margin: 4px 2px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QPushButton:pressed {
        background-color: #3d8b40;
    }

    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    /* 表格样式 */
    QTableWidget {
        gridline-color: #cccccc;
        background-color: white;
        selection-background-color: #3498db;
    }

    QTableWidget::item {
        padding: 5px;
    }

    QHeaderView::section {
        background-color: #f8f8f8;
        padding: 5px;
        border: 1px solid #cccccc;
        font-weight: bold;
    }

    /* 日志文本框样式 */
    QTextEdit#log_text {
        background-color: #2d3748;
        color: #e2e8f0;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        border: 1px solid #4a5568;
    }

    /* 进度条样式 */
    QProgressBar {
        border: 2px solid #cccccc;
        border-radius: 5px;
        text-align: center;
    }

    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 3px;
    }
    """

    self.setStyleSheet(style_sheet)
```

## 🔄 信号和槽连接

### 主要信号连接
```python
def connect_signals(self):
    """连接信号和槽"""
    # 工具栏按钮信号
    self.load_config_action.triggered.connect(self.load_configuration)
    self.save_config_action.triggered.connect(self.save_configuration)
    self.start_action.triggered.connect(self.start_backtest)
    self.stop_action.triggered.connect(self.stop_backtest)

    # 配置面板信号
    self.strategy_config.browse_strategy_btn.clicked.connect(self.browse_strategy_file)
    self.stock_pool_config.edit_custom_list_btn.clicked.connect(self.edit_custom_list)

    # 触发类型变化信号
    self.trigger_config.trigger_type_combo.currentTextChanged.connect(
        self.on_trigger_type_changed
    )

    # 日志过滤信号
    for checkbox in self.log_panel.filter_checkboxes.values():
        checkbox.toggled.connect(self.log_panel.update_log_filter)
```

## 📈 性能优化和最佳实践

### 1. 界面响应性优化
- 使用QThread进行耗时操作，避免界面冻结
- 实现日志消息的批量更新，减少界面刷新频率
- 使用信号槽机制进行线程间通信

### 2. 内存管理
- 定期清理日志内容，避免内存占用过多
- 及时释放不需要的对象引用
- 使用弱引用避免循环引用

### 3. 用户体验优化
- 提供进度反馈和状态更新
- 实现操作的撤销和重做功能
- 添加键盘快捷键支持

---

*本模块是整个量化交易系统的核心控制中心，负责协调各个子模块的工作，为用户提供统一的操作界面。*