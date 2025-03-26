from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
import psutil
import platform
import socket
import time
import os

@register(name="SystemStatus", description="获取系统运行状态", version="1.0", author="YourName")
class SystemStatusPlugin(BasePlugin):

    def __init__(self, host: APIHost):
        self.host = host

    async def initialize(self):
        pass

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self.send_system_status(ctx)

    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        await self.send_system_status(ctx)

    async def send_system_status(self, ctx: EventContext):
        # 获取系统信息
        uptime = self.get_uptime()
        version = "v20.18.1"  # 示例版本号
        os_info = platform.platform()
        hostname = socket.gethostname()

        # 获取 CPU 信息
        cpu_info = self.get_cpu_info()

        # 获取内存信息
        memory_info = self.get_memory_info()

        # 获取磁盘信息
        disk_info = self.get_disk_info()

        # 获取网络信息
        network_info = self.get_network_info()

        # 格式化输出
        response = f"""
┌── 🖥️ 系统信息 ────────────────────
│
│ 运行时间: {uptime}
│ 版本: {version}
│ 操作系统: {os_info}
│ 主机名: {hostname}
│ 
┌── 📊 系统负载 ─────────────────────
│ 1分钟负载: {cpu_info['load_1m']} ✓
│ 5分钟负载: {cpu_info['load_5m']} ✓
│ 15分钟负载: {cpu_info['load_15m']} ✓
│ CPU核心数: {cpu_info['cores']}
│ 安全负载: {cpu_info['safe_load']}
│ 
┌── 🔥 CPU信息 ────────────────────
│ CPU型号: {cpu_info['model']}
│ 核心/线程: {cpu_info['cores']}核 / {cpu_info['threads']}线程
│ 主频: {cpu_info['speed']}
│ CPU使用率: [{cpu_info['usage_bar']}] {cpu_info['usage']}%
│ CPU温度: {cpu_info['temp']}°C
│ 进程: {cpu_info['processes']['active']}活动 / {cpu_info['processes']['total']}总数
│ 
┌── 💾 内存信息 ─────────────────────
│ 总内存: {memory_info['total']}
│ 已用内存: {memory_info['used']} [{memory_info['used_bar']}] {memory_info['percent']}%
│ 可用内存: {memory_info['free']}
│ SWAP: {memory_info['swap_used']}/{memory_info['swap_total']}
│ 
┌── 💽 磁盘信息 ─────────────────────
{disk_info}
┌── 🌐 网络信息 ─────────────────────
{network_info}
└────────────────────────────────
        """.strip()

        ctx.add_return("reply", [response])
        ctx.prevent_default()

    def get_uptime(self):
        uptime_seconds = time.time() - psutil.boot_time()
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟"

    def get_cpu_info(self):
        cpu_freq = psutil.cpu_freq()
        usage = psutil.cpu_percent(interval=1)
        load_avg = os.getloadavg()
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count()
        safe_load = cores * 0.7

        return {
            'model': platform.processor(),
            'cores': cores,
            'threads': threads,
            'speed': f"{cpu_freq.current:.2f} GHz" if cpu_freq else "N/A",
            'usage': usage,
            'usage_bar': self.format_progress_bar(usage),
            'temp': "N/A",  # 需要特定库获取温度
            'processes': {
                'active': len(psutil.pids()),
                'total': len(psutil.pids())
            },
            'load_1m': f"{load_avg[0]:.2f}",
            'load_5m': f"{load_avg[1]:.2f}",
            'load_15m': f"{load_avg[2]:.2f}",
            'safe_load': f"{safe_load:.2f}",
        }

    def get_memory_info(self):
        mem = psutil.virtual_memory()
        return {
            'total': self.format_bytes(mem.total),
            'used': self.format_bytes(mem.used),
            'free': self.format_bytes(mem.available),
            'percent': mem.percent,
            'used_bar': self.format_progress_bar(mem.percent),
            'swap_used': self.format_bytes(psutil.swap_memory().used),
            'swap_total': self.format_bytes(psutil.swap_memory().total)
        }

    def get_disk_info(self):
        partitions = psutil.disk_partitions()
        disk_info = []
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append(
                f"│ 挂载点: {partition.mountpoint}\n"
                f"│ 文件系统: {partition.fstype}\n"
                f"│ 类型: {partition.device}\n"
                f"│ 总空间: {self.format_bytes(usage.total)}\n"
                f"│ 已用空间: {self.format_bytes(usage.used)} [{self.format_progress_bar(usage.percent)}] {usage.percent}%\n"
                f"│ 可用空间: {self.format_bytes(usage.free)}\n"
            )
        return "\n".join(disk_info)

    def get_network_info(self):
        net_info = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    net_info.append(
                        f"│ 网卡名称: {interface} ({"有线网络" if "eth" in interface else "虚拟网络"})\n"
                        f"│ IP地址: {addr.address}\n"
                        f"│ MAC地址: {self.get_mac(interface)}\n"
                        f"│ 下载速度: {self.format_bytes(psutil.net_io_counters(pernic=True)[interface].bytes_recv)}/s\n"
                        f"│ 上传速度: {self.format_bytes(psutil.net_io_counters(pernic=True)[interface].bytes_sent)}/s\n"
                        f"│ 连接状态: {'已连接' if psutil.net_if_stats()[interface].isup else '未连接'} ✓\n"
                    )
        return "\n".join(net_info)

    def get_mac(self, interface):
        return psutil.net_if_addrs()[interface][1].address if len(psutil.net_if_addrs()[interface]) > 1 else "N/A"

    def format_progress_bar(self, percent):
        filled_length = int(15 * percent / 100)
        bar = '■' * filled_length + '□' * (15 - filled_length)
        return f"[{bar}] {percent:.1f}%"

    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"

