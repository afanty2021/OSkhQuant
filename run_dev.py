#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
看海量化交易系统 - 开发版启动器
Version: 2.1.5-dev
Build Date: 2025-12-13
"""

import sys
import os
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """检查运行环境"""
    print("====================================")
    print("   看海量化交易系统 - 开发版")
    print("   Version: 2.1.5-dev")
    print(f"   Build Date: 2025-12-13")
    print("====================================\n")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("[错误] 需要Python 3.7或更高版本")
        print(f"当前版本: Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False

    print(f"[信息] Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查核心依赖包
    required_packages = {
        'PyQt5': 'GUI框架',
        'pandas': '数据处理',
        'numpy': '数值计算',
        'matplotlib': '图表绘制'
    }

    missing_packages = []
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"[OK] {package} - {description}")
        except ImportError:
            print(f"[缺失] {package} - {description}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n[警告] 缺失以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    # 检查xtquant
    try:
        import xtquant
        print("[OK] xtquant - MiniQMT数据接口")
    except ImportError:
        print("[警告] xtquant - MiniQMT数据接口未安装")
        print("提示: 请确保已安装MiniQMT客户端")

    return True

def set_dev_environment():
    """设置开发环境变量"""
    os.environ['KHQUANT_DEV'] = '1'
    os.environ['KHQUANT_VERSION'] = '2.1.5-dev'
    os.environ['KHQUANT_CHANNEL'] = 'dev'
    print("\n[信息] 开发环境变量已设置")

def main():
    """主函数"""
    try:
        # 检查环境
        if not check_environment():
            input("\n按回车键退出...")
            return 1

        # 设置开发环境
        set_dev_environment()

        print("\n[信息] 正在启动看海量化交易系统开发版...")
        print(f"[信息] 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 导入并启动主程序
        from GUIkhQuant import main
        main()

    except KeyboardInterrupt:
        print("\n[信息] 用户中断，程序退出")
        return 0
    except Exception as e:
        print(f"\n[错误] 程序运行异常: {str(e)}")
        print("\n错误详情:")
        traceback.print_exc()
        input("\n按回车键退出...")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())