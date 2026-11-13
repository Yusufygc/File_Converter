import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Uygulama içi güncelleme penceresi (UpdateBridge: "updateBridge" bağlam özelliği).
// Durumlar: checking | uptodate | available | downloading | installing | waiting | blocked | error
Item {
    id: root

    readonly property bool hasBridge: typeof updateBridge !== "undefined" && updateBridge !== null
    readonly property string st: hasBridge ? updateBridge.state : "idle"
    readonly property bool open: hasBridge && updateBridge.dialogOpen

    anchors.fill: parent
    visible: opacity > 0
    opacity: open ? 1.0 : 0.0

    Behavior on opacity { NumberAnimation { duration: 200 } }

    // Arka plan: yalnızca meşgul değilken tıklayınca kapatır; olayları alta geçirmez.
    Rectangle {
        anchors.fill: parent
        color: "#80000000"

        MouseArea {
            anchors.fill: parent
            onClicked: if (root.hasBridge && !updateBridge.busy) updateBridge.closeDialog()
        }
    }

    Rectangle {
        id: card
        width: Math.min(parent.width - 40, 520)
        height: contentCol.implicitHeight + 48
        anchors.centerIn: parent
        radius: theme.radiusLarge
        color: theme.bgSurface
        border.color: root.st === "error" ? theme.warning : theme.border
        border.width: 1
        scale: root.open ? 1.0 : 0.95

        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }

        // Kart içine tıklama arka plana geçmesin
        MouseArea { anchors.fill: parent }

        ColumnLayout {
            id: contentCol
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 24
            spacing: 14

            Text {
                Layout.fillWidth: true
                text: root.st === "available" ? "Yeni sürüm var" : "Güncelleme"
                font.family: theme.fontFamily
                font.pointSize: 13
                font.bold: true
                color: theme.textPrimary
            }

            Text {
                Layout.fillWidth: true
                visible: text.length > 0
                text: !root.hasBridge ? "" : (root.st === "available"
                      ? "FileConvert " + updateBridge.newVersion + " yayınlandı (yüklü sürüm: " + updateBridge.currentVersion + ")."
                      : updateBridge.message)
                font.family: theme.fontFamily
                font.pointSize: 10
                color: root.st === "error" ? theme.warning : theme.textSecondary
                wrapMode: Text.WordWrap
            }

            // Sürüm notları (düz metin)
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 140
                visible: root.hasBridge && root.st === "available" && updateBridge.notes.length > 0
                radius: theme.radiusSmall
                color: theme.bgInput
                border.color: theme.border
                border.width: 1
                clip: true

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 8

                    TextArea {
                        readOnly: true
                        text: root.hasBridge ? updateBridge.notes : ""
                        textFormat: TextEdit.PlainText
                        wrapMode: TextEdit.Wrap
                        font.family: theme.fontFamily
                        font.pointSize: 9
                        color: theme.textSecondary
                        background: null
                    }
                }
            }

            ProgressBar {
                Layout.fillWidth: true
                visible: root.st === "downloading"
                from: 0
                to: 1
                value: root.hasBridge ? updateBridge.progress : 0
            }

            BusyIndicator {
                Layout.alignment: Qt.AlignHCenter
                running: root.st === "checking" || root.st === "installing" || root.st === "waiting"
                visible: running
            }

            // Tek satır, ortalı. (Genişliği verilmemiş bir Flow her düğmeyi ayrı satıra
            // kaydırıyordu; aynı anda en çok 3 düğme görünür, 520 px karta sığar.)
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 4
                spacing: 10

                ModernButton {
                    visible: root.st === "available"
                    text: "Güncelle"
                    variant: "primary"
                    onClicked: updateBridge.startUpdate()
                }
                ModernButton {
                    visible: root.st === "available"
                    text: "Bu Sürümü Atla"
                    variant: "secondary"
                    onClicked: updateBridge.skipVersion()
                }
                ModernButton {
                    visible: root.st === "waiting"
                    text: "Beklemeyi Bırak"
                    variant: "secondary"
                    onClicked: updateBridge.stopWaiting()
                }
                ModernButton {
                    visible: root.st === "blocked" || root.st === "error"
                    text: "Sürüm Sayfası"
                    variant: "secondary"
                    onClicked: updateBridge.openReleasePage()
                }
                ModernButton {
                    visible: root.st !== "downloading" && root.st !== "installing" && root.st !== "checking"
                    text: root.st === "available" ? "Sonra" : "Kapat"
                    variant: "ghost"
                    onClicked: updateBridge.closeDialog()
                }
            }
        }
    }
}
