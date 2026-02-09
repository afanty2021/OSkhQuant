# GUI测试框架文档

## 概述

本目录包含看海量化交易系统(KHQuant)的PyQt5 GUI测试用例，基于pytest-qt框架构建。

## 测试框架

### 核心依赖

- **pytest**: 测试框架
- **pytest-qt**: PyQt5 GUI测试扩展
- **PyQt5**: GUI框架
- **pytest-mock**: Mock支持

### 目录结构

```
tests/gui/
├── __init__.py              # GUI测试模块初始化
├── conftest.py              # GUI测试配置和fixtures
├── README.md                # 本文档
├── utils/                   # 测试工具模块
│   ├── __init__.py
│   ├── widget_helpers.py    # Widget辅助工具
│   ├── signal_helpers.py    # 信号辅助工具
│   └── mock_helpers.py      # Mock辅助工具
├── test_GUIkhQuant.py       # 主界面测试
├── test_GUI.py              # 数据下载管理界面测试
├── test_GUIDataViewer.py    # 数据查看器测试
├── test_backtest_result_window.py  # 回测结果窗口测试
└── test_SettingsDialog.py   # 设置对话框测试
```

## 安装

### 1. 安装pytest-qt

```bash
# 激活虚拟环境
conda activate khquant-test

# 安装pytest-qt
pip install pytest-qt

# 或使用requirements文件
pip install -r requirements-test.txt
```

### 2. 验证安装

```bash
# 检查pytest-qt版本
python -c "import pytestqt; print(pytestqt.__version__)"

# 运行简单测试
pytest tests/gui/ -v
```

## 运行测试

### 运行所有GUI测试

```bash
# 使用虚拟环境中的pytest
D:\scoop\apps\miniconda\current\envs\khquant-test\Scripts\pytest.exe tests/gui/ -v

# 或激活环境后运行
conda activate khquant-test
pytest tests/gui/ -v
```

### 运行特定测试文件

```bash
# 测试主界面
pytest tests/gui/test_GUIkhQuant.py -v

# 测试数据下载界面
pytest tests/gui/test_GUI.py -v

# 测试数据查看器
pytest tests/gui/test_GUIDataViewer.py -v
```

### 运行特定测试类

```bash
# 测试基础功能
pytest tests/gui/test_GUIkhQuant.py::TestGUIkhQuantBasic -v

# 测试Mock功能
pytest tests/gui/test_GUIkhQuant.py::TestGUIkhQuantMock -v
```

### 运行特定测试方法

```bash
# 测试单个方法
pytest tests/gui/test_GUIkhQuant.py::TestGUIkhQuantBasic::test_module_import -v
```

### 使用标记运行测试

```bash
# 只运行GUI测试
pytest -m gui -v

# 运行慢速GUI测试
pytest -m slow_gui -v

# 排除慢速测试
pytest -m "not slow_gui" -v
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest tests/gui/ --cov=GUIkhQuant --cov=GUI --cov=GUIDataViewer --cov-report=html

# 生成终端覆盖率报告
pytest tests/gui/ --cov=GUIkhQuant --cov=GUI --cov=GUIDataViewer --cov-report=term-missing
```

### 查看覆盖率报告

```bash
# HTML报告在 htmlcov/index.html
start htmlcov/index.html  # Windows
```

## 测试编写指南

### 基本测试结构

```python
import pytest
from pytestqt import qtbot
from unittest.mock import Mock, MagicMock

pytestmark = pytest.mark.gui  # 标记为GUI测试

class TestMyGUI:
    """GUI测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, qtbot):
        """每个测试前的设置"""
        self.qtbot = qtbot
        self.temp_dir = tempfile.mkdtemp()
        yield
        # 清理
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_widget_creation(self):
        """测试Widget创建"""
        from PyQt5.QtWidgets import QWidget

        widget = QWidget()
        self.qtbot.addWidget(widget)

        assert widget is not None
```

### 使用qtbot fixture

```python
def test_button_click(qtbot):
    """测试按钮点击"""
    from PyQt5.QtWidgets import QPushButton
    from PyQt5.QtCore import Qt

    button = QPushButton("点击我")
    qtbot.addWidget(button)

    # 模拟点击
    qtbot.mouseClick(button, Qt.LeftButton)

    # 验证结果
    assert button.text() == "点击我"
```

### 使用信号助手

