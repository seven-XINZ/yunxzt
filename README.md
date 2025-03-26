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
