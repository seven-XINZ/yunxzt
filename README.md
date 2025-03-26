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
