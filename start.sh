#!/usr/bin/env bash
# Forzar XWayland para que move() funcione correctamente con KDE
export QT_QPA_PLATFORM=xcb
cd "$(dirname "$0")"
exec python3 main.py "$@"
