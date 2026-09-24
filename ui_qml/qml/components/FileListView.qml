import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Icons.js" as Icons

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
                text: Icons.glyph("folder_open")
                font.family: Icons.FONT_FAMILY
                font.pixelSize: 32
                color: theme.textMuted
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

    // Dosya Sayacı — sol üst köşe, Temizle butonuyla aynı hizada
    Text {
        text: {
            if (typeof bridge === "undefined" || !bridge || bridge.fileCount === 0) return ""
            if (bridge.fileCount === 1) return "1 dosya eklendi"
            return bridge.fileCount + " dosya eklendi"
        }
        font.family: theme.fontFamily
        font.pointSize: 9.5
        color: theme.textMuted
        anchors.left: parent.left
        anchors.leftMargin: 12
        anchors.verticalCenter: clearBtn.verticalCenter
        z: 2
    }

    // Temizle Butonu — sağ üst köşe
    ModernButton {
        id: clearBtn
        iconGlyph: "cancel"
        text: "Temizle"
        variant: "danger"
        pointSize: 9
        implicitHeight: 28
        visible: typeof bridge !== "undefined" && bridge && bridge.hasFiles
        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 6
        z: 2
        onClicked: {
            if (typeof bridge !== "undefined" && bridge) {
                bridge.clearFiles()
            }
        }
    }

    // Dosya Listesi
    ListView {
        id: listView
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.topMargin: clearBtn.visible ? clearBtn.implicitHeight + 12 : 4
        anchors.leftMargin: 4
        anchors.rightMargin: 4
        anchors.bottomMargin: 4
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
                    iconGlyph: "cancel"
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
