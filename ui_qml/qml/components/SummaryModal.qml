import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Icons.js" as Icons

Item {
    id: root

    anchors.fill: parent
    visible: opacity > 0
    opacity: (typeof bridge !== "undefined" && bridge && bridge.showSummaryModal) ? 1.0 : 0.0

    Behavior on opacity { NumberAnimation { duration: 200 } }

    // Backdrop
    Rectangle {
        anchors.fill: parent
        color: "#80000000"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (typeof bridge !== "undefined" && bridge) {
                    bridge.closeSummaryModal()
                }
            }
        }
    }

    // Modal Card
    Rectangle {
        id: card
        width: Math.min(parent.width - 40, 560)
        height: Math.min(parent.height - 40, 480)
        anchors.centerIn: parent
        radius: theme.radiusLarge
        color: theme.bgSurface
        border.color: theme.border
        border.width: 1

        scale: (typeof bridge !== "undefined" && bridge && bridge.showSummaryModal) ? 1.0 : 0.95
        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }

        MouseArea {
            anchors.fill: parent
            // Modal içindeki tıklamaların arka plana geçmesini engeller
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            // Başlık
            RowLayout {
                Layout.fillWidth: true

                Text {
                    text: "Dönüşüm Özeti"
                    font.family: theme.fontFamily
                    font.pointSize: 13
                    font.bold: true
                    color: theme.textPrimary
                    Layout.fillWidth: true
                }

                ModernButton {
                    iconGlyph: "cancel"
                    variant: "ghost"
                    pointSize: 11
                    implicitWidth: 32
                    implicitHeight: 32
                    radius: 16
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.closeSummaryModal()
                        }
                    }
                }
            }

            // İstatistik Kartları
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                // Toplam Kartı
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 70
                    radius: theme.radiusMedium
                    color: theme.bgElevated
                    border.color: theme.borderLight
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: (typeof bridge !== "undefined" && bridge && bridge.summaryData && bridge.summaryData.total !== undefined) ? bridge.summaryData.total : "0"
                            font.family: theme.fontFamily
                            font.pointSize: 16
                            font.bold: true
                            color: theme.textPrimary
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: "Toplam"
                            font.family: theme.fontFamily
                            font.pointSize: 9
                            color: theme.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }

                // Başarılı Kartı
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 70
                    radius: theme.radiusMedium
                    color: theme.bgElevated
                    border.color: theme.borderLight
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: (typeof bridge !== "undefined" && bridge && bridge.summaryData && bridge.summaryData.successCount !== undefined) ? bridge.summaryData.successCount : "0"
                            font.family: theme.fontFamily
                            font.pointSize: 16
                            font.bold: true
                            color: theme.success
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: "Başarılı"
                            font.family: theme.fontFamily
                            font.pointSize: 9
                            color: theme.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }

                // Hatalı Kartı
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 70
                    radius: theme.radiusMedium
                    color: theme.bgElevated
                    border.color: theme.borderLight
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 2
                        Text {
                            text: (typeof bridge !== "undefined" && bridge && bridge.summaryData && bridge.summaryData.failureCount !== undefined) ? bridge.summaryData.failureCount : "0"
                            font.family: theme.fontFamily
                            font.pointSize: 16
                            font.bold: true
                            color: theme.error
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: "Hatalı"
                            font.family: theme.fontFamily
                            font.pointSize: 9
                            color: theme.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            // Detay Listesi Başlığı
            Text {
                text: "Detaylar:"
                font.family: theme.fontFamily
                font.pointSize: 10
                font.bold: true
                color: theme.textSecondary
            }

            // Sonuç Listesi
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: theme.radiusMedium
                color: theme.bgElevated
                border.color: theme.borderLight
                border.width: 1
                clip: true

                ListView {
                    anchors.fill: parent
                    anchors.margins: 6
                    model: (typeof bridge !== "undefined" && bridge && bridge.summaryData && bridge.summaryData.results) ? bridge.summaryData.results : []
                    spacing: 4

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                        width: parent.width
                        height: 38
                        radius: theme.radiusSmall
                        color: theme.bgSurface

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 8

                            Text {
                                text: Icons.glyph(modelData.success ? "check" : "cancel")
                                font.family: Icons.FONT_FAMILY
                                font.pixelSize: 12
                                color: modelData.success ? theme.success : theme.error
                            }

                            Text {
                                text: modelData.fileName
                                font.family: theme.fontFamily
                                font.pointSize: 9
                                font.bold: true
                                color: theme.textPrimary
                                elide: Text.ElideRight
                                Layout.preferredWidth: 160
                            }

                            Text {
                                text: modelData.success ?
                                      ("→ " + modelData.outputName + (modelData.elapsedSeconds ? " (" + modelData.elapsedSeconds.toFixed(1) + "s)" : "")) :
                                      ("— " + modelData.errorMessage)
                                font.family: theme.fontFamily
                                font.pointSize: 9
                                color: modelData.success ? theme.textSecondary : theme.error
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }

            // Butonlar
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ModernButton {
                    iconGlyph: "folder_open"
                    text: "Klasörü Aç"
                    variant: "secondary"
                    pointSize: 10
                    implicitHeight: 40
                    visible: typeof bridge !== "undefined" && bridge && bridge.summaryData && bridge.summaryData.successCount > 0
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.openFirstOutputFolder()
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                ModernButton {
                    text: "Kapat"
                    variant: "primary"
                    pointSize: 10
                    implicitHeight: 40
                    implicitWidth: 90
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.closeSummaryModal()
                        }
                    }
                }
            }
        }
    }
}
