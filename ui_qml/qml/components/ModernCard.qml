import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    property string title: ""
    property int contentPadding: 14
    default property alias content: contentLayout.data

    radius: theme.radiusMedium
    color: theme.bgCard
    border.color: theme.border
    border.width: 1

    implicitHeight: mainCol.implicitHeight + (root.contentPadding * 2)

    Behavior on color { ColorAnimation { duration: 150 } }
    Behavior on border.color { ColorAnimation { duration: 150 } }

    ColumnLayout {
        id: mainCol
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: root.contentPadding
        spacing: 10

        // Başlık Bölümü
        Item {
            visible: root.title !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: 16

            Text {
                text: root.title.toUpperCase()
                font.family: theme.fontFamily
                font.pointSize: 9
                font.bold: true
                color: theme.textMuted
                font.letterSpacing: 1.1
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Başlık Ayracı
        Rectangle {
            visible: root.title !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: theme.border
        }

        // İçerik Bölümü
        ColumnLayout {
            id: contentLayout
            Layout.fillWidth: true
            spacing: 10
        }
    }
}
