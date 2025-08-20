# Agora SDK 自动化处理工具

这个工具可以自动化处理 Agora Mac SDK，包括解压、转换、压缩等所有步骤。

## 功能特性

- 🚀 全自动化处理流程
- 📅 自动创建日期目录
- 🔄 自动转换 Framework 为 dylib
- 📦 自动压缩生成最终包
- 🎯 支持 AED 文件集成
- 🏷️ 智能版本号识别

## 使用方法

### 方法1：交互式界面（推荐）

```bash
python quick_start.py
```

启动交互式界面，选择要处理的SDK文件，自动处理并生成压缩包。

### 方法2：命令行直接处理

```bash
python auto_process_sdk.py <SDK_ZIP文件路径>
```

### 示例

```bash
# 处理SDK文件
python auto_process_sdk.py "SDK/25.8.21/Agora_Native_SDK_for_Mac_rel.v4.4.30_25321_FULL_20250820_1052_846534.zip"

# 指定自定义输出目录
python auto_process_sdk.py "path/to/sdk.zip" --output-dir "custom_output"
```

## 处理流程

1. **解压SDK**: 将zip包解压到临时目录中
2. **查找Frameworks**: 自动扫描所有.framework文件
3. **转换为dylib**: 将所有framework转换为dylib，存储在输出目录下的临时agora_sdk目录
4. **生成标准压缩包**: 创建`agora_sdk_mac_v4.4.30_25321_FULL_20250820_1052_846534.zip`
5. **集成AED文件**: 将aed目录中的dylib文件添加到临时agora_sdk目录
6. **生成AED压缩包**: 创建`agora_sdk_mac_v4.4.30_25321_FULL_20250820_1052_846534-aed.zip`
7. **自动清理**: 删除所有临时目录和文件

## 目录结构

```
script/
├── auto_process_sdk.py          # 主自动化脚本
├── framework_to_dylib.py        # Framework转换脚本
├── check_dylib_dependencies.py  # dylib依赖检查脚本
├── quick_start.py               # 交互式启动脚本
├── SDK/                         # SDK存储目录
│   ├── 25.8.21/                # 版本目录
│   │   ├── *.zip               # 原始SDK文件
│   │   ├── agora_sdk_mac_*.zip # 标准压缩包
│   │   └── agora_sdk_mac_*-aed.zip # AED版本压缩包
│   └── ...
└── aed/                        # AED dylib文件目录
    └── libuap_aed.dylib
```

**注意**: 处理过程中会在输出目录下创建临时的 `agora_sdk` 目录，完成后自动清理。

## 依赖要求

- Python 3.6+
- macOS系统（需要install_name_tool等工具）
- 现有的framework_to_dylib_single.py脚本

## 注意事项

- 确保有足够的磁盘空间存储解压和转换后的文件
- 脚本会自动处理版本号识别，支持多种命名格式
- 如果转换过程中部分framework失败，脚本会继续处理其他文件
- 生成的压缩包会自动包含版本信息，避免文件名冲突
- 所有临时文件会在处理完成后自动清理
- 标准版本和AED版本会生成在不同大小的压缩包中

## 错误处理

脚本包含完善的错误处理机制：
- 文件不存在检查
- 解压失败处理
- 转换失败统计
- 压缩包创建验证

如果遇到问题，请检查：
1. SDK zip文件是否完整
2. 是否有足够的磁盘空间
3. Python环境和依赖是否正确安装
