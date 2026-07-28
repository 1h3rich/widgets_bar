import QtQuick
import QtQuick.Controls as QQC2
import "../Theme.js" as Theme

QQC2.Button {
    id: root
    implicitWidth: 26
    implicitHeight: 22

    // "⏸" es un glifo de fuente con un peso/estilo distinto a las
    // flechas ◀◀/▶/▶▶, así que se dibuja a mano para que combine.
    readonly property bool isPause: text === "⏸"

    background: Rectangle {
        radius: 5
        color: root.down ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 160 / 255)
             : root.hovered ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 80 / 255)
             : Qt.rgba(1, 1, 1, 14 / 255)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 22 / 255)
    }

    contentItem: Item {
        Text {
            anchors.centerIn: parent
            visible: !root.isPause
            text: root.text
            color: Theme.TEXT_PRI
            font.pixelSize: 11
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        Row {
            anchors.centerIn: parent
            visible: root.isPause
            spacing: 2
            Rectangle { width: 3; height: 10; radius: 1; color: Theme.TEXT_PRI }
            Rectangle { width: 3; height: 10; radius: 1; color: Theme.TEXT_PRI }
        }
    }
}
