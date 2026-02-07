# KHQuant 测试指南

## 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements-test.txt
```

### 2. 运行所有测试

```bash
# 基础运行
pytest tests/ -v

# 带覆盖率报告
pytest tests/ --cov=khQuantImport --cov=MyTT --cov=khQTTools --cov=khTrade --cov-report=html

# 生成详细覆盖率报告
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### 3. 运行特定测试

```bash
# 运行特定文件
pytest tests/test_khQuantImport.py -v

# 运行特定类
pytest tests/test_khQuantImport.py::TestTimeInfo -v

# 运行特定测试函数
pytest tests/test_khQuantImport.py::TestTimeInfo::test_date_str_property -v
```

### 4. 使用标记运行测试

```bash
# 只运行单元测试
pytest tests/ -m unit -v

# 只运行集成测试
pytest tests/ -m integration -v

# 排除慢速测试
pytest tests/ -m "not slow" -v

# 运行高优先级测试
pytest tests/ -m high_priority -v
```

## 测试结构

```
tests/
├── __init__.py                    # 包初始化
├── conftest.py                    # 共享fixtures和配置
├── test_khRisk.py                 # 风险管理测试
├── test_khSecurity.py             # 安全验证测试
├── test_logging_config.py         # 日志配置测试
├── test_khQuantImport.py          # 统一导入模块测试
├── test_MyTT.py                   # 技术指标库测试 (待创建)
├── test_khQTTools.py              # 量化工具集测试 (待创建)
├── test_khTrade.py                # 交易管理测试 (待创建)
├── test_constants.py              # 常量定义测试 (待创建)
├── test_khConfig.py               # 配置管理测试 (待创建)
├── test_khFrame.py                # 策略框架测试 (待创建)
├── fixtures/                      # 测试数据目录
│   ├── sample_data.json
│   └── sample_signals.json
├── TEST_PLAN.md                   # 完整测试计划
└── TEST_IMPLEMENTATION_STATUS.md  # 实现状态跟踪
```

## 测试编写规范

### 1. 测试文件命名
- 格式: `test_<module_name>.py`
- 示例: `test_khQuantImport.py`

### 2. 测试类命名
- 格式: `Test<ClassName>`
- 示例: `TestTimeInfo`

### 3. 测试函数命名
- 格式: `test_<function_name>_<scenario>`
- 示例: `test_get_price_normal`, `test_get_price_nan`

### 4. AAA模式

```python
def test_example():
    # Arrange - 准备测试数据
    data = {'close': 10.50}

    # Act - 执行被测试功能
    result = function_to_test(data)

    # Assert - 验证结果
    assert result == 10.50
```

### 5. 使用Fixtures

```python
def test_with_fixture(sample_stock_data):
    """使用共享fixture"""
    result = process_data(sample_stock_data)
    assert result is not None
```

## 常用命令

### 并行测试
```bash
pytest tests/ -n auto  # 使用所有CPU核心
```

### 只运行失败的测试
```bash
pytest tests/ --lf  # last-failed
```

### 详细的错误输出
```bash
pytest tests/ -vv --tb=long
```

### 停在第一个失败处
```bash
pytest tests/ -x
```

### 性能测试
```bash
pytest tests/ --benchmark-only
```

## 覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| khQuantImport.py | 95% | ✅ 完成 |
| MyTT.py | 90% | ⏳ 待创建 |
| khQTTools.py | 90% | ⏳ 待创建 |
| khTrade.py | 90% | ⏳ 待创建 |
| khRisk.py | 95% | ✅ 完成 |
| khSecurity.py | 95% | ✅ 完成 |
| constants.py | 100% | ⏳ 待创建 |
| khConfig.py | 85% | ⏳ 待创建 |
| khFrame.py | 85% | ⏳ 待创建 |
| **总体目标** | **90%+** | **进行中** |

## CI/CD

测试会在以下情况自动运行：
- Push到main或develop分支
- 创建Pull Request

GitHub Actions会：
1. 运行完整测试套件
2. 生成覆盖率报告
3. 检查覆盖率是否达标(>85%)
4. 在多个操作系统和Python版本上测试

## 查看覆盖率报告

### 本地查看
```bash
pytest tests/ --cov-report=html
# 然后打开 htmlcov/index.html
```

### 在线查看
推送到GitHub后，查看Codecov报告。

## 故障排除

### 导入错误
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Windows: set PYTHONPATH=%PYTHONPATH%;%CD%
```

### 找不到模块
确保在项目根目录运行测试，并且已安装依赖：
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Mock相关错误
检查`conftest.py`中的fixtures是否正确配置。

## 贡献指南

1. 为新功能编写测试
2. 确保所有测试通过
3. 保持90%+的覆盖率
4. 遵循AAA模式和命名规范
5. 使用类型提示

## 联系方式

如有问题，请创建GitHub Issue。

---

*最后更新: 2026-02-07*
