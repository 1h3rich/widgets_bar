import QtQuick
import QtQuick.Layouts
import "../Theme.js" as Theme

Item {
    id: root
    property string title: ""
    default property alias content: body.data

    Layout.fillWidth: true
    Layout.fillHeight: true

    ColumnLayout {
        id: body
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 7
        anchors.bottomMargin: 7
        spacing: 3

        Text {
            text: root.title.toUpperCase()
            color: Theme.TEXT_SEC
            font.pixelSize: 8
            font.weight: Font.Bold
            font.letterSpacing: 1
        }
    }
}
