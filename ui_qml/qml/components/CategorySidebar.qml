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

    property string searchText: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        // ── Üst Arama & Başlık Alanı ─────────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Dönüştürücüler"
                font.family: theme.fontFamily
                font.pointSize: 11
                font.bold: true
                color: theme.textPrimary
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.preferredHeight: 22
                Layout.preferredWidth: countText.implicitWidth + 14
                radius: 11
                color: theme.bgElevated
                border.color: theme.borderLight
                border.width: 1

                Text {
                    id: countText
                    anchors.centerIn: parent
                    text: (typeof bridge !== "undefined" && bridge && bridge.converters) ? bridge.converters.length : "0"
                    font.family: theme.fontFamily
                    font.pointSize: 9
                    font.bold: true
                    color: theme.textMuted
                }
            }
        }

        // Arama Çubuğu
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            radius: theme.radiusSmall
            color: searchInput.activeFocus ? theme.bgInput : theme.bgElevated
            border.color: searchInput.activeFocus ? theme.accent : theme.borderLight
            border.width: 1

            Behavior on border.color { ColorAnimation { duration: 150 } }
            Behavior on color { ColorAnimation { duration: 150 } }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 8
                spacing: 6

                Text {
                    text: Icons.glyph("search")
                    font.family: Icons.FONT_FAMILY
                    font.pixelSize: 12
                    color: theme.textMuted
                    opacity: 0.6
                }

                TextInput {
                    id: searchInput
                    Layout.fillWidth: true
                    font.family: theme.fontFamily
                    font.pointSize: 9.5
                    color: theme.textPrimary
                    clip: true
                    selectByMouse: true

                    Text {
                        text: "Format ara... (örn: pdf, docx)"
                        font.family: theme.fontFamily
                        font.pointSize: 9.5
                        color: theme.textMuted
                        visible: !searchInput.text && !searchInput.activeFocus
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    onTextChanged: {
                        root.searchText = text.trim().toLowerCase()
                    }
                }

                Text {
                    text: Icons.glyph("cancel")
                    font.family: Icons.FONT_FAMILY
                    font.pixelSize: 11
                    color: theme.textMuted
                    visible: searchInput.text.length > 0
                    opacity: clearSearchMouse.containsMouse ? 1.0 : 0.6

                    MouseArea {
                        id: clearSearchMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            searchInput.text = ""
                            root.searchText = ""
                        }
                    }
                }
            }
        }

        // Ayraç Çizgisi
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: theme.borderLight
            opacity: 0.6
        }

        // ── Kategorize Edilmiş Format Listesi (Açılır / Kapanır Akordeon) ──
        ScrollView {
            id: categoryScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }

            ColumnLayout {
                width: categoryScroll.width - (categoryScroll.ScrollBar.vertical.visible ? 12 : 0)
                spacing: 10

                Repeater {
                    model: (typeof bridge !== "undefined" && bridge) ? bridge.categorizedConverters : []

                    delegate: ColumnLayout {
                        id: catColumn
                        Layout.fillWidth: true
                        spacing: 4

                        property bool isExpanded: true
                        readonly property bool isEffectiveExpanded: root.searchText !== "" ? true : isExpanded

                        // Bu kategoride arama ile eşleşen öğe var mı?
                        readonly property var filteredItems: {
                            var items = modelData.items || []
                            if (!root.searchText) return items
                            return items.filter(function(item) {
                                var s = root.searchText
                                return (item.displayName && item.displayName.toLowerCase().indexOf(s) !== -1) ||
                                       (item.shortName && item.shortName.toLowerCase().indexOf(s) !== -1) ||
                                       (item.sourceExt && item.sourceExt.toLowerCase().indexOf(s) !== -1) ||
                                       (item.targetExt && item.targetExt.toLowerCase().indexOf(s) !== -1) ||
                                       (item.badge && item.badge.toLowerCase().indexOf(s) !== -1)
                            })
                        }

                        visible: filteredItems.length > 0

                        // ── Kategori Başlığı (Tıklanabilir Açılır / Kapanır Düğme) ──
                        Rectangle {
                            id: catHeader
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            radius: theme.radiusSmall
                            color: headerMouse.containsMouse ? theme.bgHover : "transparent"
                            border.color: headerMouse.containsMouse ? theme.borderLight : "transparent"
                            border.width: 1

                            Behavior on color { ColorAnimation { duration: 120 } }
                            Behavior on border.color { ColorAnimation { duration: 120 } }

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                spacing: 6

                                Text {
                                    text: Icons.glyph(modelData.icon || "document")
                                    font.family: Icons.FONT_FAMILY
                                    font.pixelSize: 13
                                    color: theme.textPrimary
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                Text {
                                    text: (modelData.title || "").toUpperCase()
                                    font.family: theme.fontFamily
                                    font.pointSize: 10
                                    font.weight: Font.ExtraBold
                                    font.letterSpacing: 0.8
                                    color: theme.textPrimary
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignVCenter
                                }

                                Rectangle {
                                    Layout.preferredHeight: 18
                                    Layout.preferredWidth: catCountText.implicitWidth + 10
                                    radius: 9
                                    color: theme.bgElevated
                                    Layout.alignment: Qt.AlignVCenter

                                    Text {
                                        id: catCountText
                                        anchors.centerIn: parent
                                        text: catColumn.filteredItems.length
                                        font.family: theme.fontFamily
                                        font.pointSize: 8
                                        font.bold: true
                                        color: theme.textMuted
                                    }
                                }

                                Text {
                                    text: "▾"
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: headerMouse.containsMouse ? theme.textPrimary : theme.textMuted
                                    Layout.alignment: Qt.AlignVCenter
                                    transformOrigin: Item.Center
                                    rotation: catColumn.isEffectiveExpanded ? 0 : -90

                                    Behavior on rotation { NumberAnimation { duration: 160 } }
                                }
                            }

                            MouseArea {
                                id: headerMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    catColumn.isExpanded = !catColumn.isExpanded
                                }
                            }
                        }

                        // ── Kategori İçi Format Düğmeleri (İçerik Listesi) ──
                        ColumnLayout {
                            id: itemsContainer
                            Layout.fillWidth: true
                            spacing: 3
                            visible: catColumn.isEffectiveExpanded

                            Repeater {
                                model: catColumn.filteredItems

                                delegate: Rectangle {
                                    id: itemBtn
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 38
                                    radius: theme.radiusSmall

                                    readonly property bool isSelected: (typeof bridge !== "undefined" && bridge) &&
                                                                       bridge.currentConverterIndex === modelData.index

                                    color: isSelected ?
                                           theme.accentDim :
                                           (itemMouse.containsMouse ? theme.bgHover : "transparent")

                                    border.color: isSelected ? theme.accent : "transparent"
                                    border.width: isSelected ? 1 : 0

                                    Behavior on color { ColorAnimation { duration: 120 } }
                                    Behavior on border.color { ColorAnimation { duration: 120 } }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 8
                                        anchors.rightMargin: 8
                                        spacing: 8

                                        // Aktif Seçim Gösterge Çizgisi
                                        Rectangle {
                                            Layout.preferredWidth: 3
                                            Layout.preferredHeight: 18
                                            radius: 1.5
                                            color: theme.accent
                                            visible: itemBtn.isSelected
                                        }

                                        // Format İkonu
                                        Text {
                                            text: Icons.glyph(modelData.icon || "document")
                                            font.family: Icons.FONT_FAMILY
                                            font.pixelSize: 14
                                            color: itemBtn.isSelected ?
                                                   (theme.isDark ? "#FFFFFF" : theme.accent) :
                                                   theme.textPrimary
                                            Layout.alignment: Qt.AlignVCenter
                                        }

                                        // Format Adı
                                        Text {
                                            text: modelData.shortName || modelData.displayName
                                            font.family: theme.fontFamily
                                            font.pointSize: 9.5
                                            font.bold: itemBtn.isSelected
                                            color: itemBtn.isSelected ?
                                                   (theme.isDark ? "#FFFFFF" : theme.accent) :
                                                   theme.textPrimary
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                            Layout.alignment: Qt.AlignVCenter
                                        }

                                        // Hedef Format Rozeti (Pill Badge)
                                        Rectangle {
                                            Layout.preferredHeight: 20
                                            Layout.preferredWidth: badgeText.implicitWidth + 10
                                            radius: 4
                                            Layout.alignment: Qt.AlignVCenter

                                            color: itemBtn.isSelected ?
                                                   theme.accent :
                                                   theme.bgElevated
                                            border.color: itemBtn.isSelected ? "transparent" : theme.borderLight
                                            border.width: 1

                                            Text {
                                                id: badgeText
                                                anchors.centerIn: parent
                                                text: modelData.badge || ""
                                                font.family: theme.fontFamily
                                                font.pointSize: 8
                                                font.bold: true
                                                color: itemBtn.isSelected ?
                                                       "#FFFFFF" :
                                                       theme.textSecondary
                                            }
                                        }
                                    }

                                    MouseArea {
                                        id: itemMouse
                                        anchors.fill: parent
                                        hoverEnabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                                        cursorShape: (typeof bridge !== "undefined" && bridge && bridge.isConverting) ?
                                                     Qt.ArrowCursor : Qt.PointingHandCursor
                                        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting

                                        onClicked: {
                                            if (typeof bridge !== "undefined" && bridge) {
                                                bridge.selectConverter(modelData.index)
                                            }
                                        }
                                    }

                                    ToolTip.visible: itemMouse.containsMouse && !itemBtn.isSelected
                                    ToolTip.text: modelData.displayName
                                    ToolTip.delay: 450
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
