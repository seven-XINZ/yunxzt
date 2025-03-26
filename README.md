安装
配置完成 LangBot 主程序后使用管理员账号向机器人发送命令即可安装：

!plugin get https://github.com/seven-XINZ/yunxzt

# 运行状态插件

LangBot 的系统资源查询插件，美观展示系统运行状态，仅限管理员使用。

## 功能

- 查询系统基本信息（操作系统、主机名、运行时间等）
- 显示 CPU 使用情况、温度和负载
- 显示内存和交换分区使用情况
- 显示磁盘使用情况和文件系统信息
- 显示网络接口信息和实时网络速率
- 美观的进度条和格式化输出
- 仅允许管理员使用此命令

## 安装

1. 将此插件目录放入 LangBot 的 `plugins` 目录中
2. 安装依赖：`pip install -r requirements.txt`
3. 配置管理员 ID（编辑 `config.json` 文件）
4. 重启 LangBot

## 使用

在私聊或群聊中发送 `运行状态` 即可获取系统资源使用情况的详细报告（仅限管理员）。

## 配置

首次运行插件后，会在插件目录下生成 `config.json` 文件，配置项说明：

```json
{
    "admin_ids": ["your_admin_id"],  // 管理员ID列表，请替换为您的管理员ID
    "progressBarLength": 15,   // 进度条长度
    "hideNetworkAddresses": true,  // 是否隐藏IP地址和MAC地址
    "maxDisksToShow": 10,      // 最多显示几个磁盘
    "maxNetworksToShow": 5     // 最多显示几个网卡
}

## 使用说明

1. 创建一个名为 `SystemStatus` 的目录，将上述文件放入其中
2. 将此目录放入 LangBot 的 `plugins` 目录中
3. 安装依赖：`pip install -r requirements.txt`
4. 配置管理员 ID：
   - 首次运行后，编辑生成的 `config.json` 文件
   - 将 `admin_ids` 数组中的 `"your_admin_id"` 替换为您的实际管理员 ID
5. 重启 LangBot
6. 在私聊或群聊中发送 `运行状态` 命令即可查看系统资源使用情况

## 特点

1. **管理员权限控制**：只有管理员才能使用此命令
2. **完整的系统信息**：包括 CPU、内存、磁盘和网络信息
3. **美观的格式化输出**：使用进度条和分隔线使输出更加美观
4. **信息安全保护**：可以隐藏敏感的 IP 地址和 MAC 地址
5. **可配置的显示选项**：可以自定义显示的磁盘和网卡数量

这个插件完全遵循 LangBot 的插件开发规范，并提供了安全的管理员权限控制功能。
