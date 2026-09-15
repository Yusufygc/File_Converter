import QtQuick
import QtQuick.Layouts

RowLayout {
    id: root

    spacing: 8

    Text {
        id: countLabel
        text: {
            if (typeof bridge === "undefined" || !bridge || bridge.fileCount === 0) return "Dosya eklenmedi"
            if (bridge.fileCount === 1) return "1 dosya eklendi"
            return bridge.fileCount + " dosya eklendi"
        }
        font.family: theme.fontFamily
        font.pointSize: 10
        color: theme.textMuted
        Layout.alignment: Qt.AlignVCenter
    }

    Item {
        Layout.fillWidth: true
    }

    ModernButton {
        text: " Dosya Ekle"
        variant: "accent_outline"
        pointSize: 10
        implicitHeight: 34
        enabled: typeof bridge !== "undefined" && bridge && !bridge.isConverting
        onClicked: {
            if (typeof bridge !== "undefined" && bridge) {
                bridge.openFileDialog()
            }
        }
    }

    ModernButton {
        text: " Temizle"
        variant: "danger"
        pointSize: 10
        implicitHeight: 34
        enabled: typeof bridge !== "undefined" && bridge && bridge.hasFiles && !bridge.isConverting
        onClicked: {
            if (typeof bridge !== "undefined" && bridge) {
                bridge.clearFiles()
            }
        }
    }
}
