#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agora SDK 快速启动脚本
提供交互式界面来选择和处理SDK文件
"""

import os
import sys
import subprocess
from pathlib import Path
from auto_process_sdk import AgoraSDKProcessor

def find_sdk_files():
    """查找可用的SDK文件"""
    sdk_dir = Path("SDK")
    if not sdk_dir.exists():
        return []
    
    sdk_files = []
    for version_dir in sdk_dir.iterdir():
        if version_dir.is_dir() and not version_dir.name.startswith('.'):
            zip_files = list(version_dir.glob("*.zip"))
            for zip_file in zip_files:
                if "Agora_Native_SDK_for_Mac" in zip_file.name:
                    sdk_files.append(zip_file)
    
    return sorted(sdk_files, key=lambda x: x.stat().st_mtime, reverse=True)

def display_sdk_files(sdk_files):
    """显示SDK文件列表"""
    print("📦 可用的SDK文件:")
    print("=" * 60)
    
    if not sdk_files:
        print("❌ 未找到可用的SDK文件")
        print("请确保SDK目录中有Agora_Native_SDK_for_Mac开头的zip文件")
        return
    
    for i, sdk_file in enumerate(sdk_files, 1):
        # 获取文件大小
        size_mb = sdk_file.stat().st_size / (1024 * 1024)
        # 获取修改时间
        mtime = sdk_file.stat().st_mtime
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        
        print(f"{i:2d}. {sdk_file.name}")
        print(f"    路径: {sdk_file}")
        print(f"    大小: {size_mb:.1f} MB")
        print(f"    时间: {mtime_str}")
        print()

def get_user_selection(sdk_files):
    """获取用户选择"""
    while True:
        try:
            choice = input(f"请选择要处理的SDK文件 (1-{len(sdk_files)}) 或输入 'q' 退出: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(sdk_files):
                return sdk_files[choice_num - 1]
            else:
                print(f"❌ 请输入 1-{len(sdk_files)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 再见!")
            sys.exit(0)

def confirm_processing(sdk_file):
    """确认是否开始处理"""
    print(f"\n🎯 您选择的SDK文件: {sdk_file.name}")
    print(f"📁 完整路径: {sdk_file}")
    
    # 检查文件大小
    size_mb = sdk_file.stat().st_size / (1024 * 1024)
    print(f"📊 文件大小: {size_mb:.1f} MB")
    
    # 估算处理时间
    estimated_time = "3-5分钟" if size_mb < 100 else "5-10分钟"
    print(f"⏱️  预计处理时间: {estimated_time}")
    
    print("\n⚠️  处理过程中会:")
    print("   - 在当前目录解压SDK")
    print("   - 转换所有framework为dylib")
    print("   - 生成两个压缩包（标准版和AED版）")
    
    while True:
        confirm = input("\n是否继续处理? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no', '']:
            return False
        else:
            print("请输入 y 或 n")

def process_sdk(sdk_file):
    """处理SDK文件"""
    print(f"\n🚀 开始处理SDK文件...")
    print(f"📦 文件: {sdk_file.name}")
    print("⏳ 请耐心等待，处理过程可能需要几分钟...")
    print("-" * 50)
    
    try:
        # 获取SDK文件所在的目录作为输出目录
        output_dir = sdk_file.parent
        processor = AgoraSDKProcessor(output_dir=output_dir)
        success = processor.process_sdk(str(sdk_file))
        
        if success:
            print("\n🎉 处理完成!")
            print("📁 请检查当前目录中生成的文件")
            print("📦 生成的压缩包已保存在当前目录中")
        else:
            print("\n❌ 处理失败，请检查错误信息")
            return False
            
    except Exception as e:
        print(f"\n💥 处理过程中发生错误: {e}")
        return False
    
    return True

def show_help():
    """显示帮助信息"""
    print("\n📖 帮助信息:")
    print("=" * 40)
    print("这个脚本可以自动化处理Agora Mac SDK，包括:")
    print("1. 解压SDK zip包到当前目录")
    print("2. 转换framework为dylib")
    print("3. 生成标准压缩包")
    print("4. 集成AED文件并生成AED版本压缩包")
    print("\n💡 使用提示:")
    print("- 确保有足够的磁盘空间")
    print("- 处理过程中请勿中断")
    print("- 生成的压缩包会自动包含版本号和时间戳")
    print("- 所有文件都会在当前目录中处理")

def main():
    """主函数"""
    print("🚀 Agora SDK 自动化处理工具")
    print("=" * 50)
    
    # 检查依赖
    if not os.path.exists("auto_process_sdk.py"):
        print("❌ 错误: 未找到 auto_process_sdk.py 脚本")
        print("请确保在正确的目录中运行此脚本")
        sys.exit(1)
    
    # 查找SDK文件
    sdk_files = find_sdk_files()
    
    while True:
        print("\n" + "=" * 50)
        print("请选择操作:")
        print("1. 查看可用的SDK文件")
        print("2. 处理SDK文件")
        print("3. 显示帮助信息")
        print("4. 退出")
        
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == "1":
                display_sdk_files(sdk_files)
                
            elif choice == "2":
                if not sdk_files:
                    print("❌ 没有可用的SDK文件")
                    continue
                
                display_sdk_files(sdk_files)
                selected_file = get_user_selection(sdk_files)
                
                if selected_file:
                    if confirm_processing(selected_file):
                        if process_sdk(selected_file):
                            print("\n✅ 处理成功完成!")
                            print("👋 脚本执行完毕，即将退出...")
                            sys.exit(0)
                        else:
                            print("\n❌ 处理失败，请检查错误信息")
                    else:
                        print("👋 取消处理")
                
            elif choice == "3":
                show_help()
                
            elif choice == "4":
                print("👋 再见!")
                break
                
            else:
                print("❌ 请输入 1-4 之间的数字")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
