from PySide6.QtCore import QSettings

from core.utils.resource_helper import get_resource_path
from ui.app_settings import ORG_NAME, APP_NAME, THEME_MODE_KEY

# CSS dostu yollar için ters bölüleri düze çevir
def _css_path(rel_path: str) -> str:
    abs_path = get_resource_path(rel_path)
    return abs_path.replace("\\", "/")

CHEVRON_DOWN = _css_path("assets/icons/chevron_down.svg")
CHEVRON_UP = _css_path("assets/icons/chevron_up.svg")

DARK_PALETTE = {
    "bg_primary":    "#0D0F18",
    "bg_surface":    "#13161F",
    "bg_card":       "#1C2030",
    "bg_elevated":   "#242840",
    "bg_input":      "#1A1D2E",
    "bg_hover":      "#2C3152",
    "accent":        "#4B8CF5",
    "accent_hover":  "#6BA3FF",
    "accent_dim":    "#1E3A7A",
    "accent_glow":   "rgba(75,140,245,0.15)",
    "success":       "#34D27A",
    "success_dim":   "rgba(52,210,122,0.15)",
    "warning":       "#F5A623",
    "error":         "#F05252",
    "error_dim":     "rgba(240,82,82,0.12)",
    "text_primary":  "#FFFFFF",
    "text_secondary":"#B0B8D1",
    "text_muted":    "#6E7794",
    "border":        "#252A42",
    "border_light":  "#303759",
}

LIGHT_PALETTE = {
    "bg_primary":    "#F5F6FA",
    "bg_surface":    "#FFFFFF",
    "bg_card":       "#FFFFFF",
    "bg_elevated":   "#EEF0F6",
    "bg_input":      "#FFFFFF",
    "bg_hover":      "#E7EAF3",
    "accent":        "#3B6FD6",
    "accent_hover":  "#2C5BC0",
    "accent_dim":    "#DCE6FB",
    "accent_glow":   "rgba(59,111,214,0.12)",
    "success":       "#1E9E5A",
    "success_dim":   "rgba(30,158,90,0.12)",
    "warning":       "#B9720A",
    "error":         "#D33F3F",
    "error_dim":     "rgba(211,63,63,0.10)",
    "text_primary":  "#1A1D2A",
    "text_secondary":"#4A5068",
    "text_muted":    "#7C8298",
    "border":        "#DDE1EC",
    "border_light":  "#C7CCDC",
}


