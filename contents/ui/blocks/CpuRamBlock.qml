import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "CPU · RAM"
    property var stats: ({})
    readonly property var cpuPct: stats.cpu_pct
    readonly property var ramUsed: stats.ram_used
    readonly property var ramTotal: stats.ram_total
    readonly property var ramPct: stats.ram_pct

    RowLayout {
        spacing: 5
        Text {
            text: root.cpuPct !== undefined && root.cpuPct !== null ? root.cpuPct.toFixed(0) : "--"
            color: Theme.pctColor(root.cpuPct)
            font.pixelSize: 20
            font.weight: Font.Bold
        }
        Text { text: "%"; color: Theme.TEXT_SEC; font.pixelSize: 10 }
        Item { Layout.fillWidth: true }
    }

    Text {
        text: (root.ramUsed !== undefined && root.ramUsed !== null && root.ramTotal !== undefined && root.ramTotal !== null)
              ? "RAM " + root.ramUsed.toFixed(1) + " / " + root.ramTotal.toFixed(0) + " GB"
              : "RAM -- / -- GB"
        color: (root.ramPct !== undefined && root.ramPct > 90) ? Theme.TEXT_WARN : Theme.TEXT_SEC
        font.pixelSize: 10
    }

    Item { Layout.fillHeight: true }
}
