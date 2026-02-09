# coding: utf-8
"""
GUI测试运行器

提供便捷的GUI测试运行脚本。
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    gui_tests_dir = project_root / 'tests' / 'gui'

    print("=" * 60)
    print("KHQuant GUI测试运行器")
    print("=" * 60)

    # 检查pytest-qt是否安装
    print("\n1. 检查pytest-qt安装状态...")
    try:
        import pytestqt
        print(f"   ✓ pytest-qt已安装 (版本: {pytestqt.__version__})")
    except ImportError:
        print("   ✗ pytest-qt未安装")
        print("\n   请运行: pip install pytest-qt")
        return 1

    # 检查PyQt5是否安装
    print("\n2. 检查PyQt5安装状态...")
    try:
        import PyQt5
        print("   ✓ PyQt5已安装")
    except ImportError:
        print("   ✗ PyQt5未安装")
        print("\n   请运行: pip install PyQt5")
        return 1

    # 获取pytest路径
    pytest_exe = Path(sys.executable).parent / 'pytest.exe'
    if not pytest_exe.exists():
        pytest_exe = Path(sys.executable).parent / 'Scripts' / 'pytest.exe'

    if not pytest_exe.exists():
        print(f"\n   无法找到pytest可执行文件")
        print(f"   请确保pytest已安装")
        return 1

    print(f"\n   使用pytest: {pytest_exe}")

    # 测试选项
    print("\n" + "=" * 60)
    print("请选择测试选项:")
    print("  1. 运行所有GUI测试")
    print("  2. 运行GUIkhQuant测试")
    print("  3. 运行GUI数据下载测试")
    print("  4. 运行GUIDataViewer测试")
    print("  5. 运行回测结果窗口测试")
    print("  6. 运行设置对话框测试")
    print("  7. 运行测试并生成覆盖率报告")
    print("  8. 快速测试(跳过慢速测试)")
    print("  0. 退出")
    print("=" * 60)

    choice = input("\n请输入选项 (0-8): ").strip()

    # 构建pytest命令
    cmd = [str(pytest_exe), '-v']

    if choice == '1':
        # 所有GUI测试
        cmd.extend(['-m', 'gui'])
    elif choice == '2':
        # GUIkhQuant测试
        cmd.append(str(gui_tests_dir / 'test_GUIkhQuant.py'))
    elif choice == '3':
        # GUI数据下载测试
        cmd.append(str(gui_tests_dir / 'test_GUI.py'))
    elif choice == '4':
        # GUIDataViewer测试
        cmd.append(str(gui_tests_dir / 'test_GUIDataViewer.py'))
    elif choice == '5':
        # 回测结果窗口测试
        cmd.append(str(gui_tests_dir / 'test_backtest_result_window.py'))
    elif choice == '6':
        # 设置对话框测试
        cmd.append(str(gui_tests_dir / 'test_SettingsDialog.py'))
    elif choice == '7':
        # 生成覆盖率报告
        cmd.extend([
            str(gui_tests_dir),
            '--cov=GUIkhQuant',
            '--cov=GUI',
            '--cov=GUIDataViewer',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    elif choice == '8':
        # 快速测试
        cmd.extend(['-m', 'gui and not slow_gui'])
    elif choice == '0':
        print("\n退出测试运行器")
        return 0
    else:
        print(f"\n无效选项: {choice}")
        return 1

    # 运行测试
    success = run_command(cmd, f"GUI测试 (选项 {choice})")

    if success:
        print("\n" + "=" * 60)
        print("✓ 测试完成!")
        print("=" * 60)

        if choice == '7':
            # 显示覆盖率报告位置
            coverage_dir = project_root / 'htmlcov'
            if coverage_dir.exists():
                print(f"\n覆盖率报告: {coverage_dir / 'index.html'}")
                print(f"在浏览器中打开查看详细报告")
    else:
        print("\n" + "=" * 60)
        print("✗ 测试失败")
        print("=" * 60)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