def build_style(palette: dict) -> str:
    """Verilen palete göre tam QSS string'ini üretir."""
    return f"""
/* ── Global Reset ───────────────────────────────────── */
* {{
    outline: none;
}}
QWidget {{
    background-color: {palette['bg_primary']};
    color: {palette['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', sans-serif;
    font-size: 13px;
    selection-background-color: {palette['accent_dim']};
    selection-color: {palette['accent']};
}}
QMainWindow {{
    background-color: {palette['bg_primary']};
}}

/* ── Header ─────────────────────────────────────────── */
#titleBar {{
    background-color: {palette['bg_surface']};
    border-bottom: 1px solid {palette['border']};
}}
#appTitle {{
    font-size: 16px;
    font-weight: 700;
    color: {palette['text_primary']};
    letter-spacing: -0.3px;
    margin-right: 12px;
}}
#formatBadge {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {palette['accent']};
    background-color: {palette['accent_dim']};
    border-radius: 4px;
    padding: 3px 8px;
}}

/* ── Drop Zone ──────────────────────────────────────── */
#dropZone {{
    background-color: {palette['bg_surface']};
    border: 1.5px dashed {palette['border_light']};
    border-radius: 10px;
}}
#dropZone:hover {{
    border-color: {palette['accent']};
    background-color: {palette['accent_glow']};
}}
#dropZoneActive {{
    border: 1.5px dashed {palette['accent']};
    background-color: {palette['accent_glow']};
}}
#dropZonePrimaryLabel {{
    font-size: 13px;
    font-weight: 600;
    color: {palette['text_primary']};
    background: transparent;
    border: none;
}}
#dropZoneExtLabel {{
    font-size: 11px;
    color: {palette['text_muted']};
    background: transparent;
    border: none;
    letter-spacing: 0.5px;
}}

/* ── File List ──────────────────────────────────────── */
QListWidget {{
    background-color: {palette['bg_surface']};
    border: 1px solid {palette['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 0px; /* Custom widget kullanıldığı için padding 0 olmalı, aksi halde offset oluşur */
    border-radius: 5px;
    color: {palette['text_primary']};
    border: none;
}}
QListWidget::item:selected {{
    background-color: {palette['accent_dim']};
    color: {palette['accent_hover']};
}}
QListWidget::item:hover:!selected {{
    background-color: {palette['bg_hover']};
}}
#fileNameLabel {{
    color: {palette['text_primary']};
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}}
#fileSizeLabel {{
    color: {palette['text_muted']};
    font-size: 11px;
    background: transparent;
}}

/* ── Buttons (secondary) ────────────────────────────── */
QPushButton {{
    background-color: {palette['bg_elevated']};
    color: {palette['text_primary']};
    border: 1px solid {palette['border_light']};
    border-radius: 7px;
    padding: 7px 16px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {palette['bg_hover']};
    border-color: {palette['text_muted']};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {palette['bg_card']};
    border-color: {palette['border']};
}}
QPushButton:disabled {{
    color: {palette['text_muted']};
    border-color: {palette['border']};
    background-color: {palette['bg_card']};
}}

/* ── Primary CTA ─────────────────────────────────────── */
QPushButton#primaryBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {palette['accent']}, stop:1 {palette['accent_hover']});
    color: #ffffff;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    font-size: 14px;
    padding: 0px;
    letter-spacing: 0.3px;
}}
QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {palette['accent_hover']}, stop:1 #7BB8FF);
}}
QPushButton#primaryBtn:pressed {{
    background: {palette['accent']};
}}
QPushButton#primaryBtn:disabled {{
    background: {palette['bg_elevated']};
    color: {palette['text_muted']};
    border: 1px solid {palette['border']};
}}

/* ── Add File Button ─────────────────────────────────── */
QPushButton#addBtn {{
    background-color: {palette['accent_dim']};
    color: {palette['accent_hover']};
    border: 1px solid {palette['accent_dim']};
    border-radius: 7px;
    font-weight: 600;
}}
QPushButton#addBtn:hover {{
    background-color: {palette['accent']};
    color: #ffffff;
    border-color: {palette['accent']};
}}

/* ── Danger Button ──────────────────────────────────── */
QPushButton#dangerBtn {{
    background-color: transparent;
    color: {palette['error']};
    border: 1px solid rgba(240,82,82,0.35);
    border-radius: 7px;
}}
QPushButton#dangerBtn:hover {{
    background-color: {palette['error_dim']};
    border-color: {palette['error']};
}}
QPushButton#dangerBtn:disabled {{
    color: {palette['text_muted']};
    border-color: {palette['border']};
    background-color: transparent;
}}

/* ── Progress Bar ───────────────────────────────────── */
QProgressBar {{
    background-color: {palette['bg_elevated']};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {palette['accent']}, stop:1 {palette['accent_hover']});
    border-radius: 4px;
}}

/* ── ComboBox ───────────────────────────────────────── */
QComboBox {{
    background-color: {palette['bg_input']};
    border: 1px solid {palette['border_light']};
    border-radius: 7px;
    padding: 6px 32px 6px 10px;
    color: {palette['text_primary']};
    font-size: 13px;
    min-width: 180px;
}}
QComboBox:hover, QComboBox:focus {{
    border-color: {palette['accent']};
    background-color: {palette['bg_elevated']};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 26px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: url({CHEVRON_DOWN});
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background-color: {palette['bg_surface']}; /* Daha koyu ve opak arka plan */
    border: 1px solid {palette['border_light']};
    border-radius: 7px;
    padding: 4px;
    selection-background-color: {palette['accent_dim']};
    selection-color: {palette['accent_hover']};
    color: {palette['text_primary']};
    outline: none;
    font-size: 13px; /* Font uyarısını önlemek için kesin boyut */
}}
QComboBox QAbstractItemView::item {{
    padding: 7px 10px;
    border-radius: 5px;
    min-height: 26px;
}}

/* ── SpinBox ────────────────────────────────────────── */
QSpinBox {{
    background-color: {palette['bg_input']};
    border: 1px solid {palette['border_light']};
    border-radius: 7px;
    padding: 6px 10px;
    color: {palette['text_primary']};
    font-size: 13px;
}}
QSpinBox:hover, QSpinBox:focus {{
    border-color: {palette['accent']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: 16px;
}}
QSpinBox::up-arrow {{
    image: url({CHEVRON_UP});
    width: 10px;
    height: 10px;
}}
QSpinBox::down-arrow {{
    image: url({CHEVRON_DOWN});
    width: 10px;
    height: 10px;
}}

/* ── LineEdit ───────────────────────────────────────── */
QLineEdit {{
    background-color: {palette['bg_input']};
    border: 1px solid {palette['border_light']};
    border-radius: 7px;
    padding: 7px 10px;
    color: {palette['text_primary']};
    font-size: 13px;
}}
QLineEdit:hover {{
    border-color: {palette['border_light']};
}}
QLineEdit:focus {{
    border-color: {palette['accent']};
}}
QLineEdit:read-only {{
    color: {palette['text_secondary']};
    background-color: {palette['bg_card']};
}}
QLineEdit::placeholder {{
    color: {palette['text_muted']};
}}

/* ── CheckBox ───────────────────────────────────────── */
QCheckBox {{
    spacing: 9px;
    color: {palette['text_secondary']};
    font-size: 13px;
}}
QCheckBox:hover {{
    color: {palette['text_primary']};
}}
QCheckBox::indicator {{
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1.5px solid {palette['border_light']};
    background-color: {palette['bg_input']};
}}
QCheckBox::indicator:hover {{
    border-color: {palette['accent']};
}}
QCheckBox::indicator:checked {{
    background-color: {palette['accent']};
    border-color: {palette['accent']};
}}

/* ── GroupBox ───────────────────────────────────────── */
QGroupBox {{
    background-color: {palette['bg_card']};
    border: 1px solid {palette['border']};
    border-radius: 10px;
    margin-top: 18px;
    padding: 14px 14px 12px 14px;
    font-size: 10px;
    font-weight: 700;
    color: {palette['text_muted']};
    letter-spacing: 1.2px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -1px;
    padding: 0 6px;
    background-color: {palette['bg_card']};
    color: {palette['text_muted']};
    border-radius: 3px;
}}

/* ── ScrollBar ──────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {palette['border_light']};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {palette['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}

/* ── Section Cards (options panel) ─────────────────── */
QWidget#sectionCard {{
    background: {palette['bg_card']};
    border: 1px solid {palette['border']};
    border-radius: 8px;
}}
QWidget#sectionCard QLabel {{
    background: transparent;
}}
QWidget#sectionCard QWidget {{
    background: transparent;
}}
#sectionHeaderLabel {{
    color: {palette['text_muted']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    background: transparent;
    padding: 0;
    margin: 0;
}}
QFrame#sectionDivider {{
    color: {palette['border']};
    background: transparent;
}}
#formLabel {{
    color: {palette['text_secondary']};
    font-size: 12px;
    background: transparent;
}}

/* ── Tooltip ────────────────────────────────────────── */
QToolTip {{
    background-color: {palette['bg_elevated']};
    color: {palette['text_primary']};
    border: 1px solid {palette['border_light']};
    border-radius: 6px;
    padding: 7px 11px;
    font-size: 12px;
}}

/* ── Footer ─────────────────────────────────────────── */
#footerBar {{
    background: {palette['bg_surface']};
    border-top: 1px solid {palette['border']};
}}

/* ── Status Bar Labels ──────────────────────────────── */
#statusLabel {{
    color: {palette['text_secondary']};
    font-size: 12px;
}}
#sectionLabel {{
    color: {palette['text_secondary']};
    font-size: 12px;
    font-weight: 600;
}}
#fileCount {{
    color: {palette['text_muted']};
    font-size: 12px;
}}
"""


