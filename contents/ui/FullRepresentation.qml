import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasma5support as Plasma5Support
import "Theme.js" as Theme
import "blocks"

Item {
    id: root
    implicitWidth: Theme.BAR_W
    implicitHeight: Theme.BAR_H + Theme.TRIGGER_ABOVE

    property var stats: ({})
    property bool revealed: false
    property bool pinned: false

    readonly property real contentWidth: Theme.BAR_W - 8
    readonly property real notesW: 56
    readonly property real colW1: (contentWidth - 3 * 1) / 4
    readonly property real colW2: (contentWidth - 3 * 1 - notesW) / 3

    readonly property string scriptPath: {
        var u = Qt.resolvedUrl("../code/datasource.py").toString()
        return u.replace("file://", "")
    }

    // ── Recolección de datos del sistema ────────────────────────────────
    Plasma5Support.DataSource {
        id: statsSource
        engine: "executable"
        connectedSources: []
        onNewData: (sourceName, data) => {
            disconnectSource(sourceName)
            if (data && data["stdout"]) {
                try {
                    root.stats = JSON.parse(data["stdout"])
                } catch (e) {
                    console.warn("widgets-bar: no se pudo parsear datasource.py:", e, data["stdout"])
                }
            }
        }
    }

    Timer {
        interval: 1500
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: statsSource.connectSource("python3 " + root.scriptPath)
    }

    // ── Detección de hover (zona = barra + margen superior) ─────────────
    HoverHandler {
        id: hover
        target: root
        onHoveredChanged: {
            if (hovered) {
                hideTimer.stop()
                root.revealed = true
            } else {
                hideTimer.restart()
            }
        }
    }

    Timer {
        id: hideTimer
        interval: Theme.HIDE_DELAY
        onTriggered: {
            if (!notesPopup.opened && !root.pinned) {
                root.revealed = false
            }
        }
    }

    // ── Tarjeta deslizante ────────────────────────────────────────────
    Item {
        id: clipContainer
        y: Theme.TRIGGER_ABOVE
        width: Theme.BAR_W
        height: Theme.BAR_H
        clip: true

        Rectangle {
            id: card
            width: Theme.BAR_W
            height: Theme.BAR_H
            radius: Theme.RADIUS
            color: Theme.BG_COLOR
            border.width: 1
            border.color: Theme.BORDER_COLOR
            x: root.revealed ? 0 : -width

            Behavior on x {
                NumberAnimation { duration: Theme.REVEAL_DURATION; easing.type: Easing.OutCubic }
            }

            Rectangle {
                id: pinButton
                width: 22
                height: 22
                radius: 11
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 6
                z: 10
                color: root.pinned ? Qt.rgba(149 / 255, 128 / 255, 255 / 255, 200 / 255) : Qt.rgba(1, 1, 1, 40 / 255)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 60 / 255)

                Text {
                    anchors.centerIn: parent
                    text: "📌"
                    font.pixelSize: 11
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.pinned = !root.pinned
                        if (!root.pinned && !hover.hovered) {
                            hideTimer.restart()
                        }
                    }
                }
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                spacing: 0

                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 0

                    CpuRamBlock {
                        Layout.preferredWidth: root.colW1
                        stats: root.stats
                    }
                    Separator {}
                    GpuBlock {
                        Layout.preferredWidth: root.colW1
                        stats: root.stats
                    }
                    Separator {}
                    TempBlock {
                        Layout.preferredWidth: root.colW1
                        cpuTemp: root.stats.cpu_temp
                        gpuTemp: root.stats.gpu_temp
                        ssdTemp: root.stats.ssd_temp
                        fans: root.stats.fans || []
                    }
                    Separator {}
                    DiskBlock {
                        Layout.preferredWidth: root.colW1
                        disks: root.stats.disks || []
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Qt.rgba(1, 1, 1, 12 / 255)
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 0

                    NetworkBlock {
                        Layout.preferredWidth: root.colW2
                        down: root.stats.down
                        up: root.stats.up
                    }
                    Separator {}
                    SystemBlock {
                        Layout.preferredWidth: root.colW2
                        kernel: root.stats.kernel
                        uptimeH: root.stats.uptime_h
                        uptimeM: root.stats.uptime_m
                    }
                    Separator {}
                    MediaBlock {
                        Layout.preferredWidth: root.colW2
                    }
                    Separator {}
                    NotesButton {
                        Layout.preferredWidth: root.notesW
                        onClicked: notesPopup.opened = !notesPopup.opened
                    }
                }
            }
        }
    }

    NotesPopup {
        id: notesPopup
        parent: root
        x: 0
        y: Theme.TRIGGER_ABOVE - height - 8
    }
}
