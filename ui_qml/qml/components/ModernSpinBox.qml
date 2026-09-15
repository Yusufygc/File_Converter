import QtQuick
import QtQuick.Controls

SpinBox {
    id: control

    property string suffix: ""

    font.family: theme.fontFamily
    font.pointSize: 10

    implicitWidth: 120
    implicitHeight: 38

    validator: IntValidator {
        locale: control.locale.name
        bottom: Math.min(control.from, control.to)
        top: Math.max(control.from, control.to)
    }

    textFromValue: function(value, locale) {
        return Number(value).toLocaleString(locale, 'f', 0) + (control.suffix ? " " + control.suffix : "")
    }

    valueFromText: function(text, locale) {
        var clean = text.replace(control.suffix, "").trim()
        return Number.fromLocaleString(locale, clean)
    }

    contentItem: TextInput {
        z: 2
        text: control.textFromValue(control.value, control.locale)
        font: control.font
        color: theme.textPrimary
        selectionColor: theme.accentDim
        selectedTextColor: theme.accent
        horizontalAlignment: Qt.AlignLeft
        verticalAlignment: Qt.AlignVCenter
        leftPadding: 10
        readOnly: !control.editable
        validator: control.validator
        inputMethodHints: control.inputMethodHints
    }

    up.indicator: Item {
        x: control.mirrored ? 0 : control.width - width
        height: control.height / 2
        width: 24

        Rectangle {
            anchors.fill: parent
            color: control.up.pressed ? theme.bgHover : "transparent"
            radius: 4

            Text {
                text: "▲"
                font.pixelSize: 8
                color: control.up.hovered ? theme.accent : theme.textMuted
                anchors.centerIn: parent
            }
        }
    }

    down.indicator: Item {
        x: control.mirrored ? 0 : control.width - width
        y: control.height / 2
        height: control.height / 2
        width: 24

        Rectangle {
            anchors.fill: parent
            color: control.down.pressed ? theme.bgHover : "transparent"
            radius: 4

            Text {
                text: "▼"
                font.pixelSize: 8
                color: control.down.hovered ? theme.accent : theme.textMuted
                anchors.centerIn: parent
            }
        }
    }

    background: Rectangle {
        implicitWidth: 120
        implicitHeight: 38
        color: control.hovered ? theme.bgHover : theme.bgInput
        border.color: control.activeFocus ? theme.accent : theme.borderLight
        border.width: 1
        radius: theme.radiusSmall

        Behavior on border.color { ColorAnimation { duration: 150 } }
        Behavior on color { ColorAnimation { duration: 150 } }
    }
}
