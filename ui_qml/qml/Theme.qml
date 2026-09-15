import QtQuick

QtObject {
    id: theme

    // Bridge'den veya varsayılandan aktif mod
    property string mode: (typeof bridge !== "undefined" && bridge) ? bridge.themeMode : "dark"
    readonly property bool isDark: mode === "dark"

    // ── Arka Plan Renkleri ─────────────────────────────────────────────
    readonly property color bgPrimary: isDark ? "#0D0F18" : "#F5F6FA"
    readonly property color bgSurface: isDark ? "#13161F" : "#FFFFFF"
    readonly property color bgCard: isDark ? "#1C2030" : "#FFFFFF"
    readonly property color bgElevated: isDark ? "#242840" : "#EEF0F6"
    readonly property color bgInput: isDark ? "#1A1D2E" : "#FFFFFF"
    readonly property color bgHover: isDark ? "#2C3152" : "#E7EAF3"

    // ── Vurgu & Durum Renkleri ─────────────────────────────────────────
    readonly property color accent: isDark ? "#4B8CF5" : "#3B6FD6"
    readonly property color accentHover: isDark ? "#6BA3FF" : "#2C5BC0"
    readonly property color accentDim: isDark ? "#1E3A7A" : "#DCE6FB"
    readonly property color accentGlow: isDark ? "#264B8CF5" : "#1F3B6FD6"

    readonly property color success: isDark ? "#34D27A" : "#1E9E5A"
    readonly property color successDim: isDark ? "#2634D27A" : "#1F1E9E5A"
    readonly property color warning: isDark ? "#F5A623" : "#B9720A"
    readonly property color error: isDark ? "#F05252" : "#D33F3F"
    readonly property color errorDim: isDark ? "#26F05252" : "#1FD33F3F"

    // ── Tipografi Renkleri ─────────────────────────────────────────────
    readonly property color textPrimary: isDark ? "#FFFFFF" : "#1A1D2A"
    readonly property color textSecondary: isDark ? "#B0B8D1" : "#4A5068"
    readonly property color textMuted: isDark ? "#6E7794" : "#7C8298"

    // ── Çerçeve & Ayraç Renkleri ──────────────────────────────────────
    readonly property color border: isDark ? "#252A42" : "#DDE1EC"
    readonly property color borderLight: isDark ? "#303759" : "#C7CCDC"

    // ── Geometri / Boyutlandırma ──────────────────────────────────────
    readonly property int radiusSmall: 6
    readonly property int radiusMedium: 10
    readonly property int radiusLarge: 14

    readonly property string fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif"
}
