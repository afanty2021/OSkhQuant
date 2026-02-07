# KHQuant 测试环境设置指南

## 环境要求

### Python版本
- Python 3.7+
- 推荐使用 Python 3.9 或 3.10

### 操作系统
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 20.04+)

## 安装步骤

### 1. 创建虚拟环境 (推荐)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装项目依赖

```bash
# 安装主要依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r requirements-test.txt
```

### 3. 验证安装

```bash
# 检查pytest版本
pytest --version

# 检查Python版本
python --version
```

## 测试执行

### 基础测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定文件
pytest tests/test_khRisk.py -v

# 运行特定测试类
pytest tests/test_khRisk.py::TestKhRiskManager -v

# 运行特定测试方法
pytest tests/test_khRisk.py::TestKhRiskManager::test_init_defaults -v
```

### 带覆盖率的测试

```bash
# 生成终端覆盖率报告
pytest tests/ --cov=khRisk --cov-report=term-missing

# 生成HTML覆盖率报告
pytest tests/ --cov=khRisk --cov-report=html

# 查看HTML报告
# Windows: start htmlcov/index.html
# macOS: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

### 使用便捷脚本

```bash
# 运行所有测试
python tests/run_test_suite.py

# 生成覆盖率报告
python tests/run_test_suite.py -c

# 运行特定文件
python tests/run_test_suite.py -f tests/test_khRisk.py

# 并行运行(加快速度)
python tests/run_test_suite.py -p auto

# 只运行单元测试
python tests/run_test_suite.py -m unit

# 详细输出
python tests/run_test_suite.py -v
```

## 测试文件说明

### 已有测试

| 测试文件 | 测试模块 | 状态 | 覆盖率 |
|---------|---------|------|--------|
| test_khRisk.py | khRisk.py | ✅ | 95%+ |
| test_khSecurity.py | khSecurity.py | ✅ | 95%+ |
| test_logging_config.py | logging_config.py | ✅ | - |

### 新创建测试

| 测试文件 | 测试模块 | 状态 | 说明 |
|---------|---------|------|------|
| test_khQuantImport.py | khQuantImport.py | ✅ | 统一导入模块测试 |
| test_MyTT.py | MyTT.py | ✅ | 技术指标库测试 |
| test_khQTTools.py | khQTTools.py | ✅ | 量化工具集测试 |
| test_khTrade.py | khTrade.py | ✅ | 交易管理测试 |

## 依赖说明

### 核心依赖
- pytest: 测试框架
- pytest-cov: 覆盖率插件
- pytest-mock: Mock支持
- pytest-benchmark: 性能测试

### 可选依赖
- pytest-xdist: 并行测试
- pytest-timeout: 超时控制
- coverage: 覆盖率工具
- codecov: 在线覆盖率服务

## 常见问题

### Q: 找不到pytest模块
A: 确保已安装测试依赖
```bash
pip install -r requirements-test.txt
```

### Q: 导入模块失败
A: 检查PYTHONPATH或从项目根目录运行
```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;%CD%

# macOS/Linux
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Q: 测试失败
A: 查看详细错误信息
```bash
pytest tests/ -vv --tb=long
```

### Q: 覆盖率为0%
A: 确保从项目根目录运行测试
```bash
cd /path/to/project
pytest tests/ --cov=khRisk
```

## 开发工作流

### 1. 编写新功能
```bash
# 创建功能分支
git checkout -b feature/new-function

# 开发并编写测试
# ...
```

### 2. 运行测试
```bash
# 快速测试(相关模块)
pytest tests/test_module.py -v

# 完整测试
pytest tests/ -v

# 覆盖率检查
pytest tests/ --cov=module --cov-report=html
```

### 3. 提交代码
```bash
# 确保所有测试通过
pytest tests/ -v

# 检查覆盖率
pytest tests/ --cov=. --cov-report=term

# 提交
git add .
git commit -m "feat: 新功能"
```

## CI/CD集成

### GitHub Actions
测试会在以下情况自动运行：
- Push到main或develop分支
- 创建Pull Request

### 本地预览CI
```bash
# 模拟CI环境
pytest tests/ --cov=. --cov-fail-under=85
```

## 性能测试

### 运行性能测试
```bash
# 运行所有性能测试
pytest tests/ --benchmark-only

# 运行特定性能测试
pytest tests/test_module.py::test_function --benchmark-only

# 生成性能报告
pytest tests/ --benchmark-only --benchmark-autosave
```

## 测试数据管理

### Fixtures位置
- 共享fixtures: `tests/conftest.py`
- 模块fixtures: 各测试文件内

### 测试数据文件
- 位置: `tests/fixtures/`
- 格式: JSON, CSV
- 用途: 提供测试样本数据

## 最佳实践

### 1. 测试命名
- 文件: `test_<module>.py`
- 类: `Test<ClassName>`
- 方法: `test_<function>_<scenario>`

### 2. AAA模式
```python
def test_example():
    # Arrange - 准备
    data = create_test_data()

    # Act - 执行
    result = process(data)

    # Assert - 验证
    assert result == expected
```

### 3. 使用Fixtures
```python
def test_with_fixture(sample_data):
    result = function(sample_data)
    assert result is not None
```

### 4. Mock外部依赖
```python
from unittest.mock import patch

def test_with_mock():
    with patch('module.external_function') as mock:
        mock.return_value = 42
        result = function()
        assert result == 42
```

## 下一步

1. ✅ 安装测试依赖
2. ✅ 运行测试验证
3. ✅ 查看覆盖率报告
4. ✅ 根据报告补充测试
5. ✅ 保持高覆盖率

## 联系支持

如有问题，请：
1. 查看 `tests/README.md`
2. 查看 `tests/TEST_PLAN.md`
3. 创建GitHub Issue

---

*最后更新: 2026-02-07*
*版本: 1.0*
