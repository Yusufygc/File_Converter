# UI Katmanı

`ui_qml/` — Qt Quick (QML) arayüzü + PySide6 köprüsü, [[mimari]]'de
tarif edilen backend/frontend ayrımının Qt'ye bağımlı yarısı. Eski
PySide6-widgets tabanlı `ui/` katmanı tamamen kaldırıldı — bkz. [[log]].

## `ui_qml/bridge/app_bridge.py` — `AppBridge`

Composition root / controller; `QObject` türevi, `Property`/`Signal`/
`Slot` ile QML'e reaktif iki yönlü bağlanır. Sorumlulukları:
- **Dependency composition**: `__init__()`'te `ConverterRegistry`
  oluşturur, `core.converters.discovery.register_all()` ile doldurur.
- **Kategorileme**: `_categorize_converter()` her converter'ı sınıf
  adı/uzantı kuralıyla (`Compress`/`Split`/`Merge` sınıf adı içeriyor mu,
  uzantı hangi grupta) bir kategoriye (`pdf_tools`/`images`/
  `spreadsheets`/`documents`) ve bir **ikon key'ine** (bkz. aşağıdaki
  "Merkezi İkon Mekanizması") atar — **kural tabanlı**, yeni bir
  converter eklendiğinde elle güncellenmesi gerekmez (bkz.
  [[converter-ekleme]]).
- **Dönüşüm orkestrasyonu**: `startConversion()` → `QmlConversionWorker`
  (normal, 1:N) veya `QmlMergeWorker` (birleştirme, N:1) — ikisi de
  `core.conversion_facade`'i çağırır, sonuçları sinyallerle taşır.
  `_set_status(message, kind)` — `statusMessage`/`statusKind`
  property'lerini birlikte günceller (`kind`: `neutral`/`success`/
  `warning`) — `FooterBar.qml` bunu renklendirmede kullanır, emoji
  gerekmez.
- **Ayarlar**: `QmlAppSettings` üzerinden tema/çıktı klasörü/kalite
  ayarlarını kalıcı saklar.

## `ui_qml/bridge/file_discovery.py`

`collect_files(directory, accepted_extensions) -> List[Path]` — saf
`pathlib`/`rglob` mantığı, Qt'den bağımsız (bu yüzden `tests/`'teki
hızlı, Qt'siz test paketine katılabiliyor — `tests/test_file_discovery.py`).
Eskiden `ui/file_discovery.py`'deydi, `ui/` kaldırılırken buraya taşındı.

## `ui_qml/bridge/file_list_model.py` — `FileListModel`

`QAbstractListModel` — dosya listesini QML `FileListView`'e sunar.
`FileItem.icon_url` dosya uzantısına göre `assets/icons/`'tan bir
ikon seçer (`_icon_url_for()`); `status_text` düz Türkçe metin döner
("Tamam (2.3s)", "Hata") — başarı/hata rengi zaten `FileListView.qml`'deki
durum rozetinin arka plan rengiyle taşınıyor, metne ayrıca sembol
gömülmez.

## `ui_qml/bridge/app_settings.py` — `QmlAppSettings`

`QSettings`'i sarmalar (pencere geometrisi, çıktı klasörü, DPI/kalite/
üzerine-yaz, tema tercihi). `ORG_NAME`/`APP_NAME` sabitlerini burada
tanımlar — `main.py` buradan alır.

## Merkezi İkon Mekanizması (`ui_qml/qml/Icons.js`)

Önceden onlarca yerde ham emoji karakteri (⚡✅❌📁🔄☀️🌙✕✓⚠🔍⚙️ vb.)
doğrudan `Text.text`'e veya bridge property'lerine gömülüydü — fonta/
platforma göre tutarsız render eden renkli emoji. Bunun yerine
Windows'un sistem fontu **Segoe Fluent Icons**'tan tek renkli glyph'ler
kullanılıyor (uygulama zaten Windows-only — `pywin32`, hardcoded
`C:\Program Files\...` yolları var, ek asset/bağımlılık gerekmez).

`Icons.js` (`.pragma library`) `GLYPHS` adında bir key→codepoint
tablosu ve `glyph(key)` fonksiyonu export eder. Python tarafı (`AppBridge`)
asla codepoint bilmez — yalnızca semantik key string'i (`"convert"`,
`"cancel"`, `"document"`, ...) üretir; hangi glyph'in hangi görsel
şekle karşılık geldiğini yalnızca QML/`Icons.js` bilir — katmanlar
arası sorumluluk ayrımı böyle korunur.

Kullanım deseni:
```qml
import "../Icons.js" as Icons
Text { font.family: Icons.FONT_FAMILY; text: Icons.glyph("convert") }
```

`ui_qml/qml/components/ModernButton.qml`'e `iconGlyph: string`
property'si eklendi (önceden bağlanmamış duran `iconSource` property'sinin
yanına) — `text:` ile birlikte veya tek başına kullanılabilir, ikon+
etiket arası boşluğu `Row.spacing` otomatik ayarlar (elle `"   "`
boşluk dolgusu gerekmez). `ModernComboBox.qml`'in hem kapalı hem açık
(popup) durumu, model item'ının `"icon"` alanı doluysa (converter
kataloğu ve `AppBridge.engineList` bunu taşır) otomatik bir glyph
gösterir.

## Widget/Bileşenler (`ui_qml/qml/components/`)

- `HeaderBar.qml` — logo, başlık, aktif format rozeti, sağda Ayarlar
  (`settings`/`back` glyph) ve Tema (`theme_light`/`theme_dark` glyph)
  butonları.
- `CategorySidebar.qml` — arama kutusu (`search`/`cancel` glyph),
  `bridge.categorizedConverters`'tan **jenerik** üretilen kategori
  ağacı (kategori ve item ikonları `Icons.glyph(modelData.icon)`).
- `MainCanvas.qml` / `OptionsCard.qml` — dönüşüm seçenekleri + büyük
  CTA butonu (`bridge.isConverting`'e göre `convert`/`cancel` glyph +
  "Dönüştür"/"İptal Et" metni).
- `FileListView.qml` — dosya listesi, boş durum ikonu (`folder_open`),
  satır-bazlı sil butonu (`cancel`).
- `SettingsView.qml` — motor seçimi (`ModernComboBox` + `engineList`),
  Tesseract OCR durum rozeti (`check`/`cancel` glyph + düz metin).
- `SummaryModal.qml` — sonuç listesi (satır başına `check`/`cancel`
  glyph, renk `theme.success`/`theme.error`), "Klasörü Aç" butonu
  (`folder_open`).
- `ModernButton.qml` / `ModernComboBox.qml` / `ModernCheckBox.qml` —
  paylaşılan, tema-duyarlı temel bileşenler; `Icons.js` entegrasyonu
  bunlarda merkezi.

## `ui_qml/qml/Theme.qml`

`QtObject` — açık/koyu palet renkleri, tipografi, radius sabitleri.
`mode` property'si `bridge.themeMode`'dan okunur; `Main.qml`'de
`id: theme` ile örneklenir, QML'in id-scope zinciri sayesinde tüm
alt bileşenlerden (ayrı dosyalarda tanımlı olsalar bile) doğrudan
`theme.xxx` ile erişilebilir.

## İlgili Sayfalar

- [[mimari]] — bu katmanın genel akıştaki yeri
- [[converter-arayuzu]] — `IEngineSelectable` kontrolünün dayandığı sözleşme
- [[converter-ekleme]] — yeni converter eklerken `AppBridge`'e dokunulmaması
- [[log]] — eski `ui/` katmanının kaldırılma kaydı
