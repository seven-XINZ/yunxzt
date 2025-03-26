from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
import os
import platform
import time
import psutil
import datetime
import socket
import re
import json
from typing import Dict, List, Optional, Any, Union

"""
运行状态 - LangBot 插件
查询系统资源使用情况并美观展示，只允许管理员使用
"""

# 配置项
CONFIG = {
    "admin_ids": ["your_admin_id"],  # 管理员ID列表，请替换为您的管理员ID
    "progressBarLength": 15,   # 进度条长度
    "hideNetworkAddresses": True,  # 是否隐藏IP地址和MAC地址
    "maxDisksToShow": 10,      # 最多显示几个磁盘
    "maxNetworksToShow": 5,    # 最多显示几个网卡
}

# 注册插件
@register(name="SystemStatus", description="查询系统资源使用情况，只允许管理员使用", version="1.0.0", author="LangBot")
class SystemStatusPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.host = host
        self.logger = host.logger
        self.logger.info("运行状态插件已加载")
        
        # 加载配置
        self._load_config()
        
        # 初始化网络历史数据
        self.network_history = {}
        self.last_update_time = time.time()

    # 异步初始化
    async def initialize(self):
        pass

    # 加载配置
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    CONFIG.update(loaded_config)
                    self.logger.info("已加载配置文件")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
        else:
            # 创建默认配置文件
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(CONFIG, f, indent=4, ensure_ascii=False)
                    self.logger.info("已创建默认配置文件")
            except Exception as e:
                self.logger.error(f"创建配置文件失败: {e}")

    # 检查用户是否为管理员
    def _is_admin(self, user_id: str) -> bool:
        return user_id in CONFIG["admin_ids"]

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def on_person_message(self, ctx: EventContext):
        message = ctx.event.text_message
        sender_id = ctx.event.sender_id
        
        if message == "运行状态":
            # 检查是否为管理员
            if not self._is_admin(sender_id):
                self.logger.info(f"非管理员用户 {sender_id} 尝试查看系统运行状态，已拒绝")
                ctx.add_return("reply", ["抱歉，只有管理员才能查看系统运行状态"])
                ctx.prevent_default()
                return
                
            self.logger.info(f"管理员 {sender_id} 请求查看系统运行状态")
            
            # 获取系统信息
            system_info = await self.get_system_info()
            
            # 回复消息
            ctx.add_return("reply", [system_info])
            
            # 阻止默认行为
            ctx.prevent_default()
            return

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def on_group_message(self, ctx: EventContext):
        message = ctx.event.text_message
        sender_id = ctx.event.sender_id
        group_id = ctx.event.group_id
        
        if message == "运行状态":
            # 检查是否为管理员
            if not self._is_admin(sender_id):
                self.logger.info(f"非管理员用户 {sender_id} 在群 {group_id} 尝试查看系统运行状态，已拒绝")
                ctx.add_return("reply", ["抱歉，只有管理员才能查看系统运行状态"])
                ctx.prevent_default()
                return
                
            self.logger.info(f"管理员 {sender_id} 在群 {group_id} 请求查看系统运行状态")
            
            # 获取系统信息
            system_info = await self.get_system_info()
            
            # 回复消息
            ctx.add_return("reply", [system_info])
            
            # 阻止默认行为
            ctx.prevent_default()
            return

    # 获取系统信息
    async def get_system_info(self) -> str:
        try:
            # 获取各项系统信息
            uptime_info = self.get_uptime()
            cpu_info = self.get_cpu_info()
            memory_info = self.get_memory_info()
            disk_info = self.get_disk_info()
            load_info = self.get_load_info()
            network_info = self.get_all_network_info()
            
            # 构建磁盘信息部分
            disk_section = f"{self.format_separator('💽 磁盘信息')}\n"
            
            if not disk_info:
                disk_section += "│ 未能获取磁盘信息\n"
            else:
                # 限制显示的磁盘数量
                disks_to_show = disk_info[:CONFIG["maxDisksToShow"]]
                
                for i, disk in enumerate(disks_to_show):
                    if i > 0:
                        disk_section += "│\n"  # 磁盘之间添加空行
                    
                    disk_section += f"│ 挂载点: {disk['mount']}\n"
                    disk_section += f"│ 文件系统: {disk['fs']}\n"
                    disk_section += f"│ 类型: {disk['type']}\n"
                    disk_section += f"│ 总空间: {disk['total']}\n"
                    disk_section += f"│ 已用空间: {disk['used']} {self.format_progress_bar(disk['percent'])}\n"
                    disk_section += f"│ 可用空间: {disk['available']}\n"
                
                # 如果有更多磁盘未显示，添加提示
                if len(disk_info) > CONFIG["maxDisksToShow"]:
                    disk_section += f"│\n│ (还有 {len(disk_info) - CONFIG['maxDisksToShow']} 个磁盘未显示)\n"
            
            # 构建网络信息部分
            network_section = f"{self.format_separator('🌐 网络信息')}\n"
            
            if not network_info:
                network_section += "│ 未能获取网络信息\n"
            else:
                # 按照物理接口优先排序
                sorted_networks = sorted(
                    network_info,
                    key=lambda x: (
                        self.is_virtual_interface(x['interface']),  # 物理接口优先
                        not x['status'].startswith('已连接'),  # 已连接的优先
                        x['interface']  # 最后按名称排序
                    )
                )
                
                # 限制显示的网卡数量
                networks_to_show = sorted_networks[:CONFIG["maxNetworksToShow"]]
                
                for i, network in enumerate(networks_to_show):
                    if i > 0:
                        network_section += "│\n"  # 网卡之间添加空行
                    
                    network_section += f"│ 网卡名称: {network['interface']} ({network['type']})\n"
                    network_section += f"│ IP地址: {self.hide_address(network['ip'], 'ip')}\n"
                    network_section += f"│ MAC地址: {self.hide_address(network['mac'], 'mac')}\n"
                    network_section += f"│ 下载速度: {network['rx']}/s (总计: {network['rx_total']})\n"
                    network_section += f"│ 上传速度: {network['tx']}/s (总计: {network['tx_total']})\n"
                    network_section += f"│ 连接状态: {network['status']}\n"
                
                # 如果有更多网卡未显示，添加提示
                if len(sorted_networks) > CONFIG["maxNetworksToShow"]:
                    network_section += f"│\n│ (还有 {len(sorted_networks) - CONFIG['maxNetworksToShow']} 个网卡未显示)\n"
            
            # 构建完整信息
            info = f"""
{self.format_separator('🖥️ 系统信息')}
│
│ 运行时间: {uptime_info['formatted']}
│ 版本: {platform.python_version()}
│ 操作系统: {platform.system()} {platform.release()}
│ 主机名: {socket.gethostname()}
│ 
{self.format_separator('📊 系统负载')}
│ 1分钟负载: {load_info['avg1']} {self.get_load_status(load_info['avg1'], load_info['safe_load'])}
│ 5分钟负载: {load_info['avg5']} {self.get_load_status(load_info['avg5'], load_info['safe_load'])}
│ 15分钟负载: {load_info['avg15']} {self.get_load_status(load_info['avg15'], load_info['safe_load'])}
│ CPU核心数: {load_info['max_load']}
│ 安全负载: {load_info['safe_load']}
│ 
{self.format_separator('🔥 CPU信息')}
│ CPU型号: {cpu_info['model']}
│ 核心/线程: {cpu_info['cores']}核 / {cpu_info['threads']}线程
│ 主频: {cpu_info['speed']}
│ CPU使用率: {cpu_info['usage']}
│ CPU温度: {cpu_info['temp']}
│ 进程: {cpu_info['processes']['active']}活动 / {cpu_info['processes']['total']}总数
│ 
{self.format_separator('💾 内存信息')}
│ 总内存: {memory_info['total']}
│ 已用内存: {memory_info['used']} {self.format_progress_bar(memory_info['percent'])}
│ 可用内存: {memory_info['free']}
│ SWAP: {memory_info['swap_used']}/{memory_info['swap_total']}
│ 
{disk_section}
{network_section}
{self.format_section_end()}
            """.strip()
            
            return info
            
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return "⚠️ 系统状态获取失败，请查看日志"

    # 美化工具函数: 进度条生成
    def format_progress_bar(self, percent: float, length: int = None) -> str:
        if length is None:
            length = CONFIG["progressBarLength"]
        
        filled = round(percent / 100 * length)
        return f"[{'■' * filled}{'□' * (length - filled)}] {percent:.1f}%"

    # 美化工具函数: 分隔线生成
    def format_separator(self, text: str) -> str:
        line = '─' * (28 - len(text))
        return f"┌── {text} {line}"

    # 美化工具函数: 结束线生成
    def format_section_end(self) -> str:
        return '└' + '─' * 32

    # 美化工具函数: 格式化字节为人类可读格式
    def format_bytes(self, bytes_value: int, decimals: int = 1) -> str:
        if bytes_value == 0:
            return '0 Bytes'
        
        k = 1024
        sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
        i = int(math.floor(math.log(bytes_value, k)))
        
        return f"{(bytes_value / (k ** i)):.{decimals}f} {sizes[i]}"

    # 美化工具函数: 格式化时间
    def format_uptime(self, seconds: int) -> str:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        result = ''
        if days > 0:
            result += f"{days}天 "
        if hours > 0 or days > 0:
            result += f"{hours}小时 "
        result += f"{minutes}分钟"
        
        return result

    # 美化工具函数: 格式化CPU速度
    def format_cpu_speed(self, speed_mhz: float) -> str:
        if not speed_mhz:
            return 'N/A'
        
        # 如果速度大于1000MHz，转换为GHz
        return f"{(speed_mhz / 1000):.1f} GHz" if speed_mhz >= 1000 else f"{speed_mhz} MHz"

    # 美化工具函数: 隐藏敏感信息
    def hide_address(self, address: str, type_: str = 'ip') -> str:
        if CONFIG["hideNetworkAddresses"]:
            if type_ == 'ip':
                if not address or address == 'N/A':
                    return 'N/A'
                # 隐藏IP地址的最后一段
                return re.sub(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', r'\1.\2.\3.***', address)
            elif type_ == 'mac':
                if not address or address == 'N/A':
                    return 'N/A'
                # 隐藏MAC地址的后半部分
                return re.sub(r'([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}):(.*)', r'\1:****', address, flags=re.I)
        return address

    # 获取CPU信息
    def get_cpu_info(self) -> dict:
        try:
            # 获取CPU信息
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_count_physical = psutil.cpu_count(logical=False) or 1
            cpu_count_logical = psutil.cpu_count() or 1
            
            # 获取CPU温度 (如果可用)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = None
                
                # 尝试从不同的温度传感器获取CPU温度
                for name, entries in temps.items():
                    if name.lower() in ['coretemp', 'cpu_thermal', 'k10temp', 'ryzen_smu']:
                        for entry in entries:
                            if 'core' in entry.label.lower() or 'cpu' in entry.label.lower():
                                cpu_temp = entry.current
                                break
                        if cpu_temp:
                            break
                
                # 如果没有找到特定的CPU温度，使用第一个可用的温度
                if not cpu_temp and temps:
                    for entries in temps.values():
                        if entries and hasattr(entries[0], 'current'):
                            cpu_temp = entries[0].current
                            break
                
                cpu_temp_str = f"{cpu_temp:.1f}°C" if cpu_temp else "N/A"
            except:
                cpu_temp_str = "N/A"
            
            # 获取进程信息
            processes = len(psutil.pids())
            running_processes = 0
            
            for pid in psutil.pids():
                try:
                    if psutil.Process(pid).status() == 'running':
                        running_processes += 1
                except:
                    pass
            
            # 获取CPU型号
            try:
                if platform.system() == "Linux":
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if line.strip().startswith('model name'):
                                cpu_model = line.split(':')[1].strip()
                                break
                        else:
                            cpu_model = "Unknown CPU"
                elif platform.system() == "Darwin":  # macOS
                    cpu_model = os.popen('sysctl -n machdep.cpu.brand_string').read().strip()
                elif platform.system() == "Windows":
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                    cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                    winreg.CloseKey(key)
                else:
                    cpu_model = "Unknown CPU"
            except:
                cpu_model = "Unknown CPU"
            
            # 格式化CPU速度
            cpu_speed = self.format_cpu_speed(cpu_freq.current if cpu_freq else None)
            
            return {
                'model': cpu_model,
                'speed': cpu_speed,
                'cores': cpu_count_physical,
                'threads': cpu_count_logical,
                'usage': self.format_progress_bar(cpu_percent),
                'temp': cpu_temp_str,
                'processes': {
                    'total': processes,
                    'active': running_processes
                }
            }
        except Exception as e:
            self.logger.error(f"获取CPU信息失败: {e}")
            return {
                'model': 'Unknown',
                'speed': 'N/A',
                'cores': 'N/A',
                'threads': 'N/A',
                'usage': self.format_progress_bar(0),
                'temp': 'N/A',
                'processes': {
                    'total': 0,
                    'active': 0
                }
            }

    # 获取内存信息
    def get_memory_info(self) -> dict:
        try:
            # 获取内存信息
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': self.format_bytes(mem.total),
                'free': self.format_bytes(mem.available),
                'used': self.format_bytes(mem.used),
                'percent': mem.percent,
                'swap_total': self.format_bytes(swap.total),
                'swap_used': self.format_bytes(swap.used)
            }
        except Exception as e:
            self.logger.error(f"获取内存信息失败: {e}")
            return {
                'total': 'N/A',
                'free': 'N/A',
                'used': 'N/A',
                'percent': 0,
                'swap_total': 'N/A',
                'swap_used': 'N/A'
            }

    # 获取磁盘信息
    def get_disk_info(self) -> list:
        try:
            # 获取磁盘分区信息
            partitions = psutil.disk_partitions()
            
            # 排除一些特殊挂载点
            exclude_mounts = ['/boot', '/dev', '/run', '/sys', '/proc', '/snap']
            
            disk_info = []
            
            for partition in partitions:
                # 跳过特殊挂载点
                if any(partition.mountpoint.startswith(mount) for mount in exclude_mounts) or 'docker' in partition.mountpoint:
                    continue
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # 跳过大小为0的分区
                    if usage.total == 0:
                        continue
                    
                    disk_info.append({
                        'mount': partition.mountpoint,
                        'fs': partition.fstype or 'N/A',
                        'type': partition.device.split(':')[0] if ':' in partition.device else 'N/A',
                        'total': self.format_bytes(usage.total),
                        'used': self.format_bytes(usage.used),
                        'available': self.format_bytes(usage.free),
                        'percent': usage.percent
                    })
                except:
                    # 跳过无法获取使用情况的分区
                    continue
            
            # 排序：首先是根目录，然后按挂载点字母顺序
            disk_info.sort(key=lambda x: (x['mount'] != '/', x['mount']))
            
            return disk_info
        except Exception as e:
            self.logger.error(f"获取磁盘信息失败: {e}")
            return []

    # 获取系统运行时间
    def get_uptime(self) -> dict:
        try:
            # 获取系统启动时间
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            return {
                'seconds': uptime_seconds,
                'hours': uptime_seconds // 3600,
                'minutes': (uptime_seconds % 3600) // 60,
                'formatted': self.format_uptime(int(uptime_seconds))
            }
        except Exception as e:
            self.logger.error(f"获取系统运行时间失败: {e}")
            return {
                'seconds': 0,
                'hours': 0,
                'minutes': 0,
                'formatted': 'N/A'
            }

    # 获取系统负载信息
    def get_load_info(self) -> dict:
        try:
            # 获取系统负载
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
            else:
                # Windows系统没有getloadavg函数，使用CPU使用率代替
                load_avg = (psutil.cpu_percent() / 100, 0, 0)
            
            cpu_count = psutil.cpu_count()
            
            return {
                'avg1': f"{load_avg[0]:.2f}",
                'avg5': f"{load_avg[1]:.2f}",
                'avg15': f"{load_avg[2]:.2f}",
                'max_load': cpu_count,
                'safe_load': f"{(cpu_count * 0.7):.2f}"  # 安全负载为核心数的70%
            }
        except Exception as e:
            self.logger.error(f"获取系统负载信息失败: {e}")
            cpu_count = psutil.cpu_count()
            return {
                'avg1': '0.00',
                'avg5': '0.00',
                'avg15': '0.00',
                'max_load': cpu_count,
                'safe_load': f"{(cpu_count * 0.7):.2f}"
            }

    # 根据负载值返回状态指示符
    def get_load_status(self, load: str, safe_load: str) -> str:
        try:
            load_num = float(load)
            safe_num = float(safe_load)
            
            if load_num >= safe_num * 1.5:
                return '⚠️'  # 高负载
            if load_num >= safe_num:
                return '⚡'  # 中等负载
            return '✓'  # 低负载
        except:
            return ''

    # 获取网络连接状态描述
    def get_network_status_description(self, status: str) -> str:
        status_map = {
            'up': '已连接 ✓',
            'down': '已断开 ✗',
            'unknown': '未知状态',
            'dormant': '休眠状态',
            'not present': '设备不存在',
            'lower layer down': '底层连接断开',
            'testing': '测试中',
            'middle layer down': '中间层连接断开'
        }
        return status_map.get(status, status)

    # 获取网络类型描述
    def get_network_type_description(self, type_: str) -> str:
        type_map = {
            'wired': '有线网络',
            'wireless': '无线网络',
            'bluetooth': '蓝牙网络',
            'virtual': '虚拟网络',
            'loopback': '回环接口',
            'cellular': '蜂窝网络'
        }
        return type_map.get(type_, type_)

    # 判断是否为虚拟网络接口
    def is_virtual_interface(self, iface_name: str) -> bool:
        # Docker相关接口
        if (iface_name.startswith('docker') or 
            iface_name.startswith('br-') or 
            iface_name.startswith('veth') or 
            iface_name == 'lo'):
            return True
        
        # 其他常见虚拟接口
        virtual_prefixes = ['virbr', 'vnet', 'tun', 'tap', 'vbox', 'vmnet']
        return any(iface_name.startswith(prefix) for prefix in virtual_prefixes)

    # 获取所有网络接口信息
    def get_all_network_info(self) -> list:
        try:
            # 获取网络接口信息
            net_io_counters = psutil.net_io_counters(pernic=True)
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            # 获取当前时间
            current_time = time.time()
            time_diff = current_time - self.last_update_time
            
            networks = []
            
            for iface_name in net_io_counters:
                # 跳过回环接口
                if iface_name == 'lo':
                    continue
                
                # 获取网络接口统计信息
                io_counter = net_io_counters[iface_name]
                
                # 获取网络接口地址
                ip_address = 'N/A'
                mac_address = 'N/A'
                
                if iface_name in net_if_addrs:
                    for addr in net_if_addrs[iface_name]:
                        # 获取IPv4地址
                        if addr.family == socket.AF_INET:
                            ip_address = addr.address
                        # 获取MAC地址
                        elif addr.family == psutil.AF_LINK:
                            mac_address = addr.address
                
                # 获取网络接口状态
                status = 'unknown'
                if iface_name in net_if_stats:
                    status = 'up' if net_if_stats[iface_name].isup else 'down'
                
                # 计算网络速率
                rx_bytes = io_counter.bytes_recv
                tx_bytes = io_counter.bytes_sent
                
                # 获取上次的计数器值
                last_rx = 0
                last_tx = 0
                
                if iface_name in self.network_history:
                    last_rx = self.network_history[iface_name]['rx_bytes']
                    last_tx = self.network_history[iface_name]['tx_bytes']
                
                # 计算速率 (字节/秒)
                rx_speed = (rx_bytes - last_rx) / time_diff if time_diff > 0 else 0
                tx_speed = (tx_bytes - last_tx) / time_diff if time_diff > 0 else 0
                
                # 更新历史数据
                self.network_history[iface_name] = {
                    'rx_bytes': rx_bytes,
                    'tx_bytes': tx_bytes
                }
                
                # 确定网络类型
                network_type = 'unknown'
                if iface_name.startswith('en') or iface_name.startswith('eth'):
                    network_type = 'wired'
                elif iface_name.startswith('wl') or iface_name.startswith('wi'):
                    network_type = 'wireless'
                elif self.is_virtual_interface(iface_name):
                    network_type = 'virtual'
                
                networks.append({
                    'interface': iface_name,
                    'ip': ip_address,
                    'mac': mac_address,
                    'type': self.get_network_type_description(network_type),
                    'status': self.get_network_status_description(status),
                    'rx': self.format_bytes(rx_speed),
                    'tx': self.format_bytes(tx_speed),
                    'rx_total': self.format_bytes(rx_bytes),
                    'tx_total': self.format_bytes(tx_bytes)
                })
            
            # 更新最后更新时间
            self.last_update_time = current_time
            
            return networks
        except Exception as e:
            self.logger.error(f"获取网络信息失败: {e}")
            return []

    # 插件卸载时触发
    def __del__(self):
        self.logger.info("运行状态插件已卸载")

# 导入可能需要的额外模块
import math
