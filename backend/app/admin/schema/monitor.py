from pydantic import Field

from backend.common.schema import SchemaBase


class CpuInfo(SchemaBase):
    """CPU information"""

    physical_num: int = Field(description='Number of physical cores')
    logical_num: int = Field(description='Number of logical cores')
    max_freq: float = Field(description='Maximum Frequency（MHz）')
    min_freq: float = Field(description='Minimum Frequency（MHz）')
    current_freq: float = Field(description='Current Frequency（MHz）')
    usage: float = Field(description='Usage Rate（%）')


class MemInfo(SchemaBase):
    """Memory information"""

    total: float = Field(description='Total capacity (GB)')
    used: float = Field(description='Used (GB)')
    free: float = Field(description='Available (GB)')
    usage: float = Field(description='Usage rate (%)')


class SysInfo(SchemaBase):
    """System information"""

    name: str = Field(description='hostname')
    os: str = Field(description='operating system')
    ip: str = Field(description='IP address')
    arch: str = Field(description='system architecture')


class DiskInfo(SchemaBase):
    """Disk information"""

    dir: str = Field(description='mount point')
    device: str = Field(description='device name')
    type: str = Field(description='File system type')
    total: str = Field(description='Total capacity')
    used: str = Field(description='used')
    free: str = Field(description='available')
    usage: str = Field(description='Usage rate (%)')


class ServiceInfo(SchemaBase):
    """Service process information"""

    name: str = Field(description='Service Name')
    version: str = Field(description='version')
    home: str = Field(description='Installation path')
    startup: str = Field(description='Startup time')
    elapsed: str = Field(description='running time')
    cpu_usage: str = Field(description='CPU usage')
    mem_vms: str = Field(description='virtual memory')
    mem_rss: str = Field(description='physical memory')
    mem_free: str = Field(description='Available memory')


class ServerMonitorInfo(SchemaBase):
    """Server monitoring information"""

    cpu: CpuInfo = Field(description='CPU information')
    mem: MemInfo = Field(description='memory information')
    sys: SysInfo = Field(description='System Information')
    disk: list[DiskInfo] = Field(description='Disk Information')
    service: ServiceInfo = Field(description='Service Information')


class RedisServerInfo(SchemaBase):
    """Redis server information"""

    redis_version: str = Field(description='version number')
    redis_mode: str = Field(description='Run Mode')
    role: str = Field(description='Node role')
    tcp_port: str = Field(description='Listening port')
    uptime: str = Field(description='running time')
    connected_clients: str = Field(description='Number of connected clients')
    blocked_clients: str = Field(description='Number of blocked clients')
    used_memory_human: str = Field(description='Memory used')
    used_memory_rss_human: str = Field(description='RSS memory')
    maxmemory_human: str = Field(description='Maximum memory limit')
    mem_fragmentation_ratio: str = Field(description='Memory fragmentation rate')
    instantaneous_ops_per_sec: str = Field(description='Operations per second')
    total_commands_processed: str = Field(description='Total number of commands processed')
    rejected_connections: str = Field(description='Number of rejected connections')
    keys_num: str = Field(description='Total number of keys')


class RedisCommandStat(SchemaBase):
    """Redis command statistics"""

    name: str = Field(description='command name')
    value: str = Field(description='Number of calls')


class RedisMonitorInfo(SchemaBase):
    """Redis monitoring information"""

    info: RedisServerInfo = Field(description='Server Information')
    stats: list[RedisCommandStat] = Field(description='Command Statistics')
