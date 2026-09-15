import QtQuick
import QtQuick.Controls

TextField {
    id: control

    font.family: theme.fontFamily
    font.pointSize: 10
    color: theme.textPrimary
    placeholderTextColor: theme.textMuted
    selectionColor: theme.accentDim
    selectedTextColor: theme.accent

    implicitWidth: 200
    implicitHeight: 38
    leftPadding: 12
    rightPadding: 12

    background: Rectangle {
        implicitWidth: 200
        implicitHeight: 38
        color: control.readOnly ? theme.bgCard : (control.hovered ? theme.bgHover : theme.bgInput)
        border.color: control.activeFocus ? theme.accent : theme.borderLight
        border.width: 1
        radius: theme.radiusSmall

        Behavior on border.color { ColorAnimation { duration: 150 } }
        Behavior on color { ColorAnimation { duration: 150 } }
    }
}
