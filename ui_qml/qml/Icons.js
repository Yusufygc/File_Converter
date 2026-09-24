.pragma library

// Merkezi ikon mekanizması — emoji yerine Segoe Fluent Icons (Windows
// sistem fontu, ek asset/bağımlılık gerektirmez) glyph'leri kullanılır.
// Codepoint'ler: https://learn.microsoft.com/windows/apps/design/style/segoe-fluent-icons-font

var FONT_FAMILY = "Segoe Fluent Icons"

var GLYPHS = {
    cancel: "",
    check: "",
    refresh: "",
    settings: "",
    back: "",
    search: "",
    folder_open: "",
    convert: "",
    theme_light: "",
    theme_dark: "",
    split: "",
    merge: "",
    compress: "",
    note: "",
    image: "",
    table: "",
    document: "",
}

function glyph(key) {
    return GLYPHS[key] || ""
}
