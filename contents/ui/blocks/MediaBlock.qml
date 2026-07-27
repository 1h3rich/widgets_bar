import QtQuick
import QtQuick.Layouts
import org.kde.plasma.private.mpris as Mpris
import "../Theme.js" as Theme

BlockFrame {
    id: root
    title: "Multimedia"

    Text {
        visible: mediaRepeater.count === 0
        text: "Sin reproducción"
        color: Theme.TEXT_SEC
        font.pixelSize: 11
    }

    Repeater {
        id: mediaRepeater
        model: Mpris.MultiplexerModel {}

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Text {
                Layout.fillWidth: true
                Layout.maximumWidth: 200
                elide: Text.ElideRight
                text: model.track && model.track.length > 0 ? model.track : "Sin título"
                color: Theme.TEXT_PRI
                font.pixelSize: 11
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                Layout.maximumWidth: 200
                elide: Text.ElideRight
                text: model.artist || ""
                color: Theme.TEXT_SEC
                font.pixelSize: 9
            }
            RowLayout {
                spacing: 5
                MediaButton {
                    text: "◀◀"
                    enabled: model.canGoPrevious
                    onClicked: model.container.Previous()
                }
                MediaButton {
                    text: model.playbackStatus === Mpris.PlaybackStatus.Playing ? "⏸" : "▶"
                    enabled: model.canPlay || model.canPause
                    onClicked: model.container.PlayPause()
                }
                MediaButton {
                    text: "▶▶"
                    enabled: model.canGoNext
                    onClicked: model.container.Next()
                }
                Item { Layout.fillWidth: true }
            }
        }
    }

    Item { Layout.fillHeight: true }
}
