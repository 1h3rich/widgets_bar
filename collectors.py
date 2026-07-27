"""System data collection for the widget bar."""
import subprocess
import json
import time
import psutil

_net_prev = None
_net_time = None


def get_cpu_ram():
    cpu = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    ram_used = vm.used / 1024**3
    ram_total = vm.total / 1024**3
    return {
        "cpu_pct": cpu,
        "ram_used": ram_used,
        "ram_total": ram_total,
        "ram_pct": vm.percent,
    }


def get_gpu():
    try:
        with open("/sys/class/drm/card1/device/gpu_busy_percent") as f:
            gpu_pct = int(f.read().strip())
        with open("/sys/class/drm/card1/device/mem_info_vram_used") as f:
            vram_used = int(f.read().strip()) / 1024**3
        with open("/sys/class/drm/card1/device/mem_info_vram_total") as f:
            vram_total = int(f.read().strip()) / 1024**3
        return {"gpu_pct": gpu_pct, "vram_used": vram_used, "vram_total": vram_total}
    except Exception:
        return {"gpu_pct": None, "vram_used": None, "vram_total": None}


def get_temps():
    try:
        result = subprocess.run(["sensors", "-j"], capture_output=True, text=True, timeout=2)
        data = json.loads(result.stdout)

        cpu_temp = None
        gpu_temp = None
        ssd_temp = None

        for chip, sensors in data.items():
            if "k10temp" in chip:
                tctl = sensors.get("Tctl", {})
                cpu_temp = tctl.get("temp1_input")
            elif "amdgpu" in chip:
                junction = sensors.get("junction", {})
                gpu_temp = junction.get("temp2_input")
                if gpu_temp is None:
                    edge = sensors.get("edge", {})
                    gpu_temp = edge.get("temp1_input")
            elif "nvme" in chip:
                comp = sensors.get("Composite", {})
                ssd_temp = comp.get("temp1_input")

        return {"cpu_temp": cpu_temp, "gpu_temp": gpu_temp, "ssd_temp": ssd_temp}
    except Exception:
        return {"cpu_temp": None, "gpu_temp": None, "ssd_temp": None}


def get_network():
    global _net_prev, _net_time

    now = time.time()
    try:
        counters = psutil.net_io_counters(pernic=True)
        # Prefer enp* (ethernet) if it has traffic, else first active interface
        active_iface = None
        for name, stats in counters.items():
            if name.startswith("lo"):
                continue
            if stats.bytes_recv > 0 or stats.bytes_sent > 0:
                if active_iface is None or name.startswith("enp"):
                    active_iface = name

        if active_iface is None:
            return {"iface": "--", "down": 0.0, "up": 0.0}

        curr = counters[active_iface]

        if _net_prev is None or _net_time is None:
            _net_prev = curr
            _net_time = now
            return {"iface": active_iface, "down": 0.0, "up": 0.0}

        dt = now - _net_time
        down = (curr.bytes_recv - _net_prev.bytes_recv) / dt if dt > 0 else 0
        up = (curr.bytes_sent - _net_prev.bytes_sent) / dt if dt > 0 else 0
        _net_prev = curr
        _net_time = now

        return {"iface": active_iface, "down": max(0, down), "up": max(0, up)}
    except Exception:
        return {"iface": "--", "down": 0.0, "up": 0.0}


def get_disks():
    disks = []
    try:
        root = psutil.disk_usage("/")
        disks.append({"mount": "/", "pct": root.percent, "free_gb": root.free / 1024**3})
    except Exception:
        pass
    return disks


def get_system():
    try:
        boot_time = psutil.boot_time()
        uptime_secs = time.time() - boot_time
        hours = int(uptime_secs // 3600)
        minutes = int((uptime_secs % 3600) // 60)

        kernel = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
        # Shorten kernel: "7.1.4-1-cachyos" -> "7.1.4"
        kernel_short = kernel.split("-")[0] if kernel else "--"

        return {
            "kernel": kernel_short,
            "distro": "CachyOS",
            "uptime_h": hours,
            "uptime_m": minutes,
        }
    except Exception:
        return {"kernel": "--", "distro": "CachyOS", "uptime_h": 0, "uptime_m": 0}


def format_speed(bps):
    if bps < 1024:
        return f"{bps:.0f} B/s"
    elif bps < 1024**2:
        return f"{bps/1024:.1f} KB/s"
    else:
        return f"{bps/1024**2:.1f} MB/s"