```python
def test_signal_emission(qtbot):
    """测试信号发射"""
    from PyQt5.QtCore import QObject, pyqtSignal

    class TestObject(QObject):
        test_signal = pyqtSignal(str)

    obj = TestObject()
    received = []

    def slot(message):
        received.append(message)

    obj.test_signal.connect(slot)
    obj.test_signal.emit("test")

    assert len(received) == 1
```

### 使用Widget助手

```python
from tests.gui.utils import WidgetHelpers

def test_widget_helpers(qtbot):
    """测试Widget助手"""
    from PyQt5.QtWidgets import QLineEdit

    line_edit = QLineEdit()

    # 使用助手设置文本
    WidgetHelpers.set_line_edit_text(qtbot, line_edit, "test")

    # 使用助手断言
    WidgetHelpers.assert_text_equal(line_edit, "test")
```

## 测试策略

### 1. Mock测试

对于复杂的GUI组件，使用Mock进行测试：

```python
def test_with_mock():
    """使用Mock测试"""
    mock_window = Mock()
    mock_window.show = Mock()
    mock_window.close = Mock()

    mock_window.show()
    mock_window.show.assert_called_once()
```

### 2. 集成测试

测试GUI组件之间的交互：

```python
def test_component_integration():
    """测试组件集成"""
    # 测试数据流
    # 测试信号连接
    # 测试状态变化
```

### 3. UI测试

测试UI元素的正确性：

```python
def test_ui_elements(qtbot):
    """测试UI元素"""
    from PyQt5.QtWidgets import QPushButton, QLabel

    button = QPushButton("确定")
    label = QLabel("测试")

    assert button.text() == "确定"
    assert label.text() == "测试"
```

## 常见问题

### 1. PyQt5未安装

**问题**: ImportError: No module named 'PyQt5'

**解决**:
```bash
pip install PyQt5
```

### 2. pytest-qt未安装

**问题**: ImportError: No module named 'pytestqt'

**解决**:
```bash
pip install pytest-qt
```

### 3. QApplication未创建

**问题**: QApplication实例不存在

**解决**: 使用qapp fixture（pytest-qt自动提供）

### 4. GUI测试超时

**问题**: GUI测试执行时间过长

**解决**:
- 使用Mock代替实际GUI操作
- 设置合理的超时时间
- 使用标记跳过慢速测试

### 5. 信号未触发

**问题**: 信号断言失败

**解决**:
- 使用qtbot.wait_signal()等待信号
- 增加等待时间
- 检查信号连接是否正确

## 最佳实践

### 1. 测试隔离

每个测试应该独立运行，不依赖其他测试：

```python
@pytest.fixture(autouse=True)
def setup(self):
    """每个测试独立设置"""
    self.temp_dir = tempfile.mkdtemp()
    yield
    # 清理
    shutil.rmtree(self.temp_dir, ignore_errors=True)
```

### 2. 使用Mock

对于复杂的依赖，使用Mock简化测试：

```python
@patch('GUIkhQuant.xtdata')
def test_with_mock_xtdata(mock_xtdata):
    """使用Mock xtdata测试"""
    mock_xtdata.get_market_data_ex.return_value = None
    # 测试逻辑
```

### 3. 合理的断言

使用明确的断言消息：

```python
assert widget.isVisible(), "Widget应该是可见的"
assert value == expected, f"值不匹配: {value} != {expected}"
```

### 4. 测试覆盖

确保测试覆盖主要功能：

- UI组件创建
- 信号和槽连接
- 用户交互
- 数据绑定
- 错误处理

## 测试标记

### 可用标记

- `gui`: GUI测试标记
- `slow_gui`: 慢速GUI测试
- `integration_gui`: GUI集成测试

### 使用标记

```python
@pytest.mark.gui
def test_my_gui():
    """GUI测试"""
    pass

@pytest.mark.slow_gui
def test_slow_operation():
    """慢速GUI测试"""
    pass
```

## 贡献指南

### 添加新测试

1. 在相应的测试文件中添加测试类
2. 使用描述性的测试名称
3. 添加必要的fixtures
4. 编写清晰的断言
5. 运行测试确保通过

### 代码风格

- 遵循PEP 8规范
- 使用类型注解
- 添加文档字符串
- 保持测试简洁

## 参考资源

- [pytest-qt文档](https://pytest-qt.readthedocs.io/)
- [PyQt5文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [pytest文档](https://docs.pytest.org/)
- [项目主文档](../../CLAUDE.md)

## 维护者

- AI Assistant
- 最后更新: 2026-02-09

## 版本历史

- v1.0.0 (2026-02-09): 初始版本
  - 创建GUI测试框架
  - 添加基础测试用例
  - 实现测试工具类
