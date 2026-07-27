import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Temperaturas"
    property var cpuTemp: undefined
    property var gpuTemp: undefined
    property var ssdTemp: undefined
    property var fans: []

    RowLayout {
        spacing: 8
        Layout.fillWidth: true

        ColumnLayout {
            spacing: 1
            Text {
                text: root.cpuTemp !== undefined && root.cpuTemp !== null ? root.cpuTemp.toFixed(0) + "°" : "--°"
                color: Theme.tempColor(root.cpuTemp, 85, 90)
                font.pixelSize: 14
                font.weight: Font.Bold
            }
            Text { text: "CPU"; color: Theme.TEXT_SEC; font.pixelSize: 8 }
        }
        Item { Layout.fillWidth: true }
        ColumnLayout {
            spacing: 1
            Text {
                text: root.gpuTemp !== undefined && root.gpuTemp !== null ? root.gpuTemp.toFixed(0) + "°" : "--°"
                color: Theme.tempColor(root.gpuTemp, 85, 90)
                font.pixelSize: 14
                font.weight: Font.Bold
            }
            Text { text: "GPU"; color: Theme.TEXT_SEC; font.pixelSize: 8 }
        }
        Item { Layout.fillWidth: true }
        ColumnLayout {
            spacing: 1
            Text {
                text: root.ssdTemp !== undefined && root.ssdTemp !== null ? root.ssdTemp.toFixed(0) + "°" : "--°"
                color: Theme.tempColor(root.ssdTemp, 70, 90)
                font.pixelSize: 14
                font.weight: Font.Bold
            }
            Text { text: "SSD"; color: Theme.TEXT_SEC; font.pixelSize: 8 }
        }
    }

    Row {
        spacing: 8
        visible: root.fans.length > 0
        Repeater {
            model: root.fans
            Text {
                text: "🌀 " + modelData.rpm.toFixed(0) + " RPM"
                color: Theme.TEXT_SEC
                font.pixelSize: 9
            }
        }
    }

    Item { Layout.fillHeight: true }
}
