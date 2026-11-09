#!/usr/bin/env python3
"""Lista y detiene apps en segundo plano (unidades de app.slice de systemd --user).

  procesos.py list                 -> JSON [{unit, name, rss, nproc, kind}]
  procesos.py stop UNIT[,UNIT...] [force] -> SIGTERM (o SIGKILL con "force") a las unidades

Las apps basadas en Chromium/Electron (Chromium, Brave, ChatGPT...) sacan su proceso
principal a un scope propio "app-org.chromium.Chromium-<pid>.scope" (nombre fijo en
Chromium) y dejan el resto de procesos en la unidad con la que se lanzaron. Aquí se
juntan: cada scope "app-<id>-<pid>.scope" cuyos hijos viven en otra unidad se fusiona
con esa unidad, y si no, se nombra por el ejecutable de <pid>.
"""
import json
import os
import re
import signal
import subprocess
import sys

import psutil

UID = os.getuid()
APP_SLICE = "/app.slice/"
SELF_UNITS = ()  # nada que excluir: el plasmoid vive en plasmashell (session.slice)


def pretty_name(unit):
    base = re.sub(r"\.(scope|service)$", "", unit.replace("\\x2d", "-"))
    if base.startswith("app-"):
        base = re.sub(r"-\d+$", "", base[4:])
        base = base.split("@")[0]
        if base.startswith(("org.", "com.", "io.")):
            base = base.split(".")[-1]
    else:
        base = base.split("@")[0]
    return base.removesuffix("-autostart") or unit


SCOPE_PID = re.compile(r"^app-.+-(\d+)\.scope$")


def _exe_name(pid):
    try:
        return os.path.basename(os.readlink(f"/proc/{pid}/exe"))
    except OSError:
        return None


def list_apps():
    units = {}
    unit_of = {}   # pid -> unidad
    ppid_of = {}   # pid -> ppid
    for p in psutil.process_iter():
        try:
            if p.uids().real != UID or p.pid == os.getpid():
                continue
            with open(f"/proc/{p.pid}/cgroup") as f:
                cg = f.read().strip().split(":", 2)[-1]
            if APP_SLICE not in cg:
                continue
            unit = cg.split(APP_SLICE, 1)[1].lstrip("/").split("/")[0]
            if not unit.endswith((".scope", ".service")):
                continue
            rss = p.memory_info().rss
            ppid_of[p.pid] = p.ppid()
        except (psutil.Error, OSError):
            continue
        unit_of[p.pid] = unit
        u = units.setdefault(unit, {"unit": unit, "name": pretty_name(unit), "rss": 0,
                                    "nproc": 0, "kind": unit.rsplit(".", 1)[1]})
        u["rss"] += rss
        u["nproc"] += 1

    # Fusionar scopes "app-<id>-<pid>.scope" con la unidad donde viven sus hijos.
    for unit in list(units):
        m = SCOPE_PID.match(unit)
        if not m:
            continue
        main = int(m.group(1))
        homes = {unit_of[c] for c, pp in ppid_of.items()
                 if pp == main and unit_of.get(c) not in (None, unit)}
        if len(homes) == 1:
            home = units[homes.pop()]
            src = units.pop(unit)
            home["unit"] = f"{unit},{home['unit']}"   # scope primero: el proceso principal
            home["rss"] += src["rss"]
            home["nproc"] += src["nproc"]
        elif "chromium" in unit.lower():
            exe = _exe_name(main)
            if exe:
                units[unit]["name"] = exe
    return sorted(units.values(), key=lambda u: u["rss"], reverse=True)


def stop(units, force):
    units = units.split(",")
    for unit in units:
        if not re.fullmatch(r"[\w.@:\\-]+\.(scope|service)", unit):
            sys.exit("unidad no válida")
    sig = "SIGKILL" if force else "SIGTERM"
    for unit in units:
        if unit.endswith(".service") and not force:
            if subprocess.run(["systemctl", "--user", "stop", "--no-block", unit]).returncode == 0:
                continue
        subprocess.run(["systemctl", "--user", "kill", f"--signal={sig}", unit])


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        print(json.dumps(list_apps()))
    elif len(sys.argv) >= 3 and sys.argv[1] == "stop":
        stop(sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "force")
    else:
        sys.exit(__doc__)
