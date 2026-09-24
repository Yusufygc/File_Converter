import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: root

    clip: true
    contentWidth: availableWidth

    ScrollBar.vertical: ScrollBar {
        policy: ScrollBar.AsNeeded
    }

    ColumnLayout {
        width: root.availableWidth
        spacing: 14

        // ── KART 1: Dönüşüm Türü ─────────────────────────────────────
        ModernCard {
            Layout.fillWidth: true
            title: "Dönüşüm Türü"

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Text {
                    text: "Format:"
                    font.family: theme.fontFamily
                    font.pointSize: 10
                    color: theme.textSecondary
                    Layout.preferredWidth: 55
                }

                ModernComboBox {
                    id: convCombo
                    Layout.fillWidth: true
                    model: (typeof bridge !== "undefined" && bridge) ? bridge.converters : []
                    textRoleKey: "displayName"
                    currentIndex: (typeof bridge !== "undefined" && bridge) ? bridge.currentConverterIndex : 0
                    onActivated: function(index) {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.selectConverter(index)
                        }
                    }
                }
            }

            // Birleştirme Onay Kutusu (IMergeConverter)
            ModernCheckBox {
                id: mergeCheck
                visible: typeof bridge !== "undefined" && bridge && bridge.currentConverter && bridge.currentConverter.supportsMerge
                Layout.fillWidth: true
                Layout.leftMargin: 65
                text: "Tüm dosyaları TEK çıktıda birleştir"
                checked: typeof bridge !== "undefined" && bridge && bridge.isMergeMode
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
                spacing: 10

                Text {
                    text: "Aralık:"
                    font.family: theme.fontFamily
                    font.pointSize: 10
                    color: theme.textSecondary
                    Layout.preferredWidth: 55
                }

                ModernTextField {
                    Layout.fillWidth: true
                    placeholderText: "örn: 1-3,5,7-9 (boş: tüm sayfalar)"
                    text: (typeof bridge !== "undefined" && bridge) ? bridge.pageRange : ""
                    onTextChanged: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.setPageRange(text)
                        }
                    }
                }
            }
        }

        // ── KART 2: Çıktı Konumu ─────────────────────────────────────
        ModernCard {
            Layout.fillWidth: true
            title: "Çıktı Konumu"

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Text {
                    text: "Klasör:"
                    font.family: theme.fontFamily
                    font.pointSize: 10
                    color: theme.textSecondary
                    Layout.preferredWidth: 55
                }

                ModernTextField {
                    Layout.fillWidth: true
                    readOnly: true
                    placeholderText: "Kaynak dosyayla aynı klasör (varsayılan)"
                    text: (typeof bridge !== "undefined" && bridge) ? bridge.outputDir : ""
                }

                ModernButton {
                    text: "Gözat"
                    pointSize: 10
                    implicitHeight: 38
                    implicitWidth: 68
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.browseOutputDir()
                        }
                    }
                }

                ModernButton {
                    iconGlyph: "cancel"
                    pointSize: 10
                    implicitHeight: 38
                    implicitWidth: 38
                    variant: "ghost"
                    enabled: typeof bridge !== "undefined" && bridge && bridge.outputDir !== ""
                    onClicked: {
                        if (typeof bridge !== "undefined" && bridge) {
                            bridge.clearOutputDir()
                        }
                    }
                }
            }
        }

        Item { Layout.preferredHeight: 4 }

        // ── CTA: Dönüştür / İptal Et Butonu ─────────────────────────
        ModernButton {
            id: ctaBtn
            Layout.fillWidth: true
            implicitHeight: 48
            pointSize: 12
            bold: true
            radius: theme.radiusMedium
            variant: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "danger" : "primary"
            iconGlyph: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "cancel" : "convert"
            text: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ? "İptal Et" : "Dönüştür"
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

        Item { Layout.preferredHeight: 8 }
    }
}
