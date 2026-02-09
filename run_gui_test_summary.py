# coding: utf-8
"""
GUI测试结果统计脚本
"""

import subprocess
import sys
import re
from pathlib import Path

def main():
    """主函数"""
    print("="*60)
    print("KHQuant GUI测试结果统计")
    print("="*60)

    # 运行测试
    print("\n正在运行GUI测试...")
    result = subprocess.run(
        [r'D:\scoop\apps\miniconda\current\envs\khquant-test\Scripts\pytest.exe',
         'tests/gui/', '-v', '--tb=no'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    # 解析输出
    output = result.stdout

    # 统计测试结果
    passed = len(re.findall(r'PASSED', output))
    failed = len(re.findall(r'FAILED', output))
    skipped = len(re.findall(r'SKIPPED', output))
    errors = len(re.findall(r'ERROR collecting', output))

    total = passed + failed + skipped + errors

    print(f"\nTotal: {total} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print("="*60)

    # 显示测试覆盖率
    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"测试通过率: {pass_rate:.1f}%")

    # 显示各模块测试情况
    print("\n各模块测试情况:")
    modules = [
        ('GUIkhQuant', 'test_GUIkhQuant.py'),
        ('GUI', 'test_GUI.py'),
        ('GUIDataViewer', 'test_GUIDataViewer.py'),
        ('BacktestResult', 'test_backtest_result_window.py'),
        ('SettingsDialog', 'test_SettingsDialog.py'),
    ]

    for module_name, test_file in modules:
        module_passed = len(re.findall(f'{test_file}.*PASSED', output))
        module_total = len(re.findall(f'{test_file}::', output))
        if module_total > 0:
            print(f"  {module_name}: {module_passed}/{module_total} 通过")

    # 显示通过的测试类别
    print("\nPassed test categories:")
    categories = [
        'Mock', 'WithQt', 'Components', 'UI', 'Statistics',
        'Export', 'Categories', 'Presets', 'Integration',
        'Utilities', 'Threading', 'FileOperations', 'Signals',
        'Data', 'Display', 'Search', 'Filter'
    ]

    for category in categories:
        pattern = f'PASSED.*{category}'
        matches = re.findall(pattern, output)
        if len(matches) > 0:
            print(f"  + {category}: {len(matches)} tests passed")

    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)

    return 0 if failed == 0 and errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
