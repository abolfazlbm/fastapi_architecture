from pydantic import Field

from backend.common.schema import SchemaBase


class CpuInfo(SchemaBase):
    """CPU information"""

    usage: float = Field(description='CPU usage (%)')
    logical_num: int = Field(description='logical core number')
    physical_num: int = Field(description='Physical core number')
    max_freq: float = Field(description='Maximum frequency (MHz)')
    min_freq: float = Field(description='Minimum frequency (MHz)')
    current_freq: float = Field(description='Current frequency (MHz)')


class MemInfo(SchemaBase):
    """Memory information"""

    total: float = Field(description='Total memory (GB)')
    used: float = Field(description='Memory used (GB)')
    free: float = Field(description='Available memory (GB)')
    usage: float = Field(description='Memory usage (%)')


class SysInfo(SchemaBase):
    """System information"""

    name: str = Field(description='hostname')
    ip: str = Field(description='IP address')
    os: str = Field(description='operating system')
    arch: str = Field(description='system architecture')


class DiskInfo(SchemaBase):
    """Disk information"""

    dir: str = Field(description='mount point')
    type: str = Field(description='File system type')
    device: str = Field(description='device name')
    total: str = Field(description='Total capacity')
    free: str = Field(description='Available capacity')
    used: str = Field(description='Used capacity')
    usage: str = Field(description='usage rate')


class ServiceInfo(SchemaBase):
    """Service information"""

    name: str = Field(description='Service Name')
    version: str = Field(description='version')
    home: str = Field(description='Installation path')
    cpu_usage: str = Field(description='CPU usage')
    mem_vms: str = Field(description='virtual memory')
    mem_rss: str = Field(description='physical memory')
    mem_free: str = Field(description='Available memory')
    startup: str = Field(description='Startup time')
    elapsed: str = Field(description='running time')


class ServerMonitorInfo(SchemaBase):
    """Server monitoring information"""

    cpu: CpuInfo = Field(description='CPU information')
    mem: MemInfo = Field(description='memory information')
    sys: SysInfo = Field(description='System Information')
    disk: list[DiskInfo] = Field(description='Disk information list')
    service: ServiceInfo = Field(description='Service Information')


class RedisServerInfo(SchemaBase):
    """Redis server information"""

    redis_version: str = Field(description='Redis version')
    redis_mode: str = Field(description='Run Mode')
    os: str = Field(description='operating system')
    arch_bits: str = Field(description='architecture bits')
    tcp_port: str = Field(description='TCP port')
    uptime_in_seconds: str = Field(description='running time')
    connected_clients: str = Field(description='Number of connected clients')
    used_memory_human: str = Field(description='Memory used')
    used_memory_peak_human: str = Field(description='Memory usage peak')
    maxmemory_human: str = Field(description='Maximum memory limit')
    keys_num: str = Field(description='Total number of keys')


class RedisCommandStat(SchemaBase):
    """Redis command statistics"""

    name: str = Field(description='command name')
    value: str = Field(description='Number of calls')


class RedisMonitorInfo(SchemaBase):
    """Redis monitoring information"""

    info: RedisServerInfo = Field(description='Server Information')
    stats: list[RedisCommandStat] = Field(description='Command statistics list')
