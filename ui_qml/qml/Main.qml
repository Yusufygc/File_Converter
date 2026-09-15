import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "components"

ApplicationWindow {
    id: window

    visible: true
    title: "FileConvert Pro"
    minimumWidth: 960
    minimumHeight: 680
    width: 1100
    height: 760

    color: theme.bgPrimary

    property int currentViewIndex: 0 // 0: Main Converter, 1: Settings

    // Tema Nesnesi
    Theme {
        id: theme
    }

    // Pencere Boyutu / Konumu Değişince Kaydet
    onClosing: {
        if (typeof bridge !== "undefined" && bridge) {
            bridge.saveWindowGeometry(window.x, window.y, window.width, window.height)
        }
    }

    // Bildirim Diyaloğu
    Connections {
        target: (typeof bridge !== "undefined" && bridge) ? bridge : null
        function onNotificationRequested(title, message) {
            notifDialog.title = title
            notifText.text = message
            notifDialog.open()
        }
    }

    Dialog {
        id: notifDialog
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok

        contentItem: Text {
            id: notifText
            font.family: theme.fontFamily
            font.pointSize: 10
            color: theme.textPrimary
            wrapMode: Text.Wrap
        }

        background: Rectangle {
            color: theme.bgSurface
            border.color: theme.borderLight
            border.width: 1
            radius: theme.radiusMedium
        }
    }

    // Ana Düzen
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Üst Başlık Çubuğu ─────────────────────────────────────────
        HeaderBar {
            Layout.fillWidth: true
            isSettingsPage: window.currentViewIndex === 1
            onSettingsToggleClicked: {
                window.currentViewIndex = (window.currentViewIndex === 0 ? 1 : 0)
            }
        }

        // ── Stack Page Görünüm Alanı ──────────────────────────────────
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // SAYFA 0: Ana Dönüştürücü Sayfası
            Item {
                anchors.fill: parent
                visible: opacity > 0
                opacity: window.currentViewIndex === 0 ? 1.0 : 0.0

                Behavior on opacity { NumberAnimation { duration: 180 } }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    // SOL PANEL: Kategori & Format Menüsü (Sidebar)
                    CategorySidebar {
                        Layout.preferredWidth: 280
                        Layout.fillHeight: true
                        Layout.minimumWidth: 240
                        Layout.maximumWidth: 320
                    }

                    // SAĞ PANEL: Geniş Çalışma Tuvali (Main Canvas)
                    MainCanvas {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                }
            }

            // SAYFA 1: Ayarlar ve Tercihler Sayfası
            SettingsView {
                anchors.fill: parent
                anchors.margins: 20
                visible: opacity > 0
                opacity: window.currentViewIndex === 1 ? 1.0 : 0.0
                onBackRequested: {
                    window.currentViewIndex = 0
                }

                Behavior on opacity { NumberAnimation { duration: 180 } }
            }
        }

        // ── Alt Durum Çubuğu ─────────────────────────────────────────
        FooterBar {
            Layout.fillWidth: true
        }
    }

    // ── Dönüşüm Özeti Modalı ─────────────────────────────────────────
    SummaryModal {
        z: 99
    }
}
