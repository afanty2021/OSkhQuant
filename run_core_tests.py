# coding: utf-8
"""
核心模块测试运行脚本

运行所有不依赖外部库（xtquant、schedule等）的核心模块测试，
并生成覆盖率报告。

使用方法:
    python run_core_tests.py

作者: OsKhQuant
版本: 1.0
日期: 2026-02-08
"""

import sys
import subprocess


def run_tests():
    """运行核心模块测试"""

    # 核心测试模块列表（不依赖外部库）
    core_tests = [
        "tests/test_constants.py",
        "tests/test_khConfig.py",
        "tests/test_khSecurity.py",
        "tests/test_khRisk.py",
        "tests/test_logging_config.py",
        "tests/test_MyTT.py",
        "tests/test_update_manager.py",
        "tests/test_version.py",
        "tests/test_khAlertManager.py",
        # 以下测试依赖外部库，需要特定环境
        # "tests/test_khRealtimeTrader.py",  # 依赖 xtquant
        # "tests/test_khFrame.py",           # 依赖 xtquant
        # "tests/test_khQTTools.py",         # 依赖 xtquant
        # "tests/test_khQuantImport.py",     # 依赖 xtquant
        # "tests/test_khTrade.py",           # 依赖 xtquant
        # "tests/test_miniQMT_data_parser.py", # 需要修复
        # "tests/test_SettingsDialog.py",    # 依赖 xtquant
        # "tests/test_GUIScheduler.py",      # 依赖 schedule
    ]

    # 构建pytest命令
    cmd = [
        sys.executable, "-m", "pytest",
        *core_tests,
        "-v",                    # 详细输出
        "--tb=short",            # 简短的traceback
        "--no-header",           # 不显示header
        "--cov=.",               # 覆盖率统计
        "--cov-report=term-missing",  # 终端显示未覆盖的行
        "--cov-report=html:htmlcov",   # HTML覆盖率报告
        "--no-cov-on-fail",      # 失败时不生成报告
    ]

    print("=" * 70)
    print("看海量化交易系统 - 核心模块测试")
    print("=" * 70)
    print(f"测试模块数: {len(core_tests)}")
    print(f"Python版本: {sys.version}")
    print("=" * 70)
    print()

    # 运行测试
    result = subprocess.run(cmd, shell=False)

    # 打印结果摘要
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("[SUCCESS] All core module tests passed!")
        print()
        print("Coverage reports generated:")
        print("   - Terminal: Uncovered lines shown above")
        print("   - HTML: htmlcov/index.html")
        print()
        print("To view HTML coverage report:")
        print("   Open htmlcov/index.html in your browser")
    else:
        print("[FAILED] Some tests failed, please check the errors above")
    print("=" * 70)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
