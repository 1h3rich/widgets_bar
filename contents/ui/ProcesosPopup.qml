import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.plasma.plasma5support as Plasma5Support
import "Theme.js" as Theme

Rectangle {
    id: root
    width: 380
    height: 260
    visible: opened
    property bool opened: false
    property var apps: []
    property string filter: ""

    readonly property string scriptPath: Qt.resolvedUrl("../code/procesos.py").toString().replace("file://", "")

    radius: 14
    color: Qt.rgba(14 / 255, 14 / 255, 24 / 255, 235 / 255)
    border.width: 1
    border.color: Qt.rgba(1, 1, 1, 22 / 255)

    function refresh() { src.connectSource("python3 '" + scriptPath + "' list") }
    function stopApp(unit, force) {
        src.connectSource("python3 '" + scriptPath + "' stop '" + unit + "'" + (force ? " force" : ""))
        afterStop.restart()
    }

    function human(b) {
        if (b < 1048576) return (b / 1024).toFixed(0) + " KB"
        if (b < 1073741824) return (b / 1048576).toFixed(0) + " MB"
        return (b / 1073741824).toFixed(1) + " GB"
    }

    onOpenedChanged: if (opened) refresh()

    Plasma5Support.DataSource {
        id: src
        engine: "executable"
        connectedSources: []
        onNewData: (sourceName, data) => {
            disconnectSource(sourceName)
            if (sourceName.indexOf(" list") > 0 && data && data["stdout"]) {
                try {
                    var y = list.contentY
                    root.apps = JSON.parse(data["stdout"])
                    Qt.callLater(function() {
                        list.contentY = Math.min(y, Math.max(0, list.contentHeight - list.height))
                    })
                } catch (e) {}
            }
        }
    }

    Timer { interval: 2500; running: root.opened; repeat: true; onTriggered: root.refresh() }
    Timer { id: afterStop; interval: 900; onTriggered: root.refresh() }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        Text {
            text: "APPS EN SEGUNDO PLANO (" + list.count + ")"
            color: Theme.TEXT_SEC
            font.pixelSize: 10
            font.weight: Font.DemiBold
            font.letterSpacing: 1
        }

        QQC2.TextField {
            Layout.fillWidth: true
            placeholderText: "Buscar…"
            font.pixelSize: 12
            color: Theme.TEXT_PRI
            onTextChanged: root.filter = text.toLowerCase()
            background: Rectangle {
                radius: 6
                color: Qt.rgba(1, 1, 1, 14 / 255)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 22 / 255)
            }
        }

        ListView {
            id: list
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            model: root.apps.filter(a => a.name.toLowerCase().indexOf(root.filter) >= 0)
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}

            delegate: Rectangle {
                width: list.width - 8
                height: 44
                radius: 8
                color: Qt.rgba(1, 1, 1, 12 / 255)

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 8
                    spacing: 8

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0
                        Text {
                            Layout.fillWidth: true
                            text: modelData.name
                            elide: Text.ElideRight
                            color: Theme.TEXT_PRI
                            font.pixelSize: 13
                        }
                        Text {
                            text: root.human(modelData.rss) + " · " + modelData.nproc + " proc."
                            color: Theme.TEXT_SEC
                            font.pixelSize: 10
                        }
                    }

                    Rectangle {
                        width: 64
                        height: 26
                        radius: 6
                        color: stopArea.containsMouse ? "#EBA0AC" : "#F38BA8"
                        Text {
                            anchors.centerIn: parent
                            text: "Detener"
                            color: "#1E1E2E"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                        }
                        MouseArea {
                            id: stopArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: mouse => root.stopApp(modelData.unit, mouse.button === Qt.RightButton)
                        }
                    }
                }
            }
        }

        Text {
            text: "Clic derecho en Detener = forzar cierre"
            color: Theme.TEXT_SEC
            font.pixelSize: 9
        }
    }
}
