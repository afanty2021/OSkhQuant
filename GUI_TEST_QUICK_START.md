# GUI测试快速使用指南

## 快速开始

### 1. 验证安装

```bash
# 激活虚拟环境
conda activate khquant-test

# 检查pytest-qt是否安装
python -c "import pytestqt; print('pytest-qt version:', pytestqt.__version__)"

# 应该输出: pytest-qt version: 4.5.0
```

### 2. 运行测试

```bash
# 方法1: 运行所有GUI测试
pytest tests/gui/ -v

# 方法2: 运行特定模块测试
pytest tests/gui/test_GUIkhQuant.py -v

# 方法3: 只运行Mock测试（快速）
pytest tests/gui/ -k "Mock" -v

# 方法4: 只运行PyQt5测试
pytest tests/gui/ -k "WithQt" -v
```

### 3. 使用测试运行器

```bash
# 运行交互式测试运行器
python tests/gui/run_gui_tests.py

# 或使用简化版本
python run_gui_test_summary.py
```

## 测试文件说明

### 测试文件列表

| 文件 | 测试内容 | 测试数量 |
|------|---------|---------|
| `test_GUIkhQuant.py` | 主界面测试 | ~20个 |
| `test_GUI.py` | 数据下载管理界面测试 | ~15个 |
| `test_GUIDataViewer.py` | 数据查看器测试 | ~18个 |
| `test_backtest_result_window.py` | 回测结果窗口测试 | ~20个 |
| `test_SettingsDialog.py` | 设置对话框测试 | ~18个 |

### 工具类说明

| 工具类 | 文件 | 功能 |
|--------|------|------|
| WidgetHelpers | `utils/widget_helpers.py` | Widget操作辅助 |
| SignalHelpers | `utils/signal_helpers.py` | 信号测试辅助 |
| MockHelpers | `utils/mock_helpers.py` | Mock对象创建 |

## 常用测试命令

### 查看测试列表

```bash
# 列出所有GUI测试
pytest tests/gui/ --collect-only

# 列出特定文件的测试
pytest tests/gui/test_GUIkhQuant.py --collect-only
```

### 运行特定测试

```bash
# 运行单个测试类
pytest tests/gui/test_GUIkhQuant.py::TestGUIkhQuantMock -v

# 运行单个测试方法
pytest tests/gui/test_GUIkhQuant.py::TestGUIkhQuantMock::test_main_window_mock -v
```

### 生成测试报告

```bash
# 生成HTML覆盖率报告
pytest tests/gui/ --cov=GUIkhQuant --cov=GUI --cov-report=html

# 查看报告
start htmlcov/index.html  # Windows
```

### 使用标记运行测试

```bash
# 只运行GUI测试
pytest -m gui -v

# 排除慢速测试
pytest -m "not slow_gui" -v

# 运行集成测试
pytest -m integration_gui -v
```

## 测试编写示例

### 基本测试结构

```python
import pytest
from pytestqt import qtbot
from unittest.mock import Mock

pytestmark = pytest.mark.gui

class TestMyComponent:
    """组件测试"""

    @pytest.fixture(autouse=True)
    def setup(self, qtbot):
        """设置"""
        self.qtbot = qtbot
        yield
        # 清理

    def test_widget_creation(self):
        """测试Widget创建"""
        from PyQt5.QtWidgets import QWidget

        widget = QWidget()
        self.qtbot.addWidget(widget)

        assert widget is not None
```

### 使用Mock测试

```python
def test_with_mock():
    """使用Mock测试"""
    mock_window = Mock()
    mock_window.show = Mock()

    mock_window.show()
    mock_window.show.assert_called_once()
```

### 使用信号助手

```python
from tests.gui.utils import SignalHelpers

def test_signal(qtbot):
    """测试信号"""
    from PyQt5.QtCore import QObject, pyqtSignal

    class TestObject(QObject):
        test_signal = pyqtSignal(str)

    obj = TestObject()

    # 等待信号
    SignalHelpers.wait_signal(qtbot, obj.test_signal, timeout=1000)
```

## 常见问题

### Q: 测试失败怎么办？

A: 查看详细错误信息：
```bash
pytest tests/gui/ -v --tb=long
```

### Q: 如何跳过某些测试？

A: 使用标记或跳过装饰器：
```bash
pytest tests/gui/ -k "not slow" -v
```

### Q: PyQt5未安装怎么办？

A: 安装PyQt5：
```bash
pip install PyQt5
```

### Q: 如何只运行快速测试？

A: 使用标记过滤：
```bash
pytest tests/gui/ -m "not slow_gui" -v
```

## 下一步

1. 阅读详细文档: `tests/gui/README.md`
2. 查看测试报告: `tests/gui/GUI_TEST_REPORT.md`
3. 运行测试验证环境
4. 开始编写自己的测试

## 获取帮助

- 查看pytest-qt文档: https://pytest-qt.readthedocs.io/
- 查看PyQt5文档: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- 查看项目文档: `CLAUDE.md`

---

**更新时间**: 2026-02-09
**版本**: v1.0.0
