#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
哈希验证功能演示脚本

演示如何使用update_manager中的哈希验证功能来验证下载的更新文件。
"""

import hashlib
import os
import sys


def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值

    Args:
        file_path: 文件路径

    Returns:
        str: SHA256哈希值（十六进制字符串）
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            # 分块读取文件以处理大文件（与update_manager中的实现一致）
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"计算文件哈希时出错: {str(e)}")
        return None


def create_version_info_with_checksum(file_path, version_info=None):
    """创建包含checksum的版本信息

    Args:
        file_path: 更新文件路径
        version_info: 现有的版本信息字典

    Returns:
        dict: 包含checksum的版本信息
    """
    if version_info is None:
        version_info = {}

    # 计算文件的SHA256哈希值
    file_hash = calculate_file_hash(file_path)
    if file_hash:
        version_info['checksum'] = file_hash
        print(f"文件哈希值: {file_hash}")
    else:
        print("无法计算文件哈希值")

    return version_info


def verify_file_integrity(file_path, expected_checksum):
    """验证文件完整性

    Args:
        file_path: 文件路径
        expected_checksum: 期望的SHA256哈希值

    Returns:
        bool: 验证是否通过
    """
    calculated_hash = calculate_file_hash(file_path)
    if calculated_hash is None:
        return False

    if calculated_hash == expected_checksum:
        print(f"[通过] 文件验证成功: {file_path}")
        print(f"  哈希值: {calculated_hash}")
        return True
    else:
        print(f"[失败] 文件验证失败: {file_path}")
        print(f"  期望哈希: {expected_checksum}")
        print(f"  实际哈希: {calculated_hash}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("更新文件哈希验证功能演示")
    print("=" * 60)
    print()

    # 演示1: 计算文件哈希值
    print("演示1: 计算文件哈希值")
    print("-" * 40)
    test_file = __file__  # 使用当前脚本作为测试文件
    file_hash = calculate_file_hash(test_file)
    if file_hash:
        print(f"文件: {os.path.basename(test_file)}")
        print(f"SHA256: {file_hash}")
    print()

    # 演示2: 创建版本信息
    print("演示2: 创建包含checksum的版本信息")
    print("-" * 40)
    version_info = {
        'version': '2.1.5',
        'force_update': False,
        'filename': 'khquant_2.1.5.exe',
        'description': '新版本功能更新'
    }
    version_info = create_version_info_with_checksum(test_file, version_info)
    print(f"版本信息: {version_info}")
    print()

    # 演示3: 验证文件完整性
    print("演示3: 验证文件完整性")
    print("-" * 40)
    expected_hash = file_hash
    is_valid = verify_file_integrity(test_file, expected_hash)
    print()

    # 演示4: 模拟哈希不匹配的情况
    print("演示4: 模拟哈希不匹配的情况")
    print("-" * 40)
    fake_hash = "0" * 64  # 64个0
    is_valid = verify_file_integrity(test_file, fake_hash)
    print()

    print("=" * 60)
    print("演示完成")
    print("=" * 60)
    print()
    print("使用说明:")
    print("1. 在发布更新时，计算更新文件的SHA256哈希值")
    print("2. 将哈希值添加到版本信息的checksum字段")
    print("3. update_manager会在下载后自动验证文件完整性")
    print("4. 如果哈希不匹配，下载将被拒绝并清理临时文件")
    print()
    print("示例版本信息 (version.json):")
    print('{')
    print('  "version": "2.1.5",')
    print('  "force_update": false,')
    print('  "checksum": "' + file_hash + '",')
    print('  "filename": "khquant_2.1.5.exe",')
    print('  "description": "新版本功能更新"')
    print('}')


if __name__ == '__main__':
    main()
