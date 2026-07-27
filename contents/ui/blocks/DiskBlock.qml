import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Disco"
    property var disks: []
    readonly property var disk0: (disks && disks.length > 0) ? disks[0] : undefined

    RowLayout {
        spacing: 5
        Text {
            text: root.disk0 !== undefined ? root.disk0.pct.toFixed(0) : "--"
            color: root.disk0 !== undefined ? Theme.pctColor(root.disk0.pct, 80, 90) : Theme.TEXT_SEC
            font.pixelSize: 20
            font.weight: Font.Bold
        }
        Text { text: "%"; color: Theme.TEXT_SEC; font.pixelSize: 10 }
        Item { Layout.fillWidth: true }
    }

    Text {
        text: root.disk0 !== undefined ? root.disk0.free_gb.toFixed(0) + " GB libres" : "-- GB libres"
        color: Theme.TEXT_SEC
        font.pixelSize: 10
    }

    Item { Layout.fillHeight: true }
}
