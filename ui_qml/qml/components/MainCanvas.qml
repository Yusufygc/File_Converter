import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root

    spacing: 12

    // ── 1. DOSYA ALANI: DropZone, Dosya Listesi ──────────────────────────
    // Sürükle-Bırak Alanı (tıklanarak da dosya seçilebilir — ayrı "Dosya Ekle"
    // butonuna gerek yok)
    DropZone {
        Layout.fillWidth: true
    }

    // Dosya Listesi (Temizle butonu artık bu kutunun sağ üst köşesinde)
    FileListView {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }

    // ── 2. ALT AKSİYON ALANI: Seçenekler, Çıktı Klasörü, İlerleme, CTA ─────
    ColumnLayout {
        Layout.fillWidth: true
        spacing: 8

        // Format Bilgisi ve Seçenekler (Birleştirme & Sayfa Aralığı)
        ModernCard {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 10

                // Üst Satır: Aktif Format Bilgisi ve Rozetler
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    // Aktif Format Başlığı
                    Text {
                        text: {
                            if (typeof bridge === "undefined" || !bridge || !bridge.currentConverter) return "Dönüştürücü Seçin"
                            return bridge.currentConverter.displayName || "Dönüştürücü"
                        }
                        font.family: theme.fontFamily
                        font.pointSize: 11
                        font.bold: true
                        color: theme.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    // Desteklenen Uzantılar Rozeti
                    Rectangle {
                        Layout.preferredHeight: 24
                        Layout.preferredWidth: extText.implicitWidth + 16
                        radius: 12
                        color: theme.bgElevated
                        border.color: theme.borderLight
                        border.width: 1

                        Text {
                            id: extText
                            anchors.centerIn: parent
                            text: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                                  "Desteklenen: " + bridge.currentConverter.acceptedExtsStr : ""
                            font.family: theme.fontFamily
                            font.pointSize: 8.5
                            color: theme.textSecondary
                        }
                    }
                }

                // İkinci Satır: Özel Seçenekler (Birleştirme & Sayfa Aralığı)
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    visible: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                             (bridge.currentConverter.supportsMerge || bridge.currentConverter.supportsPageRange) : false

                    // Birleştirme Onay Kutusu (IMergeConverter)
                    ModernCheckBox {
                        id: mergeCheck
                        visible: typeof bridge !== "undefined" && bridge && bridge.currentConverter && bridge.currentConverter.supportsMerge
                        text: "Tüm dosyaları TEK çıktıda birleştir"
                        checked: typeof bridge !== "undefined" && bridge && bridge.isMergeMode
                        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                        onCheckedChanged: {
                            if (typeof bridge !== "undefined" && bridge) {
                                bridge.setIsMergeMode(checked)
                            }
                        }
                    }

                    // Sayfa Aralığı Girdisi (IPageRangeSelectable)
                    RowLayout {
                        visible: typeof bridge !== "undefined" && bridge && bridge.currentConverter && bridge.currentConverter.supportsPageRange
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: "Sayfa Aralığı:"
                            font.family: theme.fontFamily
                            font.pointSize: 9.5
                            color: theme.textSecondary
                        }

                        ModernTextField {
                            Layout.fillWidth: true
                            placeholderText: "örn: 1-3,5,7-9 (boş: tüm sayfalar)"
                            text: (typeof bridge !== "undefined" && bridge) ? bridge.pageRange : ""
                            enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                            onTextChanged: {
                                if (typeof bridge !== "undefined" && bridge) {
                                    bridge.setPageRange(text)
                                }
                            }
                        }
                    }
                }
            }
        }

        // Çıktı Klasörü Seçimi
        ModernCard {
            Layout.fillWidth: true

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: "Çıktı Klasörü:"
                    font.family: theme.fontFamily
                    font.pointSize: 9.5
                    color: theme.textSecondary
                    Layout.preferredWidth: 85
                }

                ModernTextField {
                    Layout.fillWidth: true
                    readOnly: true
                    placeholderText: "Kaynak dosyayla aynı klasör (varsayılan)"
                    text: (typeof bridge !== "undefined" && bridge) ? bridge.outputDir : ""
                }

                ModernButton {
                    text: "Gözat"
                    pointSize: 9.5
                    implicitHeight: 36
                    implicitWidth: 68
                    enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.browseOutputDir()
                        }
                    }
                }

                ModernButton {
                    iconGlyph: "cancel"
                    pointSize: 9.5
                    implicitHeight: 36
                    implicitWidth: 36
                    variant: "ghost"
                    enabled: typeof bridge !== "undefined" && bridge && bridge.outputDir !== "" && !bridge.isConverting
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.clearOutputDir()
                        }
                    }

                    ToolTip.visible: hovered && enabled
                    ToolTip.text: "Varsayılan konuma sıfırla"
                    ToolTip.delay: 300
                }
            }
        }

        // İlerleme Çubuğu
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 14
            visible: typeof bridge !== "undefined" && bridge && bridge.isConverting

            Rectangle {
                anchors.fill: parent
                radius: 7
                color: theme.bgElevated
                border.color: theme.borderLight
                border.width: 1

                Rectangle {
                    height: parent.height
                    width: parent.width * ((typeof bridge !== "undefined" && bridge && bridge.progressMax > 0) ?
                           bridge.progressValue / bridge.progressMax : 0)
                    radius: 7
                    color: theme.accent

                    Behavior on width { NumberAnimation { duration: 150 } }
                }
            }
        }

        // Büyük CTA Dönüştür Butonu
        ModernButton {
            id: ctaBtn
            Layout.fillWidth: true
            implicitHeight: 46
            pointSize: 11.5
            bold: true
            radius: theme.radiusMedium
            variant: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "danger" : "primary"
            iconGlyph: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "cancel" : ""
            text: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "Dönüştürmeyi İptal Et" : "Dönüştürmeyi Başlat"
            enabled: typeof bridge !== "undefined" && bridge && (bridge.isConverting || bridge.hasFiles)

            onClicked: {
                if (typeof bridge !== "undefined" && bridge) {
                    if (bridge.isConverting) {
                        bridge.cancelConversion()
                    } else {
                        bridge.startConversion()
                    }
                }
            }
        }
    }
}
