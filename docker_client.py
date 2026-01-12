import docker
from dataclasses import dataclass
from typing import Literal

Logs_levels = Literal["error", "all"]


@dataclass
class ContainerStatus:
    name: str
    status: str
    health: str


@dataclass(frozen=True)
class IOUsage:
    net_rx_gb: float  # Download total
    net_tx_gb: float  # Upload total
    disk_read_mb: float
    disk_write_mb: float


@dataclass(frozen=True)
class ContainerMetrics:
    name: str
    cpu_pct: float
    mem_mb: float
    mem_pct: float
    io: IOUsage


class DockerMonitor:
    def __init__(self):
        self._client = docker.from_env()

    def check_containers(self) -> list[ContainerStatus]:
        results = []
        for c in self._client.containers.list():
            results.append(ContainerStatus(c.name, c.status, c.health))
        return results

    def container_logs(
        self, name: str, lines: int = 20, level: Logs_levels = "all"
    ) -> str:
        stdout_bool = level.lower() == "all"
        return (
            self._client.containers.get(name)
            .logs(stdout=stdout_bool, tail=lines, timestamps=True)
            .decode("utf-8")
        ) or "No logs found"

    def get_metrics(self, name: str) -> ContainerMetrics:
        container = self._client.containers.get(name)
        # stream=False is critical for a single-shot check
        raw = container.stats(stream=False)
        assert isinstance(raw, dict), "stats() returned non-dict"

        # 1. CPU Calculation
        cpu_stats = raw["cpu_stats"]
        precpu = raw["precpu_stats"]

        cpu_delta = (
            cpu_stats["cpu_usage"]["total_usage"] - precpu["cpu_usage"]["total_usage"]
        )
        system_delta = cpu_stats["system_cpu_usage"] - precpu["system_cpu_usage"]
        online_cpus = cpu_stats.get("online_cpus", 1)

        cpu_pct = 0.0
        if system_delta > 0:
            cpu_pct = round((cpu_delta / system_delta) * online_cpus * 100, 2)

        # 2. Memory Calculation (Usage vs Limit)
        mem_stats = raw["memory_stats"]
        mem_usage = mem_stats.get("usage", 0)
        mem_limit = mem_stats.get("limit", 1)

        mem_mb = round(mem_usage / (1024**2), 1)
        mem_pct = round((mem_usage / mem_limit) * 100, 2)

        # 3. Network IO (Sum of all interfaces)
        networks = raw.get("networks", {})
        rx_bytes = sum(iface["rx_bytes"] for iface in networks.values())
        tx_bytes = sum(iface["tx_bytes"] for iface in networks.values())

        # 4. Disk IO (Sum of all recursive service bytes)
        blk_stats = raw.get("blkio_stats", {}).get("io_service_bytes_recursive", [])
        # Fallback to 0 if list is None/empty
        blk_stats = blk_stats if blk_stats else []

        read_b = sum(i["value"] for i in blk_stats if i["op"].lower() == "read")
        write_b = sum(i["value"] for i in blk_stats if i["op"].lower() == "write")

        return ContainerMetrics(
            name=name,
            cpu_pct=cpu_pct,
            mem_mb=mem_mb,
            mem_pct=mem_pct,
            io=IOUsage(
                net_rx_gb=round(rx_bytes / (1024**3), 2),
                net_tx_gb=round(tx_bytes / (1024**3), 2),
                disk_read_mb=round(read_b / (1024**2), 1),
                disk_write_mb=round(write_b / (1024**2), 1),
            ),
        )


# TODO: Add an event stream as an alert system


if __name__ == "__main__":
    monitor = DockerMonitor()
    print(monitor.container_logs("jellyfin"))
