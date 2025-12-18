#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
开发版构建验证脚本
"""

import sys
import os
from datetime import datetime

def verify_build():
    """验证开发版构建"""
    print("====================================")
    print("    开发版构建验证")
    print("====================================\n")

    # 1. 验证版本信息
    try:
        from version import get_version_info
        version_info = get_version_info()
        print(f"[版本] 当前版本: {version_info['version']}")
        print(f"[版本] 构建日期: {version_info['build_date']}")
        print(f"[版本] 更新通道: {version_info['channel']}")

        if version_info['channel'] != 'dev':
            print("[错误] 版本通道未设置为dev")
            return False
        if 'dev' not in version_info['version']:
            print("[错误] 版本号未包含dev标识")
            return False
    except Exception as e:
        print(f"[错误] 版本模块验证失败: {e}")
        return False

    # 2. 验证启动脚本
    print("\n[文件] 验证启动脚本...")
    scripts = ['run_dev.bat', 'run_dev.py']
    for script in scripts:
        if os.path.exists(script):
            print(f"[OK] {script}")
        else:
            print(f"[缺失] {script}")
            return False

    # 3. 验证主程序
    print("\n[主程序] 验证核心模块...")
    try:
        import GUIkhQuant
        print("[OK] GUIkhQuant.py")
    except Exception as e:
        print(f"[错误] 主程序模块导入失败: {e}")
        return False

    # 4. 验证配置文件
    print("\n[配置] 验证配置文件...")
    if os.path.exists('requirements.txt'):
        print("[OK] requirements.txt")
    else:
        print("[警告] requirements.txt不存在")

    # 5. 构建总结
    print("\n====================================")
    print("    构建验证完成")
    print("====================================")
    print("\n开发版构建信息:")
    print(f"- 版本号: {version_info['version']}")
    print(f"- 构建日期: {version_info['build_date']}")
    print(f"- 更新通道: {version_info['channel']}")
    print("\n可用的启动方式:")
    print("1. 运行 run_dev.bat (Windows批处理)")
    print("2. 运行 python run_dev.py (Python脚本)")
    print("\n验证状态: 成功 ✓")

    return True

if __name__ == "__main__":
    success = verify_build()
    sys.exit(0 if success else 1)