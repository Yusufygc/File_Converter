# UI Katmanı

`ui_qml/` — Qt Quick (QML) arayüzü + PySide6 köprüsü, [[mimari]]'de
tarif edilen backend/frontend ayrımının Qt'ye bağımlı yarısı. Eski
PySide6-widgets tabanlı `ui/` katmanı tamamen kaldırıldı — bkz. [[log]].

## `ui_qml/bridge/app_bridge.py` — `AppBridge`

Composition root / controller; `QObject` türevi, `Property`/`Signal`/
`Slot` ile QML'e reaktif iki yönlü bağlanır. Sorumlulukları:
- **Dependency composition**: `__init__()`'te `ConverterRegistry`
  oluşturur, `core.converters.discovery.register_all()` ile doldurur.
- **Kategorileme** (`ui_qml/bridge/converter_catalog.py`): kenar çubuğu
  grupları, grup içi sıra, kısa ad ve ikon **tek tablodan** gelir
  (sınıf adı → `CatalogEntry(group, short_name, icon)`). Gruplar kullanıcının
  niyetine göre: PDF'e Dönüştür (5), PDF'ten Dönüştür (8), PDF Düzenle (5),
  Güvenlik ve Bakım (5), Ofis Biçimleri (9). Tabloda olmayan converter
  "Diğer" grubunda adıyla görünür; `tests/test_converter_catalog.py` eksik
  satırı yakalar. Tablo sırası aynı zamanda converter listesinin sırası
  (eski `_PREFERRED_ORDER`) ve dosya bırakılınca otomatik seçilecek aracın
  önceliğidir. Eski sınıf adı/uzantı kuralları (`_categorize_converter`,
  `_PDF_TOOL_META`) kaldırıldı: gruplar iki eksene dağılmıştı, PDF ile
  başlayan bir iş dört grupta aranıyordu (bkz. [[log]]).
- **Dosya-önce akışı** (`_add_paths`): dosya listesi her zaman **tek
  türdür**. Liste boşken bırakılan dosyaların çoğunluk türü alınır, doluyken
  listedeki tür; diğerleri eklenmez ve durum çubuğunda bildirilir
  ("Farklı türde N dosya eklenmedi (Word)"; desteklenmeyen biçimler de).
  Etkin araç o türü kabul etmiyorsa katalog sırasındaki ilk uygun araç
  seçilir (.pdf → PDF → Word, .xlsx → Excel → PDF...). `selectConverter()`
  dosyalar yeni araca uyuyorsa listeyi KORUR, uymuyorsa temizler.
  `fileTypeFilter`/`fileTypeLabel` kenar çubuğunu süzer; `.jpeg` = `.jpg`
  (`converter_catalog.normalize_ext`). Kararlar kullanıcı onaylı (2026-11-13).
- **Dönüşüm orkestrasyonu**: `startConversion()` → `QmlConversionWorker`
  (normal, 1:N) veya `QmlMergeWorker` (birleştirme, N:1) — ikisi de
  `core.conversion_facade`'i çağırır, sonuçları sinyallerle taşır.
  `_set_status(message, kind)` — `statusMessage`/`statusKind`
  property'lerini birlikte günceller (`kind`: `neutral`/`success`/
  `warning`) — `FooterBar.qml` bunu renklendirmede kullanır, emoji
  gerekmez.
- **Araca özgü seçenekler** ([[converter-arayuzu]] `IOptionsProvider`):
  converter sözlüklerinde (`converters`, `categorizedConverters`,
  `currentConverter`) `optionSpecs` listesi yayınlanır; QML her alan
  değiştiğinde `setExtraOption(key, value)` çağırır (şemada olmayan
  anahtarlar yok sayılır). `_extra_options` converter değişiminde ve
  açılışta şema varsayılanlarına döner, `_build_options()` bunu
  `ConversionOptions.extra`'ya kopyalar. **Parola dahil bu değerler
  bilinçli olarak QSettings'e yazılmaz.**
- **Ayarlar**: `QmlAppSettings` üzerinden tema/çıktı klasörü/kalite
  ayarlarını kalıcı saklar. `FILECONVERT_HOME` ayarlıysa (testler,
  derleme sonrası exe denemesi) kayıt defteri yerine o klasördeki
  `settings.ini`'ye yazar — gerçek kullanıcı ayarlarına dokunulmaz.
