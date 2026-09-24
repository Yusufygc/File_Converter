import QtQuick
import QtQuick.Controls
import "../Icons.js" as Icons

CheckBox {
    id: control

    font.family: theme.fontFamily
    font.pointSize: 10
    implicitHeight: 28

    indicator: Rectangle {
        implicitWidth: 18
        implicitHeight: 18
        x: control.leftPadding
        anchors.verticalCenter: parent.verticalCenter
        radius: 4
        color: control.checked ? theme.accent : theme.bgInput
        border.color: control.checked ? theme.accent : (control.hovered ? theme.accentHover : theme.borderLight)
        border.width: 1.5

        Text {
            anchors.centerIn: parent
            text: Icons.glyph("check")
            font.family: Icons.FONT_FAMILY
            font.pixelSize: 12
            font.bold: true
            color: theme.isDark ? theme.gunmetal : "#FFFFFF"
            visible: control.checked
        }

        Behavior on color { ColorAnimation { duration: 120 } }
        Behavior on border.color { ColorAnimation { duration: 120 } }
    }

    contentItem: Text {
        text: control.text
        font: control.font
        color: control.hovered ? theme.textPrimary : theme.textSecondary
        leftPadding: control.indicator.width + control.spacing + 4
        verticalAlignment: Text.AlignVCenter
    }
}
