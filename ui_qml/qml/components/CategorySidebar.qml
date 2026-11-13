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
    // Listedeki dosyaların türü (".pdf"); doluyken yalnızca o türü kabul eden araçlar görünür.
    readonly property string fileFilter: (typeof bridge !== "undefined" && bridge) ? bridge.fileTypeFilter : ""
    // Akordeon: aynı anda tek grup açık; başlangıçta ve araç değişince etkin aracın grubu.
    property string expandedGroup: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                                   bridge.currentConverter.group : ""

    function matches(item) {
        if (root.fileFilter && (item.acceptedTypes || []).indexOf(root.fileFilter) === -1)
            return false
        if (!root.searchText)
            return true
        var s = root.searchText
        return (item.displayName && item.displayName.toLowerCase().indexOf(s) !== -1) ||
               (item.shortName && item.shortName.toLowerCase().indexOf(s) !== -1) ||
               (item.sourceExt && item.sourceExt.toLowerCase().indexOf(s) !== -1) ||
               (item.targetExt && item.targetExt.toLowerCase().indexOf(s) !== -1) ||
               (item.badge && item.badge.toLowerCase().indexOf(s) !== -1)
    }

    readonly property int visibleCount: {
        var cats = (typeof bridge !== "undefined" && bridge) ? bridge.categorizedConverters : []
        var n = 0
        for (var i = 0; i < cats.length; i++)
            n += cats[i].items.filter(root.matches).length
        return n
    }

    Connections {
        target: (typeof bridge !== "undefined") ? bridge : null
        function onCurrentConverterChanged() {
            if (bridge.currentConverter) root.expandedGroup = bridge.currentConverter.group
        }
    }

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
                    text: (root.searchText || root.fileFilter) ?
                          root.visibleCount + " / " + ((typeof bridge !== "undefined" && bridge && bridge.converters) ? bridge.converters.length : 0) :
                          ((typeof bridge !== "undefined" && bridge && bridge.converters) ? bridge.converters.length : "0")
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

        // Dosya türü süzgeci şeridi (dosya-önce akışı)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: filterRow.implicitHeight + 12
            visible: root.fileFilter !== ""
            radius: theme.radiusSmall
            color: theme.accentDim
            border.color: theme.borderLight
            border.width: 1

            RowLayout {
                id: filterRow
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 6
                spacing: 6

                Text {
                    Layout.fillWidth: true
                    text: ((typeof bridge !== "undefined" && bridge) ? bridge.fileTypeLabel : "") +
                          " dosyaları için uygun araçlar"
                    font.family: theme.fontFamily
                    font.pointSize: 9
                    font.bold: true
                    color: theme.textPrimary
                    wrapMode: Text.WordWrap
                }

                Text {
                    text: "Listeyi temizle"
                    font.family: theme.fontFamily
                    font.pointSize: 8.5
                    font.underline: clearFilterMouse.containsMouse
                    color: theme.textSecondary

                    MouseArea {
                        id: clearFilterMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
                        onClicked: bridge.clearFiles()
                    }
                }
            }
        }

        // Ayraç Çizgisi
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: theme.border
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

                        // Arama ya da dosya süzgeci varken eşleşen tüm gruplar açık; yoksa tek grup (akordeon).
                        readonly property bool isEffectiveExpanded: (root.searchText !== "" || root.fileFilter !== "") ?
                                                                    true : root.expandedGroup === modelData.id

                        // Bu kategoride arama ve dosya türüyle eşleşen öğeler
                        readonly property var filteredItems: (modelData.items || []).filter(root.matches)

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
                                    font.letterSpacing: 0.3
                                    color: theme.textPrimary
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignVCenter
                                    elide: Text.ElideRight
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
                                    root.expandedGroup = (root.expandedGroup === modelData.id) ? "" : modelData.id
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
                                            color: itemBtn.isSelected ? theme.accent : theme.textPrimary
                                            Layout.alignment: Qt.AlignVCenter
                                        }

                                        // Format Adı
                                        Text {
                                            text: modelData.shortName || modelData.displayName
                                            font.family: theme.fontFamily
                                            font.pointSize: 9.5
                                            font.bold: itemBtn.isSelected
                                            color: itemBtn.isSelected ? theme.accent : theme.textPrimary
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
                                                       (theme.isDark ? theme.gunmetal : "#FFFFFF") :
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
