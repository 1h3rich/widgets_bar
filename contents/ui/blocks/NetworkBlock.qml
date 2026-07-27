import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Red"
    property var down: undefined
    property var up: undefined

    RowLayout {
        Text {
            text: "↓ " + Theme.formatSpeed(root.down)
            color: "#60D0FF"
            font.pixelSize: 12
            font.weight: Font.Bold
        }
        Item { Layout.fillWidth: true }
    }
    RowLayout {
        Text {
            text: "↑ " + Theme.formatSpeed(root.up)
            color: "#80F090"
            font.pixelSize: 12
            font.weight: Font.Bold
        }
        Item { Layout.fillWidth: true }
    }

    Item { Layout.fillHeight: true }
}
