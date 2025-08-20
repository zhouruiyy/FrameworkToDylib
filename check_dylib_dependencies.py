import os
import subprocess
import sys

def check_dylib_dependencies(dylib_path):
    """
    查看dylib文件的依赖关系
    
    Args:
        dylib_path: dylib文件的路径
    """
    # 检查文件是否存在
    if not os.path.exists(dylib_path):
        print(f"错误: 文件不存在: {dylib_path}")
        return False
    
    # 检查是否为dylib文件
    if not dylib_path.endswith(".dylib"):
        print(f"警告: 文件不是dylib格式: {dylib_path}")
    
    print(f"=== 分析dylib依赖: {dylib_path} ===\n")
    
    try:
        # 使用otool -L查看依赖
        rpaths_output = subprocess.check_output(["otool", "-L", dylib_path])
        dependencies = rpaths_output.decode("utf-8").split("\n")
        
        print("依赖列表:")
        print("-" * 50)
        
        for i, dep in enumerate(dependencies):
            dep_stripped = dep.strip()
            if dep_stripped and not dep_stripped.startswith(dylib_path):
                # 跳过文件自身的引用
                if i == 0:
                    print(f"自身ID: {dep_stripped}")
                else:
                    print(f"依赖 {i}: {dep_stripped}")
        
        print("\n" + "=" * 50)
        
        # 使用otool -D查看动态库ID
        try:
            id_output = subprocess.check_output(["otool", "-D", dylib_path])
            print("动态库ID:")
            print("-" * 20)
            print(id_output.decode("utf-8").strip())
        except subprocess.CalledProcessError:
            print("无法获取动态库ID")
        
        print("\n" + "=" * 50)
        
        # 使用file命令查看文件信息
        try:
            file_output = subprocess.check_output(["file", dylib_path])
            print("文件信息:")
            print("-" * 20)
            print(file_output.decode("utf-8").strip())
        except subprocess.CalledProcessError:
            print("无法获取文件信息")
        
        print("\n" + "=" * 50)
        
        # 使用lipo -info查看架构信息
        try:
            lipo_output = subprocess.check_output(["lipo", "-info", dylib_path])
            print("架构信息:")
            print("-" * 20)
            print(lipo_output.decode("utf-8").strip())
        except subprocess.CalledProcessError:
            print("无法获取架构信息")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法分析dylib文件: {e}")
        return False

def check_multiple_dylibs(directory_path):
    """
    批量检查目录中所有dylib文件的依赖
    
    Args:
        directory_path: 包含dylib文件的目录路径
    """
    if not os.path.exists(directory_path):
        print(f"错误: 目录不存在: {directory_path}")
        return False
    
    if not os.path.isdir(directory_path):
        print(f"错误: 路径不是目录: {directory_path}")
        return False
    
    dylib_files = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".dylib"):
            dylib_files.append(os.path.join(directory_path, file_name))
    
    if not dylib_files:
        print(f"在目录中没有找到dylib文件: {directory_path}")
        return False
    
    print(f"找到 {len(dylib_files)} 个dylib文件\n")
    
    for dylib_file in dylib_files:
        print(f"\n{'='*60}")
        check_dylib_dependencies(dylib_file)
        print(f"{'='*60}\n")

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  查看单个dylib: python check_dylib_dependencies.py <dylib_path>")
        print("  批量查看目录: python check_dylib_dependencies.py -d <directory_path>")
        print("\n示例:")
        print("  python check_dylib_dependencies.py ./libAgoraRtcKit.dylib")
        print("  python check_dylib_dependencies.py -d ./agora_sdk")
        sys.exit(1)
    
    if sys.argv[1] == "-d" and len(sys.argv) == 3:
        # 批量检查目录
        directory_path = sys.argv[2]
        check_multiple_dylibs(directory_path)
    elif len(sys.argv) == 2:
        # 检查单个文件
        dylib_path = sys.argv[1]
        check_dylib_dependencies(dylib_path)
    else:
        print("参数错误，请检查用法")
        sys.exit(1)

if __name__ == "__main__":
    main()
