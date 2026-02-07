# coding: utf-8
"""
测试套件运行脚本

提供便捷的测试运行功能，支持：
1. 运行所有测试
2. 运行特定模块测试
3. 生成覆盖率报告
4. 性能测试

@author: Test Suite
@version: 1.0
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def run_tests(args):
    """运行测试"""
    # 构建pytest命令
    cmd = ['pytest', 'tests/']

    # 添加详细输出
    if args.verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')

    # 添加覆盖率
    if args.coverage:
        cmd.extend([
            '--cov=khQuantImport,MyTT,khQTTools,khTrade,khRisk,khSecurity,constants',
            '--cov-report=html',
            '--cov-report=term-missing',
        ])

        # 设置覆盖率阈值
        if args.cov_threshold:
            cmd.append(f'--cov-fail-under={args.cov_threshold}')

    # 添加标记过滤
    if args.mark:
        cmd.append(f'-m {args.mark}')

    # 添加并行运行
    if args.parallel:
        cmd.append(f'-n {args.parallel}')

    # 添加特定文件
    if args.file:
        cmd = ['pytest', args.file, '-v']
        if args.coverage:
            module = args.file.replace('tests/test_', '').replace('.py', '')
            cmd.extend([
                f'--cov={module}',
                '--cov-report=term-missing',
            ])

    # 添加失败后停止
    if args.exitfirst:
        cmd.append('-x')

    # 添加只运行失败的测试
    if args.last_failed:
        cmd.append('--lf')

    # 添加详细错误输出
    if args.tb:
        cmd.append(f'--tb={args.tb}')

    # 运行命令
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode


def run_benchmark(args):
    """运行性能测试"""
    cmd = ['pytest', 'tests/', '--benchmark-only', '-v']

    if args.file:
        cmd = ['pytest', args.file, '--benchmark-only', '-v']

    print(f"运行性能测试: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='KHQuant测试套件运行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s                          # 运行所有测试
  %(prog)s -v                       # 详细输出
  %(prog)s -c                       # 生成覆盖率报告
  %(prog)s -c --cov-threshold 90    # 覆盖率低于90%时失败
  %(prog)s -f test_khRisk.py        # 运行特定测试文件
  %(prog)s -m unit                  # 只运行单元测试
  %(prog)s -p                       # 并行运行测试
  %(prog)s --benchmark              # 运行性能测试
  %(prog)s --lf                     # 只运行上次失败的测试
        '''
    )

    # 基本选项
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')
    parser.add_argument('-x', '--exitfirst', action='store_true',
                        help='第一个失败后停止')
    parser.add_argument('--lf', '--last-failed', action='store_true',
                        help='只运行上次失败的测试')
    parser.add_argument('--tb', choices=['short', 'long', 'line', 'no'],
                        default='short',
                        help='错误回溯格式')

    # 覆盖率选项
    parser.add_argument('-c', '--coverage', action='store_true',
                        help='生成覆盖率报告')
    parser.add_argument('--cov-threshold', type=int,
                        help='覆盖率阈值，低于此值时测试失败')

    # 过滤选项
    parser.add_argument('-m', '--mark',
                        help='只运行带有特定标记的测试')
    parser.add_argument('-f', '--file',
                        help='运行特定的测试文件')

    # 性能选项
    parser.add_argument('-p', '--parallel', metavar='N',
                        help='并行运行测试(N为并行数或auto)')
    parser.add_argument('--benchmark', action='store_true',
                        help='运行性能测试')

    args = parser.parse_args()

    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # 运行测试
    if args.benchmark:
        returncode = run_benchmark(args)
    else:
        returncode = run_tests(args)

    # 输出覆盖率报告位置
    if args.coverage and returncode == 0:
        print("\n覆盖率报告已生成: htmlcov/index.html")

    return returncode


if __name__ == '__main__':
    sys.exit(main())
