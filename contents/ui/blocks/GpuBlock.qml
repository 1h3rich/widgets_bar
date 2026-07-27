import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "GPU · VRAM"
    property var stats: ({})
    readonly property var gpuPct: stats.gpu_pct
    readonly property var vramUsed: stats.vram_used
    readonly property var vramTotal: stats.vram_total

    RowLayout {
        spacing: 5
        Text {
            text: root.gpuPct !== undefined && root.gpuPct !== null ? String(root.gpuPct) : "--"
            color: Theme.pctColor(root.gpuPct)
            font.pixelSize: 20
            font.weight: Font.Bold
        }
        Text { text: "%"; color: Theme.TEXT_SEC; font.pixelSize: 10 }
        Item { Layout.fillWidth: true }
    }

    Text {
        text: (root.vramUsed !== undefined && root.vramUsed !== null && root.vramTotal !== undefined && root.vramTotal !== null)
              ? "VRAM " + root.vramUsed.toFixed(1) + " / " + root.vramTotal.toFixed(0) + " GB"
              : "VRAM --"
        color: Theme.TEXT_SEC
        font.pixelSize: 10
    }

    Item { Layout.fillHeight: true }
}
