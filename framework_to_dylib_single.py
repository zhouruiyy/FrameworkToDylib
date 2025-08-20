import os
import subprocess
import sys

def convert_framework_to_dylib(framework_path, output_path):
    """
    将单个Framework转换为dylib文件
    
    Args:
        framework_path: Framework的路径，例如 "/path/to/MyFramework.framework"
        output_path: 输出dylib文件的目录路径
    """
    # 检查Framework路径是否存在
    if not os.path.exists(framework_path):
        print(f"错误: Framework路径不存在: {framework_path}")
        return False
    
    # 检查是否为Framework目录
    if not framework_path.endswith(".framework"):
        print(f"错误: 路径不是Framework: {framework_path}")
        return False
    
    # 创建输出目录
    if not os.path.exists(output_path):
        os.makedirs(output_path, mode=0o755)
    
    # 获取Framework名称
    framework_name = os.path.basename(framework_path).replace(".framework", "")
    
    # 查找Framework中的动态库文件
    # 通常在Versions/Current/目录下
    possible_lib_paths = [
        os.path.join(framework_path, "Versions", "Current", framework_name),
        os.path.join(framework_path, framework_name)
    ]
    
    lib_path = None
    for path in possible_lib_paths:
        if os.path.exists(path):
            lib_path = path
            break
    
    if lib_path is None:
        print(f"错误: 在Framework中找不到动态库文件: {framework_path}")
        return False
    
    # 输出dylib文件名和路径
    out_lib_name = f"lib{framework_name}.dylib"
    out_lib_path = os.path.join(output_path, out_lib_name)
    
    # 复制动态库文件
    command = f'cp "{lib_path}" "{out_lib_path}"'
    print(f"复制文件: {command}")
    result = subprocess.call(command, shell=True)
    if result != 0:
        print(f"错误: 复制文件失败")
        return False
    
    # 修改动态库的ID
    command = f'install_name_tool -id @rpath/{out_lib_name} "{out_lib_path}"'
    print(f"修改ID: {command}")
    result = subprocess.call(command, shell=True)
    if result != 0:
        print(f"错误: 修改动态库ID失败")
        return False
    
    # 处理依赖的@rpath引用
    try:
        rpaths_output = subprocess.check_output(["otool", "-L", out_lib_path])
        rpaths = rpaths_output.decode("utf-8").split("\n")
        
        for rpath in rpaths:
            rpath_stripped = rpath.strip()
            if rpath_stripped.startswith("@rpath") and not rpath_stripped.endswith(".dylib"):
                # 处理类似 @rpath/SomeFramework.framework/Versions/A/SomeFramework 的引用
                rpath_stripped = rpath_stripped.split(" ")[0]
                dep_lib = rpath_stripped.split("/")[-1]
                
                # 跳过自身的引用
                if dep_lib == framework_name:
                    continue
                    
                command = f'install_name_tool -change "{rpath_stripped}" @rpath/lib{dep_lib}.dylib "{out_lib_path}"'
                print(f"修改依赖: {command}")
                subprocess.call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"警告: 获取依赖信息失败: {e}")
    
    print(f"成功转换Framework为dylib: {out_lib_path}")
    return True

def main():
    if len(sys.argv) != 3:
        print("用法: python framework_to_dylib_single.py <framework_path> <output_path>")
        print("示例: python framework_to_dylib_single.py /path/to/MyFramework.framework ./output")
        sys.exit(1)
    
    framework_path = sys.argv[1]
    output_path = sys.argv[2]
    
    success = convert_framework_to_dylib(framework_path, output_path)
    if success:
        print("转换完成!")
    else:
        print("转换失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
