import QtQuick

QtObject {
    id: theme

    // Bridge'den veya varsayılandan aktif mod
    property string mode: (typeof bridge !== "undefined" && bridge) ? bridge.themeMode : "dark"
    readonly property bool isDark: mode === "dark"

    // ── Resmî 5 Renkli Koyu Palet Sabitleri (Gunmetal & Silver) ────────
    // 1. GUNMETAL:        #292C36  RGB(41, 44, 54)     CMYK(24%, 19%, 0%, 79%)
    // 2. ROMAN SILVER:    #848A98  RGB(132, 138, 152)  CMYK(13%, 9%, 0%, 40%)
    // 3. COOL GREY:       #8E99AC  RGB(142, 153, 172)  CMYK(18%, 11%, 0%, 33%)
    // 4. SILVER SAND:     #BDC2C7  RGB(189, 194, 199)  CMYK(5%, 3%, 0%, 22%)
    // 5. METALLIC SILVER: #A1A7AF  RGB(161, 167, 175)  CMYK(8%, 5%, 0%, 31%)
    readonly property color gunmetal: "#292C36"
    readonly property color romanSilver: "#848A98"
    readonly property color coolGrey: "#8E99AC"
    readonly property color silverSand: "#BDC2C7"
    readonly property color metallicSilver: "#A1A7AF"

    // ── Resmî 5 Renkli Açık Palet Sabitleri (Jet Stream & Slate) ────────
    // 1. JET STREAM:          #C1D1CF  RGB(193, 209, 207)  CMYK(8%, 0%, 1%, 18%)
    // 2. DARK JUNGLE GREEN:   #171F22  RGB(23, 31, 34)     CMYK(32%, 9%, 0%, 87%)
    // 3. GRANITE GRAY (Slate):#636467  RGB(99, 100, 103)   CMYK(4%, 3%, 0%, 60%)
    // 4. LIGHT SLATE GRAY:    #748B91  RGB(116, 139, 145)  CMYK(20%, 4%, 0%, 43%)
    // 5. GRANITE GRAY (Sage): #666B64  RGB(102, 107, 100)  CMYK(5%, 0%, 7%, 58%)
    readonly property color jetStream: "#C1D1CF"
    readonly property color darkJungleGreen: "#171F22"
    readonly property color graniteGray: "#636467"
    readonly property color lightSlateGray: "#748B91"
    readonly property color sageGranite: "#666B64"

    // Geriye dönük uyumluluk takma adları
    readonly property color _gunmetal: gunmetal
    readonly property color _jetStream: jetStream

    // ── Arka Plan & Yüzey Renkleri ─────────────────────────────────────
    // Koyu tema: Gunmetal tabanından kademeli türetilen derin yüzey hiyerarşisi
    // Açık tema: Jet Stream tabanı üzerinde temiz beyaz kartlar & açık yüzeyler
    readonly property color bgPrimary: isDark ? gunmetal : jetStream
    readonly property color bgSurface: isDark ? Qt.lighter(gunmetal, 1.10) : "#FFFFFF"
    readonly property color bgCard: isDark ? Qt.lighter(gunmetal, 1.25) : "#FFFFFF"
    readonly property color bgElevated: isDark ? Qt.lighter(gunmetal, 1.45) : Qt.lighter(jetStream, 1.05)
    readonly property color bgInput: isDark ? Qt.lighter(gunmetal, 1.18) : "#FFFFFF"
    readonly property color bgHover: isDark ? Qt.lighter(gunmetal, 1.65) : Qt.darker(jetStream, 1.06)

    // ── Vurgu & Durum Renkleri ─────────────────────────────────────────
    // Koyu tema: Silver Sand ana vurgusu, Cool Grey parlama ve seçim katmanı
    // Açık tema: Dark Jungle Green ana vurgusu, Light Slate Gray seçim katmanı
    readonly property color accent: isDark ? silverSand : darkJungleGreen
    readonly property color accentHover: isDark ? Qt.lighter(silverSand, 1.08) : Qt.lighter(darkJungleGreen, 1.35)
    readonly property color accentDim: isDark ? Qt.rgba(142/255, 153/255, 172/255, 0.20) : Qt.rgba(116/255, 139/255, 145/255, 0.20)
    readonly property color accentGlow: isDark ? Qt.rgba(142/255, 153/255, 172/255, 0.15) : Qt.rgba(116/255, 139/255, 145/255, 0.15)

    readonly property color success: isDark ? "#34D27A" : "#1E9E5A"
    readonly property color successDim: isDark ? "#2634D27A" : "#1F1E9E5A"
    readonly property color warning: isDark ? "#F5A623" : "#B9720A"
    readonly property color error: isDark ? "#F05252" : "#D33F3F"
    readonly property color errorDim: isDark ? "#26F05252" : "#1FD33F3F"

    // ── Tipografi Renkleri ─────────────────────────────────────────────
    // Koyu: Silver Sand (birincil) / Metallic Silver (ikincil) / Roman Silver (soluk)
    // Açık: Dark Jungle Green (birincil) / Granite Gray (ikincil) / Light Slate Gray (soluk)
    readonly property color textPrimary: isDark ? silverSand : darkJungleGreen
    readonly property color textSecondary: isDark ? metallicSilver : graniteGray
    readonly property color textMuted: isDark ? romanSilver : lightSlateGray

    // ── Çerçeve & Ayraç Renkleri ──────────────────────────────────────
    // Koyu: Roman Silver tonlu zarif çerçeveler / Cool Grey belirgin sınır çizgileri
    // Açık: Sage Granite tonlu zarif çerçeveler / Sage Granite belirgin sınır çizgileri
    readonly property color border: isDark ? Qt.rgba(132/255, 138/255, 152/255, 0.28) : Qt.rgba(102/255, 107/255, 100/255, 0.28)
    readonly property color borderLight: isDark ? coolGrey : sageGranite

    // ── Geometri / Boyutlandırma ──────────────────────────────────────
    readonly property int radiusSmall: 6
    readonly property int radiusMedium: 10
    readonly property int radiusLarge: 14

    readonly property string fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif"
}
