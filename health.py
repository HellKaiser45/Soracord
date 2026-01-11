import psutil
from dataclasses import dataclass

# Metrics: cpu usage, ram usage, disk usage


@dataclass
class CPUMetrics:
    usage_percent: float
    per_core_usage: list[float]
    load_avg_15min: float


@dataclass
class RAMMetrics:
    total: float
    used: float
    free: float


@dataclass
class DiskMetrics:
    total: float
    used: float
    free: float


def cpu() -> CPUMetrics:
    cores = len(psutil.Process().cpu_affinity())  # OK- cpu cores
    cpu_percent_cores = psutil.cpu_percent(interval=1, percpu=True)  # OK - cores
    cpu_percent = psutil.cpu_percent(interval=1)  # OK
    loadA = psutil.getloadavg()[2] / cores * 100  # OK avg 15 mins %
    cpu = CPUMetrics(cpu_percent, cpu_percent_cores, loadA)

    return cpu


def ram() -> RAMMetrics:
    ram = psutil.virtual_memory()
    gb = 1024**3

    return RAMMetrics(
        round(ram.total / gb), round(ram.used / gb), round(ram.available / gb)
    )


def disk():
    disk = psutil.disk_usage("/")
    gb = 1024**3
    return DiskMetrics(
        round(disk.total / gb), round(disk.used / gb), round(disk.free / gb)
    )


if __name__ == "__main__":
    print("------------")
    print("CPU")
    print("------------")
    print(cpu())
    print("------------")
    print("RAM")
    print("------------")
    print(ram())
    print("------------")
    print("DISK")
    print("------------")
    print(disk())
