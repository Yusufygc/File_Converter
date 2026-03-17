"""
Application Theme — Dark Professional
=======================================
Merkezi renk/stil sabitleri. Tek yerden yönetim.
"""

PALETTE = {
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

MAIN_STYLE = f"""
/* ── Global Reset ───────────────────────────────────── */
* {{
    outline: none;
}}
QWidget {{
    background-color: {PALETTE['bg_primary']};
    color: {PALETTE['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', sans-serif;
    font-size: 13px;
    selection-background-color: {PALETTE['accent_dim']};
    selection-color: {PALETTE['accent']};
}}
QMainWindow {{
    background-color: {PALETTE['bg_primary']};
}}

/* ── Header ─────────────────────────────────────────── */
#titleBar {{
    background-color: {PALETTE['bg_surface']};
    border-bottom: 1px solid {PALETTE['border']};
}}
#appTitle {{
    font-size: 16px;
    font-weight: 700;
    color: {PALETTE['text_primary']};
    letter-spacing: -0.3px;
}}
#formatBadge {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {PALETTE['accent']};
    background-color: {PALETTE['accent_dim']};
    border-radius: 4px;
    padding: 3px 8px;
}}

/* ── Drop Zone ──────────────────────────────────────── */
#dropZone {{
    background-color: {PALETTE['bg_surface']};
    border: 1.5px dashed {PALETTE['border_light']};
    border-radius: 10px;
}}
#dropZone:hover {{
    border-color: {PALETTE['accent']};
    background-color: {PALETTE['accent_glow']};
}}
#dropZoneActive {{
    border: 1.5px dashed {PALETTE['accent']};
    background-color: {PALETTE['accent_glow']};
}}

/* ── File List ──────────────────────────────────────── */
QListWidget {{
    background-color: {PALETTE['bg_surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 6px 8px;
    border-radius: 5px;
    color: {PALETTE['text_primary']};
    border: none;
}}
QListWidget::item:selected {{
    background-color: {PALETTE['accent_dim']};
    color: {PALETTE['accent_hover']};
}}
QListWidget::item:hover:!selected {{
    background-color: {PALETTE['bg_hover']};
}}

/* ── Buttons (secondary) ────────────────────────────── */
QPushButton {{
    background-color: {PALETTE['bg_elevated']};
    color: {PALETTE['text_primary']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 7px;
    padding: 7px 16px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {PALETTE['bg_hover']};
    border-color: {PALETTE['text_muted']};
    color: #ffffff;
}}
QPushButton:pressed {{
    background-color: {PALETTE['bg_card']};
    border-color: {PALETTE['border']};
}}
QPushButton:disabled {{
    color: {PALETTE['text_muted']};
    border-color: {PALETTE['border']};
    background-color: {PALETTE['bg_card']};
}}

/* ── Primary CTA ─────────────────────────────────────── */
QPushButton#primaryBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {PALETTE['accent']}, stop:1 {PALETTE['accent_hover']});
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
        stop:0 {PALETTE['accent_hover']}, stop:1 #7BB8FF);
}}
QPushButton#primaryBtn:pressed {{
    background: {PALETTE['accent']};
}}
QPushButton#primaryBtn:disabled {{
    background: {PALETTE['bg_elevated']};
    color: {PALETTE['text_muted']};
    border: 1px solid {PALETTE['border']};
}}

/* ── Add File Button ─────────────────────────────────── */
QPushButton#addBtn {{
    background-color: {PALETTE['accent_dim']};
    color: {PALETTE['accent_hover']};
    border: 1px solid {PALETTE['accent_dim']};
    border-radius: 7px;
    font-weight: 600;
}}
QPushButton#addBtn:hover {{
    background-color: {PALETTE['accent']};
    color: #ffffff;
    border-color: {PALETTE['accent']};
}}

/* ── Danger Button ──────────────────────────────────── */
QPushButton#dangerBtn {{
    background-color: transparent;
    color: {PALETTE['error']};
    border: 1px solid rgba(240,82,82,0.35);
    border-radius: 7px;
}}
QPushButton#dangerBtn:hover {{
    background-color: {PALETTE['error_dim']};
    border-color: {PALETTE['error']};
}}
QPushButton#dangerBtn:disabled {{
    color: {PALETTE['text_muted']};
    border-color: {PALETTE['border']};
    background-color: transparent;
}}

/* ── Progress Bar ───────────────────────────────────── */
QProgressBar {{
    background-color: {PALETTE['bg_elevated']};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {PALETTE['accent']}, stop:1 {PALETTE['accent_hover']});
    border-radius: 4px;
}}

/* ── ComboBox ───────────────────────────────────────── */
QComboBox {{
    background-color: {PALETTE['bg_input']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 7px;
    padding: 6px 32px 6px 10px;
    color: {PALETTE['text_primary']};
    font-size: 13px;
    min-width: 180px;
}}
QComboBox:hover, QComboBox:focus {{
    border-color: {PALETTE['accent']};
    background-color: {PALETTE['bg_elevated']};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 26px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {PALETTE['text_secondary']};
}}
QComboBox QAbstractItemView {{
    background-color: {PALETTE['bg_elevated']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 7px;
    padding: 4px;
    selection-background-color: {PALETTE['accent_dim']};
    selection-color: {PALETTE['accent_hover']};
    color: {PALETTE['text_primary']};
    outline: none;
    font-size: 13px;
}}
QComboBox QAbstractItemView::item {{
    padding: 7px 10px;
    border-radius: 5px;
    min-height: 26px;
}}

/* ── SpinBox ────────────────────────────────────────── */
QSpinBox {{
    background-color: {PALETTE['bg_input']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 7px;
    padding: 6px 10px;
    color: {PALETTE['text_primary']};
    font-size: 13px;
}}
QSpinBox:hover, QSpinBox:focus {{
    border-color: {PALETTE['accent']};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: 16px;
}}
QSpinBox::up-arrow {{
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-bottom: 4px solid {PALETTE['text_secondary']};
}}
QSpinBox::down-arrow {{
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid {PALETTE['text_secondary']};
}}

/* ── LineEdit ───────────────────────────────────────── */
QLineEdit {{
    background-color: {PALETTE['bg_input']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 7px;
    padding: 7px 10px;
    color: {PALETTE['text_primary']};
    font-size: 13px;
}}
QLineEdit:hover {{
    border-color: {PALETTE['border_light']};
}}
QLineEdit:focus {{
    border-color: {PALETTE['accent']};
}}
QLineEdit:read-only {{
    color: {PALETTE['text_secondary']};
    background-color: {PALETTE['bg_card']};
}}
QLineEdit::placeholder {{
    color: {PALETTE['text_muted']};
}}

/* ── CheckBox ───────────────────────────────────────── */
QCheckBox {{
    spacing: 9px;
    color: {PALETTE['text_secondary']};
    font-size: 13px;
}}
QCheckBox:hover {{
    color: {PALETTE['text_primary']};
}}
QCheckBox::indicator {{
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1.5px solid {PALETTE['border_light']};
    background-color: {PALETTE['bg_input']};
}}
QCheckBox::indicator:hover {{
    border-color: {PALETTE['accent']};
}}
QCheckBox::indicator:checked {{
    background-color: {PALETTE['accent']};
    border-color: {PALETTE['accent']};
}}

/* ── GroupBox ───────────────────────────────────────── */
QGroupBox {{
    background-color: {PALETTE['bg_card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    margin-top: 18px;
    padding: 14px 14px 12px 14px;
    font-size: 10px;
    font-weight: 700;
    color: {PALETTE['text_muted']};
    letter-spacing: 1.2px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -1px;
    padding: 0 6px;
    background-color: {PALETTE['bg_card']};
    color: {PALETTE['text_muted']};
    border-radius: 3px;
}}

/* ── ScrollBar ──────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {PALETTE['border_light']};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {PALETTE['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}

/* ── Section Cards (options panel) ─────────────────── */
QWidget#sectionCard {{
    background: {PALETTE['bg_card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
}}
QWidget#sectionCard QLabel {{
    background: transparent;
}}
QWidget#sectionCard QWidget {{
    background: transparent;
}}

/* ── Tooltip ────────────────────────────────────────── */
QToolTip {{
    background-color: {PALETTE['bg_elevated']};
    color: {PALETTE['text_primary']};
    border: 1px solid {PALETTE['border_light']};
    border-radius: 6px;
    padding: 7px 11px;
    font-size: 12px;
}}

/* ── Status Bar Labels ──────────────────────────────── */
#statusLabel {{
    color: {PALETTE['text_secondary']};
    font-size: 12px;
}}
#sectionLabel {{
    color: {PALETTE['text_secondary']};
    font-size: 12px;
    font-weight: 600;
}}
#fileCount {{
    color: {PALETTE['text_muted']};
    font-size: 12px;
}}
"""