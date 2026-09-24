import QtQuick
import QtQuick.Controls
import "../Icons.js" as Icons

Item {
    id: root

    property string text: ""
    property string iconSource: ""
    property string iconGlyph: ""
    property string variant: "secondary" // primary | secondary | danger | ghost | accent_outline
    property bool enabled: true
    property real pointSize: 11
    property bool bold: true
    property int radius: theme.radiusSmall
    property alias hovered: mouseArea.containsMouse

    signal clicked()

    implicitWidth: contentRow.implicitWidth + 28
    implicitHeight: 38

    opacity: enabled ? 1.0 : 0.5
    Behavior on opacity { NumberAnimation { duration: 150 } }

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: root.radius
        border.width: 1

        color: {
            if (!root.enabled) {
                return (root.variant === "primary") ? theme.bgElevated : "transparent"
            }
            if (root.variant === "primary") {
                return mouseArea.pressed ? Qt.darker(theme.accent, 1.1) :
                       mouseArea.containsMouse ? theme.accentHover : theme.accent
            } else if (root.variant === "danger") {
                return mouseArea.pressed ? Qt.darker(theme.errorDim, 1.2) :
                       mouseArea.containsMouse ? theme.errorDim : "transparent"
            } else if (root.variant === "accent_outline") {
                return mouseArea.pressed ? Qt.darker(theme.accentDim, 1.1) :
                       mouseArea.containsMouse ? theme.accentDim : "transparent"
            } else if (root.variant === "ghost") {
                return mouseArea.containsMouse ? theme.bgHover : "transparent"
            } else { // secondary
                return mouseArea.pressed ? theme.bgCard :
                       mouseArea.containsMouse ? theme.bgHover : theme.bgElevated
            }
        }

        border.color: {
            if (!root.enabled) return theme.border
            if (root.variant === "primary") return "transparent"
            if (root.variant === "danger") {
                return mouseArea.containsMouse ? theme.error : theme.errorDim
            }
            if (root.variant === "accent_outline") {
                return mouseArea.containsMouse ? theme.accent : theme.accentDim
            }
            if (root.variant === "ghost") return "transparent"
            return mouseArea.containsMouse ? theme.textMuted : theme.borderLight
        }

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }
    }

    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: 8

        Image {
            id: icon
            visible: root.iconSource !== ""
            source: root.iconSource
            width: 16
            height: 16
            anchors.verticalCenter: parent.verticalCenter
            sourceSize: Qt.size(16, 16)
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: glyphIcon
            visible: root.iconGlyph !== ""
            text: Icons.glyph(root.iconGlyph)
            font.family: Icons.FONT_FAMILY
            font.pointSize: root.pointSize + 1
            anchors.verticalCenter: parent.verticalCenter
            color: label.color
        }

        Text {
            id: label
            visible: root.text !== ""
            text: root.text
            font.family: theme.fontFamily
            font.pointSize: root.pointSize
            font.bold: root.bold
            anchors.verticalCenter: parent.verticalCenter

            color: {
                if (!root.enabled) return theme.textMuted
                if (root.variant === "primary") return "#FFFFFF"
                if (root.variant === "danger") return theme.error
                if (root.variant === "accent_outline") return theme.accent
                return theme.textPrimary
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: root.enabled
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled
        onClicked: root.clicked()
    }
}
