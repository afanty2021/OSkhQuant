# coding: utf-8
"""
测试运行器

运行所有单元测试并生成报告。

使用方法:
    python run_tests.py
    python run_tests.py -v  # 详细输出
    python run_tests.py test_khRisk  # 只运行特定测试

@author: Test Suite
@version: 1.0
"""

import unittest
import sys
import os
import argparse
import time
from datetime import datetime


def discover_tests(test_dir='tests', pattern='test_*.py'):
    """发现测试用例"""
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # 添加测试目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # 加载测试模块
    suite = test_loader.discover(test_dir, pattern=pattern, top_level_dir=os.path.dirname(os.path.abspath(__file__)))
    return suite


def run_tests(verbosity=1, test_name=None):
    """运行测试"""
    # 设置工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 加载各个测试模块
    test_modules = [
        'tests.test_khRisk',
        'tests.test_khSecurity',
        'tests.test_logging_config',
    ]

    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"警告: 无法加载测试模块 {module_name}: {e}")

    # 如果指定了特定测试名，过滤测试
    if test_name:
        filtered_suite = unittest.TestSuite()
        for test_group in suite:
            for test in test_group:
                if test_name in str(test):
                    filtered_suite.addTest(test)
        suite = filtered_suite

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=verbosity)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # 输出统计信息
    print("\n" + "=" * 70)
    print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"测试用例数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print("=" * 70)

    # 输出失败详情
    if result.failures:
        print("\n失败详情:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)

    if result.errors:
        print("\n错误详情:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)

    return result.wasSuccessful()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行单元测试')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-t', '--test', type=str, help='运行特定测试')
    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1
    success = run_tests(verbosity=verbosity, test_name=args.test)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
