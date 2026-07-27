# widgets_bar

Barra de widgets flotante para KDE Plasma 6 (CachyOS/Arch), esquina inferior izquierda: CPU/RAM, GPU/VRAM, temperaturas, disco, red, info del sistema, control multimedia (MPRIS) y notas rápidas.

## Cómo se ve / comportamiento

- Empieza invisible. Al acercar el cursor a la zona de la barra (o justo por encima) se despliega con una animación de opacidad + una máscara que la revela de abajo hacia arriba, como un cajón. Al alejar el cursor, se repliega tras un pequeño retraso.
- Fondo con blur nativo de KDE, esquinas redondeadas.
- Botón de notas: panel flotante con auto-guardado.

## Ejecutar

```bash
./start.sh
```

Fuerza `QT_QPA_PLATFORM=xcb` porque en Wayland nativo `move()`/`setGeometry()` los ignora KDE Plasma — hace falta XWayland para que la barra se posicione bien.

## Estructura

- `main.py` — punto de entrada
- `bar.py` — ventana principal y todos los bloques de datos
- `collectors.py` — recolección de métricas del sistema
- `media_ctrl.py` — control MPRIS vía D-Bus
- `notes_panel.py` — panel flotante de notas con auto-guardado (`data/notes.txt`, no se sube al repo)

## Hardware que asume por defecto

Pensada para AMD (lee `gpu_busy_percent` de `/sys/class/drm`, sensores `amdgpu`/`k10temp`/`nvme` vía `lm-sensors`). Si tu hardware es distinto, hay que ajustar `collectors.py`.

## Requisitos

Python 3, PyQt6, `psutil`, `lm-sensors` (comando `sensors`), un reproductor con soporte MPRIS si quieres el bloque de multimedia.

---

Hecho con ayuda de IA (Claude Code). Puede tener fallos en hardware o configuraciones distintas a las mías (otra GPU, un solo monitor, otro entorno de escritorio) — si algo no funciona, lo primero es mirar `collectors.py`, que es donde están las rutas específicas de sensores.