- Açılışta yüklenen converter sayısını ve kullanılamayanları günlüğe yazar
  (paketlenmiş exe'de eksik modül tanısı, bkz. [[paketleme]]).

## `ui_qml/bridge/update_bridge.py` — `UpdateBridge`

QML'e `updateBridge` adıyla bağlanır; `UpdateModal.qml` ve Ayarlar'daki
"Güncellemeler" kartını `core/update_service.py`'ye bağlar. Ayrıntı:
[[guncelleme-sistemi]].

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
  `bridge.categorizedConverters`'tan **jenerik** üretilen grup ağacı.
  Akordeon: aynı anda tek grup açık (başta ve araç değişince etkin aracın
  grubu); arama ya da dosya süzgeci varken eşleşen tüm gruplar açık.
  Liste doluyken "PDF dosyaları için uygun araçlar · Listeyi temizle"
  şeridi çıkar ve başlıktaki sayı "18 / 32" olur.
- `DropZone.qml` — liste boşken tüm desteklenen türleri
  (`supportedTypesStr`) ve "uygun araç otomatik seçilir" yazar; dosya
  seçme penceresi de liste boşken tüm türleri kabul eder.
- `MainCanvas.qml` / `OptionsCard.qml` — dönüşüm seçenekleri + büyük
  CTA butonu (`bridge.isConverting`'e göre `convert`/`cancel` glyph +
  "Dönüştür"/"İptal Et" metni).
- `DynamicOptionField.qml` — tek bir `OptionSpec`'i `kind`'a göre
  `ModernTextField` (password: `echoMode: Password`), `ModernComboBox`
  veya `ModernSpinBox` olarak çizer. `MainCanvas.qml`'de seçenek kartının
  üçüncü satırında `Repeater { model: currentConverter.optionSpecs }`
  içinde kullanılır; converter değişince alanlar yeniden çizilir.
  (`OptionsCard.qml` hiçbir yerde örneklenmiyor — yeni alanlar oraya eklenmedi.)
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

### Koyu Tema Renk Paleti (Gunmetal & Silver)
Paletin 5 rengi anlamsal UI rollerine şu şekilde dağıtılmıştır:
1. **GUNMETAL** (`#292C36`): Ana pencere tabanı (`bgPrimary`), kademeli yüzey türetimi (`bgSurface`, `bgCard`, `bgElevated`, `bgInput`, `bgHover`) ve açık renkli butonlarda yüksek kontrastlı metin/ikon rengi.
2. **ROMAN SILVER** (`#848A98`): Soluk/ikincil metinler (`textMuted`), dosya boyutları, yer tutucular, hafif çerçeveler (`border`) ve kart içi ayraçlar.
3. **COOL GREY** (`#8E99AC`): Giriş/seçim kutuları ve butonların sınır çizgileri (`borderLight`), yarı saydam seçim arka planı (`accentDim`), rozet bordürleri.
4. **SILVER SAND** (`#BDC2C7`): Birincil yüksek kontrastlı metinler (`textPrimary`), ana dönüştürme butonu (`accent`), aktif seçim göstergeleri.
5. **METALLIC SILVER** (`#A1A7AF`): İkincil başlıklar ve etiketler (`textSecondary`), butonların üzerine gelindiğindeki vurgu sınırları.

### Açık Tema Renk Paleti (Jet Stream & Slate)
Açık temadaki 5 resmî renk anlamsal UI rollerine şu şekilde dağıtılmıştır:
1. **JET STREAM** (`#C1D1CF`): Ana pencere taban zemini (`bgPrimary`) ve kademeli açık yüzeyler (`bgElevated`: `#CFDCDA`).
2. **DARK JUNGLE GREEN** (`#171F22`): Birincil yüksek kontrastlı metinler (`textPrimary`), ana dönüştürme butonu (`accent`), aktif seçim göstergesi ve aktif onay kutuları.
3. **GRANITE GRAY (Slate)** (`#636467`): İkincil başlıklar, etiketler (`textSecondary`, `"Format:"`, `"Klasör:"`), hover sınırları.
4. **LIGHT SLATE GRAY** (`#748B91`): Soluk/ikincil metinler (`textMuted`), rozet bordürleri, yarı saydam seçim arka planı (`accentDim`).
5. **GRANITE GRAY (Sage)** (`#666B64`): Giriş/seçim kutuları, arama çubuğu ve buton kenarlıkları (`borderLight`), hafif çerçeveler (`border`).

## İlgili Sayfalar

- [[mimari]] — bu katmanın genel akıştaki yeri
- [[converter-arayuzu]] — `IEngineSelectable` kontrolünün dayandığı sözleşme
- [[converter-ekleme]] — yeni converter eklerken `AppBridge`'e dokunulmaması
- [[log]] — eski `ui/` katmanının kaldırılma kaydı
