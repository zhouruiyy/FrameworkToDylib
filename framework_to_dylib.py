import os
import subprocess

def convert_xcframework_to_dylib(xcframework_path, lib_name, output_path):
  # Create the output directory if it doesn't exist
  if not os.path.exists(output_path):
    os.makedirs(output_path, mode=0o755)

  # 动态查找动态库文件
  framework_path = os.path.join(xcframework_path, "macos-arm64_x86_64", lib_name + ".framework")
  lib_path = None
  
  # 尝试多种可能的路径
  possible_paths = [
    os.path.join(framework_path, "Versions", "A", lib_name),
    os.path.join(framework_path, "Versions", "Current", lib_name),
    os.path.join(framework_path, "Versions", "B", lib_name),
    os.path.join(framework_path, lib_name)
  ]
  
  print(f"🔍 查找 {lib_name} 的动态库文件...")
  for path in possible_paths:
    if os.path.exists(path) and os.path.isfile(path):
      lib_path = path
      print(f"✅ 找到动态库: {path}")
      break
    else:
      print(f"❌ 路径不存在: {path}")
  
  if lib_path is None:
    print(f"❌ 找不到动态库文件: {lib_name}")
    return False
  
  out_lib_name = "lib" + lib_name + ".dylib"
  out_lib_path = os.path.join(output_path, out_lib_name)
  
  # Construct the command to convert xcframework to dylib
  command = "cp \"{0}\" \"{1}\"".format(lib_path, out_lib_path)
  print("copy: " + command)
  result = subprocess.call(command, shell=True)
  
  if result != 0:
    print(f"❌ 复制文件失败: {lib_name}")
    return False
  
  command = "install_name_tool -id @rpath/{0} {1}".format(out_lib_name, out_lib_path)
  subprocess.call(command, shell=True)

  # otool -L lib_path
  rpaths_output = subprocess.check_output(["otool", "-L", out_lib_path])
  rpaths = rpaths_output.decode("utf-8").split("\n")
  for rpath in rpaths:
    rpath_stripped = rpath.strip()
    if rpath_stripped.startswith("@rpath") and not rpath_stripped.endswith(".dylib"):
      # @rpath/Agoraffmpeg.framework/Versions/A/Agoraffmpeg (compatibility version 0.0.0, current version 0.0.0)
      rpath_stripped = rpath_stripped.split(" ")[0]
      dep_lib = rpath_stripped.split("/")[-1]
      command = "install_name_tool -change {0} @rpath/lib{1}.dylib {2}".format(rpath_stripped, dep_lib, out_lib_path)
      subprocess.call(command, shell=True)
  
  return True


def cp_framework_from_xcframework(xcframework_path, lib_name, output_path):
  # Create the output directory if it doesn't exist
  if not os.path.exists(output_path):
    os.makedirs(output_path, mode=0o755)

  lib_path = os.path.join(xcframework_path, "macos-arm64_x86_64", lib_name + ".framework")
  out_lib_path = os.path.join(output_path, lib_name + ".framework")
  # Construct the command to convert xcframework to dylib
  command = "cp -r {0} {1}".format(lib_path, out_lib_path)

  # Execute the command
  subprocess.call(command, shell=True)

def process_xcframeworks(xcframework_path, output_path):
    """处理指定路径下的所有xcframework文件"""
    # Read the contents of the directory
    for file_name in os.listdir(xcframework_path):
        # Check if the item is a file
        if not file_name.endswith(".xcframework") or os.path.isfile(os.path.join(xcframework_path, file_name)):
            continue
        lib_name = file_name.split(".")[0]
        convert_xcframework_to_dylib(os.path.join(xcframework_path, file_name), lib_name, output_path)

# 如果直接运行此脚本，使用默认路径
if __name__ == "__main__":
    # Path to the agora_sdk_mac folder
    xcframework_path = "/Users/zhourui/Rico/Agora/script/SDK/25.8.20/Agora_Native_SDK_for_Mac_FULL/libs"
    
    # Path to the output folder for dylib libraries
    output_path = "./agora_sdk"
    
    process_xcframeworks(xcframework_path, output_path)
