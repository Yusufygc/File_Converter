import QtQuick

Rectangle {
    id: root

    height: 36
    color: theme.bgSurface
    border.color: theme.border
    border.width: 1

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        Text {
            text: (typeof bridge !== "undefined" && bridge) ? bridge.statusMessage : "Hazır"
            font.family: theme.fontFamily
            font.pointSize: 9
            color: {
                var kind = (typeof bridge !== "undefined" && bridge) ? bridge.statusKind : "neutral"
                if (kind === "success") return theme.success
                if (kind === "warning") return theme.warning
                return theme.textSecondary
            }
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
