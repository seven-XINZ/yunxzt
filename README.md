安装
配置完成 LangBot 主程序后使用管理员账号向机器人发送命令即可安装：

!plugin get https://github.com/seven-XINZ/yunxzt

# 运行状态插件

LangBot 的系统资源查询插件，美观展示系统运行状态。

## 功能

- 查询系统基本信息（操作系统、主机名、运行时间等）
- 显示 CPU 使用情况、温度和负载
- 显示内存和交换分区使用情况
- 显示磁盘使用情况和文件系统信息
- 显示网络接口信息和实时网络速率
- 美观的进度条和格式化输出

## 安装

1. 将此插件目录放入 LangBot 的 `plugins` 目录中
2. 安装依赖：`pip install -r requirements.txt`
3. 重启 LangBot

## 使用

在私聊或群聊中发送 `运行状态` 即可获取系统资源使用情况的详细报告。

## 配置

插件内部包含以下配置项，可以根据需要进行修改：

```python
CONFIG = {
    "delMsgTime": 90,      # 消息保留时间(秒)
    "progressBarLength": 15,   # 进度条长度
    "refreshInterval": None,   # 刷新间隔(秒)，设为None表示不自动刷新
    "maxDisksToShow": 10,      # 最多显示几个磁盘，设置为较大的数值以显示所有磁盘
    "preferredInterfaces": ['enp3s0', 'enp4s0', 'eth0', 'eth1', 'wlan0', 'wlan1'], # 优先选择的网卡
    "hideNetworkAddresses": True,  # 是否隐藏IP地址和MAC地址
    "maxNetworksToShow": 15,   # 最多显示几个网卡
    "showAllNetworks": True    # 是否显示所有网卡
}


## 使用说明

1. 创建一个名为 `SystemStatus` 的目录，将上述文件放入其中
2. 将此目录放入 LangBot 的 `plugins` 目录中
3. 安装依赖：`pip install -r requirements.txt`
4. 重启 LangBot
5. 在私聊或群聊中发送 `运行状态` 命令即可查看系统资源使用情况

## 注意事项

1. 此插件需要 `psutil` 库来获取系统信息，请确保已正确安装
2. 某些系统信息（如 CPU 温度）可能在某些平台上不可用
3. 网络速率计算基于两次查询之间的差值，首次查询可能显示为 0
4. 插件已经处理了各种可能的错误情况，即使某些信息无法获取，也会尽量显示其他可用信息

此插件完全遵循 LangBot 的插件开发规范，并保留了原插件的所有功能和美观的格式化输出。
