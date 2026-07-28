# widgets_bar

Widget nativo de KDE Plasma 6 (plasmoid) para el escritorio: CPU/RAM, GPU/VRAM, temperaturas + RPM de ventiladores, disco, red, info del sistema, control multimedia (MPRIS) y notas rápidas.

Versión anterior: app PyQt6 independiente (ventana flotante que simulaba un widget). Este es un plasmoid real, instalable desde "Añadir widgets" de Plasma — el código PyQt6 sigue disponible en el historial de este repo.

## Cómo se ve / comportamiento

- Vive en el escritorio (detrás de las ventanas normales, visible solo sobre escritorio vacío), esquina inferior izquierda.
- Al acercar el cursor se despliega deslizándose horizontalmente; al alejarlo se repliega tras un pequeño retraso.
- Botón de fijar (📌): mantiene la barra desplegada de forma permanente, ignorando el auto-ocultado.
- Fondo translúcido con esquinas redondeadas, compuesto directamente por Plasma Shell (sin hacks de blur de ventana).
- Botón de notas: panel con auto-guardado (persistido vía `Qt.labs.settings`/`QtCore.Settings`).

## Instalar

```bash
kpackagetool6 -t Plasma/Applet -i .
```

Para desarrollo, reemplazar la copia instalada por un symlink al repo:

```bash
rm -rf ~/.local/share/plasma/plasmoids/org.cachyos.widgetsbar
ln -s "$(pwd)" ~/.local/share/plasma/plasmoids/org.cachyos.widgetsbar
```

Luego, desde el escritorio: clic derecho → **Añadir o gestionar widgets** → buscar "Widgets Bar" → arrastrar al escritorio.

## Estructura

- `metadata.json` — metadatos del plasmoid (Plasma 6, `FormFactors: ["desktop"]`)
- `contents/ui/main.qml` — `PlasmoidItem` raíz
- `contents/ui/FullRepresentation.qml` — tarjeta deslizante, zona de hover, recolección de datos, layout de bloques
- `contents/ui/blocks/` — un componente QML por bloque de datos (CPU/RAM, GPU/VRAM, temperaturas, disco, red, sistema, multimedia, notas)
- `contents/ui/NotesPopup.qml` — panel de notas con auto-guardado
- `contents/ui/Theme.js` — paleta y helpers de color compartidos
- `contents/code/datasource.py` — recolector de estadísticas del sistema, invocado periódicamente vía `Plasma5Support.DataSource` (engine "executable")

## Multimedia (MPRIS)

Usa `org.kde.plasma.private.mpris` (el mismo módulo QML que los controles multimedia del bloqueo de pantalla de KDE) en vez de D-Bus manual.

## Hardware que asume por defecto

Pensada para AMD (lee `gpu_busy_percent` de `/sys/class/drm`, sensores `amdgpu`/`k10temp`/`nvme` vía `lm-sensors`). Si tu hardware es distinto, hay que ajustar `contents/code/datasource.py`.

## Requisitos

KDE Plasma 6, Python 3, `psutil`, `lm-sensors` (comando `sensors`), un reproductor con soporte MPRIS si quieres el bloque de multimedia.

## Actualizaciones

- **Icono de pausa del bloque multimedia dibujado a mano** en vez de con el glifo de fuente `⏸`: ese carácter tiene un peso/estilo de trazo distinto al de `◀◀`/`▶`/`▶▶`, así que quedaba visualmente descolocado. Ahora `MediaButton.qml` dibuja dos barras (`Rectangle`) cuando el botón representa "pausa", manteniendo el resto de iconos como texto — ver `contents/ui/blocks/MediaButton.qml`.

---

Hecho con ayuda de IA (Claude Code). Puede tener fallos en hardware o configuraciones distintas a las mías (otra GPU, un solo monitor, otra versión de Plasma) — si algo no funciona, lo primero es mirar `contents/code/datasource.py`, que es donde están las rutas específicas de sensores.
