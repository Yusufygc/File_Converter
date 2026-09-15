import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    implicitHeight: 110
    radius: theme.radiusMedium
    color: dropArea.containsDrag ? theme.accentGlow : (mouseArea.containsMouse ? theme.bgHover : theme.bgSurface)
    border.color: dropArea.containsDrag ? theme.accent : (mouseArea.containsMouse ? theme.accent : theme.borderLight)
    border.width: dropArea.containsDrag || mouseArea.containsMouse ? 1.5 : 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    Column {
        anchors.centerIn: parent
        spacing: 6

        // Icon
        Image {
            source: (typeof bridge !== "undefined" && bridge) ? bridge.appIconUrl : ""
            width: 32
            height: 32
            anchors.horizontalCenter: parent.horizontalCenter
            sourceSize: Qt.size(32, 32)
            fillMode: Image.PreserveAspectFit
            opacity: dropArea.containsDrag || mouseArea.containsMouse ? 1.0 : 0.8
        }

        // Primary text
        Text {
            text: "Dosyaları veya bir klasörü buraya sürükleyin ya da tıklayın"
            font.family: theme.fontFamily
            font.pointSize: 10
            font.bold: true
            color: theme.textPrimary
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // Accepted extensions label
        Text {
            text: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                  bridge.currentConverter.acceptedExtsStr : ""
            font.family: theme.fontFamily
            font.pointSize: 9
            color: theme.textMuted
            font.letterSpacing: 0.5
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    DropArea {
        id: dropArea
        anchors.fill: parent
        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting

        onDropped: function(drop) {
            if (drop.hasUrls && typeof bridge !== "undefined" && bridge) {
                bridge.addFilesFromUrls(drop.urls)
                drop.acceptProposedAction()
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
        cursorShape: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ?
                     Qt.ArrowCursor : Qt.PointingHandCursor
        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
        onClicked: {
            if (typeof bridge !== "undefined" && bridge) {
                bridge.openFileDialog()
            }
        }
    }
}
