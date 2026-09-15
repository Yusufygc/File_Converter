import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    radius: theme.radiusMedium
    color: theme.bgSurface
    border.color: theme.border
    border.width: 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    // Boş Liste Durumu
    Item {
        anchors.fill: parent
        visible: typeof bridge === "undefined" || !bridge || bridge.fileCount === 0

        Column {
            anchors.centerIn: parent
            spacing: 8
            opacity: 0.5

            Text {
                text: "📁"
                font.pixelSize: 32
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Dönüştürülecek dosya bulunmuyor"
                font.family: theme.fontFamily
                font.pointSize: 10
                color: theme.textMuted
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // Dosya Listesi
    ListView {
        id: listView
        anchors.fill: parent
        anchors.margins: 4
        clip: true
        model: (typeof bridge !== "undefined" && bridge) ? bridge.fileListModel : null
        spacing: 4

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
        }

        delegate: Rectangle {
            id: fileRow
            width: listView.width
            height: 48
            radius: theme.radiusSmall
            color: rowMouse.containsMouse ? theme.bgHover : theme.bgElevated
            border.color: theme.borderLight
            border.width: 1

            Behavior on color { ColorAnimation { duration: 100 } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 12

                // File Icon
                Image {
                    source: iconUrl
                    Layout.preferredWidth: 22
                    Layout.preferredHeight: 22
                    sourceSize: Qt.size(22, 22)
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }

                // File Name
                Text {
                    text: name
                    font.family: theme.fontFamily
                    font.pointSize: 10
                    font.bold: true
                    color: theme.textPrimary
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter

                    ToolTip.visible: (status === "error" && errorMessage !== "") && rowMouse.containsMouse
                    ToolTip.text: errorMessage
                    ToolTip.delay: 300
                }

                // File Size
                Text {
                    text: sizeStr
                    font.family: theme.fontFamily
                    font.pointSize: 9
                    color: theme.textMuted
                    Layout.preferredWidth: 64
                    horizontalAlignment: Text.AlignRight
                    Layout.alignment: Qt.AlignVCenter
                }

                // Status Badge
                Rectangle {
                    Layout.preferredHeight: 24
                    Layout.preferredWidth: Math.max(statusTextItem.implicitWidth + 16, 76)
                    radius: 12
                    Layout.alignment: Qt.AlignVCenter

                    color: {
                        if (status === "converting") return theme.warning
                        if (status === "success") return theme.successDim
                        if (status === "error") return theme.errorDim
                        return "transparent"
                    }

                    Text {
                        id: statusTextItem
                        anchors.centerIn: parent
                        text: statusText
                        font.family: theme.fontFamily
                        font.pointSize: 9
                        font.bold: status !== "idle"

                        color: {
                            if (status === "converting") return "#FFFFFF"
                            if (status === "success") return theme.success
                            if (status === "error") return theme.error
                            return theme.textMuted
                        }
                    }
                }

                // Delete Single Row Button
                ModernButton {
                    text: "✕"
                    variant: "ghost"
                    pointSize: 9
                    implicitWidth: 26
                    implicitHeight: 26
                    radius: 13
                    enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                    Layout.alignment: Qt.AlignVCenter
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.removeFile(index)
                        }
                    }

                    ToolTip.visible: hovered
                    ToolTip.text: "Listeden Kaldır"
                    ToolTip.delay: 400
                }
            }

            MouseArea {
                id: rowMouse
                anchors.fill: parent
                hoverEnabled: true
                acceptedButtons: Qt.NoButton
            }
        }
    }
}
