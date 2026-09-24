import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../Icons.js" as Icons

ScrollView {
    id: root

    clip: true
    contentWidth: availableWidth

    signal backRequested()

    ScrollBar.vertical: ScrollBar {
        policy: ScrollBar.AsNeeded
    }

    Item {
        width: root.availableWidth
        implicitHeight: contentCol.implicitHeight + 40

        ColumnLayout {
            id: contentCol
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.min(parent.width - 40, 680)
            spacing: 16

            Item { Layout.preferredHeight: 4 }

            // ── Üst Başlık ────────────────────────────────────────────
            Column {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                spacing: 2

                Text {
                    text: "Ayarlar ve Tercihler"
                    font.family: theme.fontFamily
                    font.pointSize: 13
                    font.bold: true
                    color: theme.textPrimary
                    anchors.horizontalCenter: parent.horizontalCenter
                    horizontalAlignment: Text.AlignHCenter
                }

                Text {
                    text: "Dönüşüm motoru, kalite parametreleri ve OCR yapılandırması"
                    font.family: theme.fontFamily
                    font.pointSize: 9
                    color: theme.textMuted
                    anchors.horizontalCenter: parent.horizontalCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: theme.border
            }

            // ── KART 1: Dönüşüm Motoru ───────────────────────────────
            ModernCard {
                Layout.fillWidth: true
                title: "Dönüşüm Motoru"

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: "Motor:"
                        font.family: theme.fontFamily
                        font.pointSize: 10
                        color: theme.textSecondary
                        Layout.preferredWidth: 60
                    }

                    Loader {
                        Layout.fillWidth: true
                        sourceComponent: (typeof bridge !== "undefined" && bridge && bridge.currentConverter && bridge.currentConverter.supportsEngineSelect) ?
                                         engineComboComp : engineStaticComp
                    }

                    Component {
                        id: engineComboComp
                        ModernComboBox {
                            model: (typeof bridge !== "undefined" && bridge) ? bridge.engineList : []
                            textRoleKey: "name"
                            currentIndex: (typeof bridge !== "undefined" && bridge) ? bridge.selectedEngineIndex : 0
                            onActivated: function(index) {
                                if (typeof bridge !== "undefined" && bridge) {
                                    bridge.selectEngine(index)
                                }
                            }
                        }
                    }

                    Component {
                        id: engineStaticComp
                        Rectangle {
                            height: 38
                            Layout.fillWidth: true
                            color: theme.bgInput
                            border.color: theme.borderLight
                            border.width: 1
                            radius: theme.radiusSmall

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.left: parent.left
                                anchors.leftMargin: 12
                                anchors.right: parent.right
                                anchors.rightMargin: 12
                                text: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                                      bridge.currentConverter.activeEngineName : ""
                                font.family: theme.fontFamily
                                font.pointSize: 10
                                color: theme.textPrimary
                                elide: Text.ElideRight
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: "Durum:"
                        font.family: theme.fontFamily
                        font.pointSize: 10
                        color: theme.textSecondary
                        Layout.preferredWidth: 60
                    }

                    Row {
                        spacing: 6
                        Layout.alignment: Qt.AlignVCenter

                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: (typeof bridge !== "undefined" && bridge && bridge.engineIsAvailable) ? theme.success : theme.error
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: (typeof bridge !== "undefined" && bridge) ? bridge.engineStatusText.replace("●", "").trim() : "—"
                            font.family: theme.fontFamily
                            font.pointSize: 10
                            font.bold: true
                            color: (typeof bridge !== "undefined" && bridge && bridge.engineIsAvailable) ? theme.success : theme.error
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }

            // ── KART 2: Kalite Ayarları ──────────────────────────────
            ModernCard {
                Layout.fillWidth: true
                title: "Kalite Ayarları"

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    Text {
                        text: "DPI:"
                        font.family: theme.fontFamily
                        font.pointSize: 10
                        color: theme.textSecondary
                        Layout.preferredWidth: 60
                    }

                    ModernSpinBox {
                        from: 72
                        to: 600
                        stepSize: 25
                        value: (typeof bridge !== "undefined" && bridge) ? bridge.dpi : 150
                        suffix: "dpi"
                        Layout.preferredWidth: 130
                        onValueModified: {
                            if (typeof bridge !== "undefined" && bridge) {
                                bridge.setDpi(value)
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: "Kalite:"
                        font.family: theme.fontFamily
                        font.pointSize: 10
                        color: theme.textSecondary
                    }

                    ModernSpinBox {
                        from: 1
                        to: 100
                        stepSize: 5
                        value: (typeof bridge !== "undefined" && bridge) ? bridge.quality : 90
                        suffix: "%"
                        Layout.preferredWidth: 110
                        onValueModified: {
                            if (typeof bridge !== "undefined" && bridge) {
                                bridge.setQuality(value)
                            }
                        }
                    }
                }

                ModernCheckBox {
                    Layout.fillWidth: true
                    Layout.leftMargin: 72
                    text: "Mevcut çıktı dosyalarının üzerine yaz"
                    checked: typeof bridge !== "undefined" && bridge && bridge.overwriteExisting
                    onCheckedChanged: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.setOverwriteExisting(checked)
                        }
                    }
                }
            }

            // ── KART 3: OCR Motoru Bilgisi ───────────────────────────
            ModernCard {
                Layout.fillWidth: true
                title: "OCR (Optik Karakter Tanıma)"

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        text: "Tesseract:"
                        font.family: theme.fontFamily
                        font.pointSize: 10
                        color: theme.textSecondary
                        Layout.preferredWidth: 60
                    }

                    Rectangle {
                        height: 26
                        width: ocrStatusRow.implicitWidth + 16
                        radius: 13
                        color: (typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ? theme.successDim : theme.errorDim

                        Row {
                            id: ocrStatusRow
                            anchors.centerIn: parent
                            spacing: 6

                            Text {
                                text: Icons.glyph((typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ? "check" : "cancel")
                                font.family: Icons.FONT_FAMILY
                                font.pointSize: 9
                                color: (typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ? theme.success : theme.error
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: (typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ?
                                      "Tesseract OCR Hazır" : "Tesseract OCR Kurulu Değil"
                                font.family: theme.fontFamily
                                font.pointSize: 9
                                font.bold: true
                                color: (typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ? theme.success : theme.error
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    Layout.leftMargin: 72
                    text: (typeof bridge !== "undefined" && bridge && bridge.isOcrAvailable) ?
                          "Taranmış belge PDF'leri dönüştürülürken Türkçe ve İngilizce OCR motoru aktif olarak kullanılacaktır." :
                          "Taranmış PDF'lerde resimdeki yazıları düzenlenebilir Word metnine dönüştürmek için PowerShell'den kurabilirsiniz:\nwinget install UB-Mannheim.TesseractOCR"
                    font.family: theme.fontFamily
                    font.pointSize: 9
                    color: theme.textMuted
                    wrapMode: Text.WordWrap
                }
            }

            Item { Layout.preferredHeight: 12 }
        }
    }
}
