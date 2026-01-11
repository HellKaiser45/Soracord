import docker
from dataclasses import dataclass


@dataclass
class ContainerStatus:
    name: str
    status: str
    health: str


@dataclass
class ContainerStats:
    name: str
    cpu: float
    mem: float


class DockerMonitor:
    def __init__(self):
        self._client = docker.from_env()

    def check_containers(self) -> list[ContainerStatus]:
        results = []
        for c in self._client.containers.list():
            results.append(ContainerStatus(c.name, c.status, c.health))
        return results

    def container_logs(self, name: str):
        pass

    def container_stats(self, name: str):
        container = self._client.containers.get(name)

        raw_stats = container.stats(stream=False)

        assert isinstance(raw_stats, dict), f"Expected dict, got {type(raw_stats)}"

        cpu_delta = (
            raw_stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - raw_stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            raw_stats["cpu_stats"]["system_cpu_usage"]
            - raw_stats["precpu_stats"]["system_cpu_usage"]
        )
        cpu_percent = round(
            (cpu_delta / system_delta)
            * (raw_stats["cpu_stats"]["online_cpus"] or 1)
            * 100,
            3,
        )

        ram_bytes = raw_stats["memory_stats"]["usage"]
        ram_limit_bytes = raw_stats["memory_stats"]["limit"]
        ram_percent = round((ram_bytes / ram_limit_bytes) * 100, 3)

        network = next(iter(raw_stats["networks"].values()))  # Get first interface
        rx_total = round(network["rx_bytes"] / 1024**3, 2)  # dl
        tx_total = round(network["tx_bytes"] / 1024**3, 2)  # upl

        read_bytes = 0
        write_bytes = 0
        if raw_stats["blkio_stats"]["io_service_bytes_recursive"]:
            for item in raw_stats["blkio_stats"]["io_service_bytes_recursive"]:
                if item["op"] == "read":
                    read_bytes += item["value"]
                elif item["op"] == "write":
                    write_bytes += item["value"]

        return round(read_bytes / 1024**2, 2)


if __name__ == "__main__":
    monitor = DockerMonitor()
    print(monitor.container_stats("radarr"))
