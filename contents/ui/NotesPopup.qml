import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtCore
import "Theme.js" as Theme

Rectangle {
    id: root
    width: 360
    height: 200
    visible: opened
    property bool opened: false

    radius: 14
    color: Qt.rgba(14 / 255, 14 / 255, 24 / 255, 220 / 255)
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, 22 / 255)

    Settings {
        id: settings
        category: "Notes"
        property string text: ""
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 4

        Text {
            text: "Notas rápidas"
            color: Theme.TEXT_SEC
            font.pixelSize: 10
            font.weight: Font.DemiBold
        }

        QQC2.ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            QQC2.TextArea {
                id: editor
                text: settings.text
                color: Theme.TEXT_PRI
                font.pixelSize: 12
                wrapMode: TextEdit.Wrap
                background: null
                selectByMouse: true

                onTextChanged: saveTimer.restart()
            }
        }
    }

    Timer {
        id: saveTimer
        interval: 800
        onTriggered: settings.text = editor.text
    }
}
