#!/usr/bin/env python3
"""Recolector de estadísticas del sistema para el plasmoid widgets-bar.

Se invoca una vez por tick desde QML (Plasma5Support.DataSource, engine
"executable"), imprime un único JSON con todas las métricas y termina.
El delta de red se persiste en disco porque cada invocación es un proceso
nuevo (no hay estado en memoria entre ticks).
"""
import json
import os
import subprocess
import time

import psutil

NET_STATE_FILE = os.path.expanduser("~/.cache/widgets-bar-plasmoid/netstate.json")


def get_cpu_ram():
    cpu = psutil.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    return {
        "cpu_pct": cpu,
        "ram_used": vm.used / 1024**3,
        "ram_total": vm.total / 1024**3,
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


def get_temps_and_fans():
    try:
        result = subprocess.run(["sensors", "-j"], capture_output=True, text=True, timeout=2)
        data = json.loads(result.stdout)

        cpu_temp = gpu_temp = ssd_temp = None
        fans = []
        for chip, sensors in data.items():
            if "k10temp" in chip:
                cpu_temp = sensors.get("Tctl", {}).get("temp1_input")
            elif "amdgpu" in chip:
                gpu_temp = sensors.get("junction", {}).get("temp2_input")
                if gpu_temp is None:
                    gpu_temp = sensors.get("edge", {}).get("temp1_input")
            elif "nvme" in chip:
                ssd_temp = sensors.get("Composite", {}).get("temp1_input")

            chip_label = "GPU" if "amdgpu" in chip else chip.split("-")[0].upper()
            for label, vals in sensors.items():
                if not isinstance(vals, dict):
                    continue
                rpm = vals.get(label + "_input") if label.startswith("fan") else None
                if rpm is not None:
                    fans.append({"label": chip_label, "rpm": rpm})

        return {"cpu_temp": cpu_temp, "gpu_temp": gpu_temp, "ssd_temp": ssd_temp, "fans": fans}
    except Exception:
        return {"cpu_temp": None, "gpu_temp": None, "ssd_temp": None, "fans": []}


def get_network():
    now = time.time()
    try:
        counters = psutil.net_io_counters(pernic=True)
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

        prev = None
        os.makedirs(os.path.dirname(NET_STATE_FILE), exist_ok=True)
        if os.path.exists(NET_STATE_FILE):
            try:
                with open(NET_STATE_FILE) as f:
                    prev = json.load(f)
            except Exception:
                prev = None

        with open(NET_STATE_FILE, "w") as f:
            json.dump({
                "bytes_recv": curr.bytes_recv,
                "bytes_sent": curr.bytes_sent,
                "timestamp": now,
            }, f)

        if prev is None:
            return {"iface": active_iface, "down": 0.0, "up": 0.0}

        dt = now - prev["timestamp"]
        down = (curr.bytes_recv - prev["bytes_recv"]) / dt if dt > 0 else 0
        up = (curr.bytes_sent - prev["bytes_sent"]) / dt if dt > 0 else 0
        return {"iface": active_iface, "down": max(0, down), "up": max(0, up)}
    except Exception:
        return {"iface": "--", "down": 0.0, "up": 0.0}


def get_disks():
    try:
        root = psutil.disk_usage("/")
        return [{"mount": "/", "pct": root.percent, "free_gb": root.free / 1024**3}]
    except Exception:
        return []


def get_system():
    try:
        uptime_secs = time.time() - psutil.boot_time()
        hours = int(uptime_secs // 3600)
        minutes = int((uptime_secs % 3600) // 60)
        kernel = subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip()
        kernel_short = kernel.split("-")[0] if kernel else "--"
        return {
            "kernel": kernel_short,
            "distro": "CachyOS",
            "uptime_h": hours,
            "uptime_m": minutes,
        }
    except Exception:
        return {"kernel": "--", "distro": "CachyOS", "uptime_h": 0, "uptime_m": 0}


def main():
    stats = {}
    stats.update(get_cpu_ram())
    stats.update(get_gpu())
    stats.update(get_temps_and_fans())
    stats.update(get_network())
    stats["disks"] = get_disks()
    stats.update(get_system())
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
