import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Sistema"
    property var kernel: undefined
    property var uptimeH: undefined
    property var uptimeM: undefined

    RowLayout {
        Text {
            text: "CachyOS"
            color: Theme.ACCENT
            font.pixelSize: 13
            font.weight: Font.Bold
        }
        Item { Layout.fillWidth: true }
    }
    Text {
        text: "Linux " + (root.kernel !== undefined ? root.kernel : "--")
        color: Theme.TEXT_SEC
        font.pixelSize: 9
    }
    Text {
        text: (root.uptimeH !== undefined)
              ? root.uptimeH + "h " + String(root.uptimeM).padStart(2, "0") + "m activo"
              : "--"
        color: Theme.TEXT_PRI
        font.pixelSize: 10
    }

    Item { Layout.fillHeight: true }
}
