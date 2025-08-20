#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动化SDK处理脚本
"""

import os
import sys
from pathlib import Path

def test_script_import():
    """测试脚本导入"""
    try:
        from auto_process_sdk import AgoraSDKProcessor
        print("✅ 脚本导入成功")
        return True
    except ImportError as e:
        print(f"❌ 脚本导入失败: {e}")
        return False

def test_dependencies():
    """测试依赖脚本"""
    required_scripts = [
        "framework_to_dylib_single.py",
        "check_dylib_dependencies.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ 缺少依赖脚本: {missing_scripts}")
        return False
    else:
        print("✅ 所有依赖脚本都存在")
        return True

def test_directory_structure():
    """测试目录结构"""
    required_dirs = ["SDK", "aed"]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"⚠️  缺少目录: {missing_dirs}")
        print("   这些目录会在运行时自动创建")
    else:
        print("✅ 所有必需目录都存在")
    
    return True

def test_aed_files():
    """测试AED文件"""
    aed_dir = Path("aed")
    if aed_dir.exists():
        aed_files = list(aed_dir.glob("*.dylib"))
        if aed_files:
            print(f"✅ 找到 {len(aed_files)} 个AED文件")
            for file in aed_files:
                print(f"   - {file.name}")
        else:
            print("⚠️  AED目录中没有dylib文件")
    else:
        print("⚠️  AED目录不存在")
    
    return True

def test_sdk_files():
    """测试SDK文件"""
    sdk_dir = Path("SDK")
    if sdk_dir.exists():
        sdk_versions = [d for d in sdk_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if sdk_versions:
            print(f"✅ 找到 {len(sdk_versions)} 个SDK版本目录")
            for version_dir in sdk_versions:
                zip_files = list(version_dir.glob("*.zip"))
                if zip_files:
                    print(f"   - {version_dir.name}: {len(zip_files)} 个zip文件")
                    for zip_file in zip_files[:3]:  # 只显示前3个
                        print(f"     * {zip_file.name}")
                    if len(zip_files) > 3:
                        print(f"     ... 还有 {len(zip_files) - 3} 个文件")
                else:
                    print(f"   - {version_dir.name}: 无zip文件")
        else:
            print("⚠️  SDK目录中没有版本子目录")
    else:
        print("⚠️  SDK目录不存在")
    
    return True

def run_tests():
    """运行所有测试"""
    print("🧪 开始测试自动化SDK处理脚本...\n")
    
    tests = [
        ("脚本导入测试", test_script_import),
        ("依赖脚本测试", test_dependencies),
        ("目录结构测试", test_directory_structure),
        ("AED文件测试", test_aed_files),
        ("SDK文件测试", test_sdk_files),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过\n")
            else:
                print("❌ 测试失败\n")
        except Exception as e:
            print(f"💥 测试异常: {e}\n")
    
    print("📊 测试结果汇总")
    print("=" * 40)
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    if passed == total:
        print("🎉 所有测试通过！脚本可以正常使用。")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述问题。")
        return False

def show_usage_example():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("=" * 40)
    
    # 查找一个可用的SDK文件作为示例
    sdk_dir = Path("SDK")
    example_zip = None
    
    if sdk_dir.exists():
        for version_dir in sdk_dir.iterdir():
            if version_dir.is_dir():
                zip_files = list(version_dir.glob("*.zip"))
                if zip_files:
                    example_zip = zip_files[0]
                    break
    
    if example_zip:
        print(f"# 处理SDK文件")
        print(f"python auto_process_sdk.py \"{example_zip}\"")
        print()
        print(f"# 指定自定义目录")
        print(f"python auto_process_sdk.py \"{example_zip}\" --sdk-dir \"custom_sdk\" --aed-dir \"custom_aed\"")
    else:
        print("# 处理SDK文件")
        print("python auto_process_sdk.py \"path/to/your/sdk.zip\"")
        print()
        print("# 指定自定义目录")
        print("python auto_process_sdk.py \"path/to/your/sdk.zip\" --sdk-dir \"custom_sdk\" --aed-dir \"custom_aed\"")

if __name__ == "__main__":
    success = run_tests()
    
    if success:
        show_usage_example()
    else:
        print("\n🔧 请修复上述问题后重新运行测试。")
        sys.exit(1)
