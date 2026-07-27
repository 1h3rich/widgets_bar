import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Notas"
    signal clicked()

    Layout.fillWidth: false

    QQC2.Button {
        id: btn
        implicitWidth: 36
        implicitHeight: 30

        background: Rectangle {
            radius: 8
            color: btn.down ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 160 / 255)
                 : btn.hovered ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 80 / 255)
                 : Qt.rgba(1, 1, 1, 12 / 255)
            border.width: 1
            border.color: Qt.rgba(1, 1, 1, 20 / 255)
        }

        contentItem: Text {
            text: "📝"
            font.pixelSize: 15
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: root.clicked()
    }

    Item { Layout.fillHeight: true }
}
