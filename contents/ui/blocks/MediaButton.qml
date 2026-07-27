import QtQuick
import QtQuick.Controls as QQC2
import "../Theme.js" as Theme

QQC2.Button {
    id: root
    implicitWidth: 26
    implicitHeight: 22

    background: Rectangle {
        radius: 5
        color: root.down ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 160 / 255)
             : root.hovered ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 80 / 255)
             : Qt.rgba(1, 1, 1, 14 / 255)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 22 / 255)
    }

    contentItem: Text {
        text: root.text
        color: Theme.TEXT_PRI
        font.pixelSize: 11
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
