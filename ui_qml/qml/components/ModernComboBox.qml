import QtQuick
import QtQuick.Controls
import "../Icons.js" as Icons

ComboBox {
    id: control

    property string textRoleKey: "displayName"
    property string valueRoleKey: "id"

    function iconFor(item) {
        return (item && item.icon !== undefined) ? item.icon : ""
    }

    font.family: theme.fontFamily
    font.pointSize: 10
    font.weight: Font.Normal

    implicitWidth: 220
    implicitHeight: 38

    textRole: textRoleKey

    displayText: {
        if (currentIndex < 0) return ""
        if (!model) return ""
        var item = null
        if (Array.isArray(model)) {
            item = model[currentIndex]
        } else if (typeof model.get === "function") {
            item = model.get(currentIndex)
        }
        if (typeof item === "string") return item
        if (item && item[control.textRoleKey] !== undefined) return item[control.textRoleKey]
        if (item && item.displayName !== undefined) return item.displayName
        if (item && item.name !== undefined) return item.name
        return control.currentText || ""
    }

    property string currentIcon: {
        if (currentIndex < 0 || !model) return ""
        var item = null
        if (Array.isArray(model)) {
            item = model[currentIndex]
        } else if (typeof model.get === "function") {
            item = model.get(currentIndex)
        }
        return control.iconFor(item)
    }

    delegate: ItemDelegate {
        id: itemDel
        width: control.popup.width
        implicitHeight: 36
        padding: 8

        contentItem: Item {
            Text {
                id: itemIconText
                visible: text !== ""
                text: Icons.glyph(control.iconFor(modelData))
                font.family: Icons.FONT_FAMILY
                font.pointSize: 10
                color: itemDel.hovered ? theme.accent : theme.textPrimary
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: {
                    if (typeof modelData === "string") return modelData
                    if (modelData && modelData[control.textRoleKey] !== undefined) return modelData[control.textRoleKey]
                    if (modelData && modelData.displayName !== undefined) return modelData.displayName
                    if (modelData && modelData.name !== undefined) return modelData.name
                    return ""
                }
                color: itemDel.hovered ? theme.accent : theme.textPrimary
                font.family: theme.fontFamily
                font.pointSize: 10
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
                anchors.left: itemIconText.visible ? itemIconText.right : parent.left
                anchors.leftMargin: itemIconText.visible ? 8 : 0
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        background: Rectangle {
            color: itemDel.hovered ? theme.bgHover : (control.currentIndex === index ? theme.accentDim : "transparent")
            radius: theme.radiusSmall
        }
    }

    indicator: Canvas {
        id: canvas
        x: control.width - width - 12
        y: (control.height - height) / 2
        width: 10
        height: 6
        contextType: "2d"

        Connections {
            target: control
            function onPressedChanged() { canvas.requestPaint() }
        }

        onPaint: {
            context.reset()
            context.moveTo(0, 0)
            context.lineTo(width, 0)
            context.lineTo(width / 2, height)
            context.closePath()
            context.fillStyle = theme.textMuted
            context.fill()
        }
    }

    contentItem: Item {
        Text {
            id: currentIconText
            visible: text !== ""
            text: Icons.glyph(control.currentIcon)
            font.family: Icons.FONT_FAMILY
            font.pointSize: control.font.pointSize
            color: theme.textPrimary
            anchors.left: parent.left
            anchors.leftMargin: 12
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: control.displayText
            font: control.font
            color: theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            anchors.left: currentIconText.visible ? currentIconText.right : parent.left
            anchors.leftMargin: currentIconText.visible ? 8 : 12
            anchors.right: parent.right
            anchors.rightMargin: control.indicator.width + 18
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    background: Rectangle {
        implicitWidth: 120
        implicitHeight: 38
        color: control.hovered ? theme.bgHover : theme.bgInput
        border.color: control.activeFocus || control.popup.visible ? theme.accent : theme.borderLight
        border.width: 1
        radius: theme.radiusSmall

        Behavior on border.color { ColorAnimation { duration: 150 } }
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    popup: Popup {
        y: control.height + 4
        width: control.width
        implicitHeight: Math.min(contentItem.implicitHeight + 10, 260)
        padding: 4

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator { }
        }

        background: Rectangle {
            color: theme.bgSurface
            border.color: theme.borderLight
            border.width: 1
            radius: theme.radiusSmall
        }
    }
}