def _load_theme_mode() -> str:
    """
    Tema tercihini `QSettings`'ten okur. Açıkça org/app adı verilen
    `QSettings` her zaman kullanılabilir — `QApplication` kurulmuş
    olmasına gerek yoktur, bu yüzden bu modül import edilir edilmez
    (ui.main_window'dan çok önce) güvenle çağrılabilir.
    """
    settings = QSettings(ORG_NAME, APP_NAME)
    mode = settings.value(THEME_MODE_KEY, "dark")
    return str(mode).lower() if mode else "dark"


# Modül import edilir edilmez doğru palet seçilir — bu sayede import
# zincirindeki her dosyadaki `from ui.styles.theme import PALETTE`
# (options_panel.py, file_list.py, drop_zone.py, summary_dialog.py,
# main_window.py) Python'un tek-seferlik modül önbelleği sayesinde
# aynı, doğru paleti alır.
_MODE = _load_theme_mode()
# dict(...) ile KOPYALANIR — `apply_theme()` PALETTE'i yerinde
# temizleyip (clear()) yeniden dolduruyor (update()); PALETTE doğrudan
# DARK_PALETTE/LIGHT_PALETTE nesnesinin kendisi olsaydı bu işlem o
# sabit paleti de boşaltıp bozardı.
PALETTE = dict(LIGHT_PALETTE if _MODE == "light" else DARK_PALETTE)
MAIN_STYLE = build_style(PALETTE)


def apply_theme(mode: str) -> str:
    """
    Paleti yerinde (in-place) günceller — `PALETTE` nesne kimliği
    korunur, bu sayede `from ui.styles.theme import PALETTE` yapan her
    modüldeki referans aynı dict'i gösterdiği için içeriği anında
    güncel olur (canlı tema geçişi buna dayanır, bkz.
    docs/wiki/ui-katmani.md). Yeni QSS'i döner; çağıran
    (`MainWindow`) bunu `QApplication.setStyleSheet()` ile uygular ve
    dinamik (duruma göre renklenen) widget'ların `retheme()`'ini
    tetikler.
    """
    global MAIN_STYLE
    new_palette = LIGHT_PALETTE if mode == "light" else DARK_PALETTE
    PALETTE.clear()
    PALETTE.update(new_palette)
    MAIN_STYLE = build_style(PALETTE)
    return MAIN_STYLE
