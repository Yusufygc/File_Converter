import QtQuick
import QtQuick.Controls

Rectangle {
    id: root

    property bool isSettingsPage: false
    signal settingsToggleClicked()

    height: 56
    color: theme.bgSurface
    border.color: theme.border
    border.width: 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        // App Logo
        Image {
            source: (typeof bridge !== "undefined" && bridge) ? bridge.appIconUrl : ""
            width: 28
            height: 28
            anchors.verticalCenter: parent.verticalCenter
            sourceSize: Qt.size(28, 28)
            fillMode: Image.PreserveAspectFit
        }

        // Title
        Text {
            text: "FileConvert"
            font.family: theme.fontFamily
            font.pointSize: 13
            font.bold: true
            color: theme.textPrimary
            anchors.verticalCenter: parent.verticalCenter
        }

        // Active Format Badge
        Rectangle {
            id: formatBadge
            height: 24
            width: badgeText.implicitWidth + 16
            radius: 4
            color: theme.accentDim
            border.color: theme.isDark ? theme.coolGrey : theme.lightSlateGray
            border.width: 1
            anchors.verticalCenter: parent.verticalCenter

            Text {
                id: badgeText
                anchors.centerIn: parent
                text: (typeof bridge !== "undefined" && bridge && bridge.currentConverter) ?
                      bridge.currentConverter.displayName.toUpperCase() : ""
                font.family: theme.fontFamily
                font.pointSize: 9
                font.bold: true
                color: theme.accent
                font.letterSpacing: 0.8
            }
        }
    }

    // Right action buttons (Settings + Theme)
    Row {
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        // Settings Button (Left of Theme Button)
        ModernButton {
            width: 36
            height: 36
            radius: 18
            iconGlyph: root.isSettingsPage ? "back" : "settings"
            pointSize: root.isSettingsPage ? 14 : 12
            variant: root.isSettingsPage ? "secondary" : "ghost"
            onClicked: root.settingsToggleClicked()

            ToolTip.visible: hovered
            ToolTip.text: root.isSettingsPage ? "Ana Sayfaya Dön" : "Ayarlar"
            ToolTip.delay: 400
        }

        // Theme Switch Button
        ModernButton {
            width: 36
            height: 36
            radius: 18
            iconGlyph: theme.isDark ? "theme_light" : "theme_dark"
            pointSize: 13
            variant: "ghost"
            onClicked: {
                if (typeof bridge !== "undefined" && bridge) {
                    bridge.toggleTheme()
                }
            }

            ToolTip.visible: hovered
            ToolTip.text: theme.isDark ? "Açık Temaya Geç" : "Koyu Temaya Geç"
            ToolTip.delay: 400
        }
    }
}
