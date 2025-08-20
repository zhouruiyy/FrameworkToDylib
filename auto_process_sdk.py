#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agora SDK 自动化处理模块
提供SDK解压、framework转换、压缩包生成等功能
"""

import os
import sys
import zipfile
import subprocess
import shutil
from pathlib import Path
import argparse

class AgoraSDKProcessor:
    """Agora SDK 处理器"""
    
    def __init__(self, sdk_dir="agora_sdk", aed_dir="SDK/aed", output_dir=None):
        # 如果没有指定输出目录，则使用当前工作目录
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        # 在输出目录下创建临时的sdk目录
        self.sdk_dir = self.output_dir / sdk_dir
        self.aed_dir = Path(aed_dir)
        self.temp_dir = Path("temp_sdk")
        # 版本信息
        self.version_suffix = ""
        
    def process_sdk(self, sdk_zip_path):
        """
        处理SDK文件
        
        Args:
            sdk_zip_path: SDK zip文件的路径
            
        Returns:
            bool: 处理是否成功
        """
        try:
            print(f"🚀 开始处理SDK: {sdk_zip_path}")
            
            # 解析原zip文件名，提取版本信息
            self._parse_zip_filename(sdk_zip_path)
            
            # 1. 解压SDK
            if not self._extract_sdk(sdk_zip_path):
                return False
            
            # 2. 转换framework为dylib
            if not self._convert_frameworks():
                return False
            
            # 3. 生成标准压缩包
            if not self._create_standard_zip():
                return False
            
            # 4. 生成AED版本压缩包
            if not self._create_aed_zip():
                return False
            
            # 5. 清理临时文件
            self._cleanup()
            
            print("✅ SDK处理完成!")
            return True
            
        except Exception as e:
            print(f"❌ 处理SDK时发生错误: {e}")
            self._cleanup()
            return False
    
    def _parse_zip_filename(self, sdk_zip_path):
        """解析zip文件名，提取版本信息"""
        try:
            zip_filename = Path(sdk_zip_path).name
            
            # 查找v4.4.30的位置
            version_start = zip_filename.find("v4.4.30")
            if version_start != -1:
                # 提取v4.4.30后面的所有字符，但去掉.zip扩展名
                version_part = zip_filename[version_start:]
                if version_part.endswith('.zip'):
                    self.version_suffix = version_part[:-4]  # 去掉.zip
                else:
                    self.version_suffix = version_part
                print(f"📋 提取版本信息: {self.version_suffix}")
            else:
                # 如果没有找到v4.4.30，使用默认后缀
                self.version_suffix = "unknown"
                print(f"⚠️  未找到版本信息，使用默认后缀: {self.version_suffix}")
                
        except Exception as e:
            print(f"⚠️  解析文件名失败: {e}")
            # 使用默认后缀作为后备
            self.version_suffix = "unknown"
    
    def _extract_sdk(self, sdk_zip_path):
        """解压SDK文件"""
        try:
            print("📦 解压SDK文件...")
            
            # 清理临时目录
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            
            # 创建临时目录
            self.temp_dir.mkdir(exist_ok=True)
            
            # 解压zip文件
            with zipfile.ZipFile(sdk_zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            print("✅ SDK解压完成")
            return True
            
        except Exception as e:
            print(f"❌ 解压SDK失败: {e}")
            return False
    
    def _convert_frameworks(self):
        """转换framework为dylib"""
        try:
            print("🔄 转换framework为dylib...")
            
            # 查找所有framework文件
            framework_files = []
            for root, dirs, files in os.walk(self.temp_dir):
                for dir_name in dirs:
                    if dir_name.endswith('.framework'):
                        framework_path = os.path.join(root, dir_name)
                        framework_files.append(framework_path)
            
            if not framework_files:
                print("⚠️  未找到framework文件")
                return True
            
            print(f"📁 找到 {len(framework_files)} 个framework文件")
            
            # 创建输出目录
            self.sdk_dir.mkdir(exist_ok=True)
            
            # 转换每个framework
            for framework_path in framework_files:
                lib_name = os.path.basename(framework_path).replace('.framework', '')
                print(f"  🔄 转换: {lib_name}")
                
                if not self._convert_single_framework(framework_path, lib_name):
                    print(f"  ❌ 转换失败: {lib_name}")
                    return False
            
            print("✅ Framework转换完成")
            return True
            
        except Exception as e:
            print(f"❌ 转换framework失败: {e}")
            return False
    
    def _convert_single_framework(self, framework_path, lib_name):
        """转换单个framework为dylib"""
        try:
            # 查找Framework中的动态库文件
            possible_paths = [
                os.path.join(framework_path, "Versions", "A", lib_name),
                os.path.join(framework_path, "Versions", "Current", lib_name),
                os.path.join(framework_path, "Versions", "B", lib_name),
                os.path.join(framework_path, lib_name)
            ]
            
            lib_path = None
            for path in possible_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    lib_path = path
                    break
            
            if lib_path is None:
                print(f"    ❌ 找不到动态库文件: {lib_name}")
                return False
            
            # 输出dylib文件名和路径
            out_lib_name = f"lib{lib_name}.dylib"
            out_lib_path = os.path.join(self.sdk_dir, out_lib_name)
            
            # 复制动态库文件
            shutil.copy2(lib_path, out_lib_path)
            
            # 修改动态库的ID
            command = f'install_name_tool -id @rpath/{out_lib_name} "{out_lib_path}"'
            subprocess.call(command, shell=True)
            
            # 处理依赖的@rpath引用
            try:
                rpaths_output = subprocess.check_output(["otool", "-L", out_lib_path])
                rpaths = rpaths_output.decode("utf-8").split("\n")
                
                for rpath in rpaths:
                    rpath_stripped = rpath.strip()
                    if rpath_stripped.startswith("@rpath") and not rpath_stripped.endswith(".dylib"):
                        rpath_stripped = rpath_stripped.split(" ")[0]
                        dep_lib = rpath_stripped.split("/")[-1]
                        
                        if dep_lib == lib_name:
                            continue
                            
                        command = f'install_name_tool -change "{rpath_stripped}" @rpath/lib{dep_lib}.dylib "{out_lib_path}"'
                        subprocess.call(command, shell=True)
            except subprocess.CalledProcessError:
                pass  # 忽略依赖处理错误
            
            return True
            
        except Exception as e:
            print(f"    ❌ 转换失败: {e}")
            return False
    
    def _create_standard_zip(self):
        """创建标准压缩包"""
        try:
            print("📦 创建标准压缩包...")
            
            # 生成文件名
            zip_name = f"agora_sdk_mac_{self.version_suffix}.zip"
            
            # 确保zip文件在指定的输出目录下创建
            zip_path = self.output_dir / zip_name
            print(f"📁 输出目录: {self.output_dir}")
            print(f"📁 zip文件将创建在: {zip_path.absolute()}")
            
            # 创建zip文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.sdk_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.sdk_dir)
                        zipf.write(file_path, arcname)
            
            print(f"✅ 标准压缩包创建完成: {zip_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建标准压缩包失败: {e}")
            return False
    
    def _create_aed_zip(self):
        """创建AED版本压缩包"""
        try:
            print("📦 创建AED版本压缩包...")
            
            # 检查AED目录
            if not self.aed_dir.exists():
                print("⚠️  AED目录不存在，跳过AED版本创建")
                return True
            
            # 直接将AED文件添加到现有的dylib目录中
            aed_files = list(self.aed_dir.glob("*.dylib"))
            if not aed_files:
                print("⚠️  AED目录中没有dylib文件，跳过AED版本创建")
                return True
            
            print(f"📁 集成 {len(aed_files)} 个AED文件到现有目录")
            for aed_file in aed_files:
                shutil.copy2(aed_file, self.sdk_dir)
            
            # 生成AED版本文件名
            zip_name = f"agora_sdk_mac_{self.version_suffix}-aed.zip"
            
            # 确保zip文件在指定的输出目录下创建
            zip_path = self.output_dir / zip_name
            print(f"📁 输出目录: {self.output_dir}")
            print(f"📁 AED zip文件将创建在: {zip_path.absolute()}")
            
            # 创建AED版本zip文件（从包含AED文件的现有目录创建）
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.sdk_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.sdk_dir)
                        zipf.write(file_path, arcname)
            
            print(f"✅ AED版本压缩包创建完成: {zip_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建AED版本压缩包失败: {e}")
            return False
    
    def _cleanup(self):
        """清理临时文件"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print("🧹 临时目录清理完成")
            
            if self.sdk_dir.exists():
                shutil.rmtree(self.sdk_dir)
                print("🧹 临时SDK目录清理完成")
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Agora SDK 自动化处理工具")
    parser.add_argument("sdk_zip", help="SDK zip文件路径")
    parser.add_argument("--sdk-dir", default="agora_sdk", help="输出SDK目录")
    parser.add_argument("--aed-dir", default="aed", help="AED文件目录")
    parser.add_argument("--output-dir", help="zip包输出目录")
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.sdk_zip):
        print(f"❌ 错误: SDK文件不存在: {args.sdk_zip}")
        sys.exit(1)
    
    # 创建处理器并处理
    processor = AgoraSDKProcessor(args.sdk_dir, args.aed_dir, args.output_dir)
    success = processor.process_sdk(args.sdk_zip)
    
    if success:
        print("🎉 处理成功完成!")
        sys.exit(0)
    else:
        print("❌ 处理失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
