# Kronolojik Kayıt

En yeni girişler en üstte. Format: `[YYYY-AA-GG] [İŞLEM_TİPİ] | Açıklama`
İşlem tipleri: `INGEST` (yeni özellik/kaynak), `REFACTOR` (mimari
değişiklik), `FIX` (hata düzeltme), `DOCS` (dokümantasyon).

## [2026-09-24] [FIX] | Converter seçiminde donma — OcrEngine.is_available() cache'lenmedi

Kullanıcı raporu: "PDF → DOCX"/"PDF → TXT" seçilince kısa bir donma/
kasılma oluyordu. Kök neden: `OcrEngine.is_available()`
(`core/converters/ocr_engine.py`) her çağrıda `pytesseract.get_tesseract_version()`
ile bir `tesseract.exe --version` subprocess'i başlatıyordu, sonucu
hiç cache'lemiyordu. `PdfToDocxConverter`/`PdfToTxtConverter`'ın
`active_engine_name`/`is_available`/`available_engines()` property'leri
bunu ayrı ayrı çağırıyor; `AppBridge.selectConverter()`'ın emit ettiği
sinyallere bağlı `SettingsView.qml` (her zaman canlı, Loader değil)
tek bir converter seçiminde bu subprocess'i 3-4 kez tetikliyordu —
UI thread senkron blokleniyordu. Tesseract bu oturumda kurulana kadar
`_tesseract_cmd` `None` olduğu için erken dönüş yapılıyordu, sorun
gözükmüyordu; kurulumdan sonra ortaya çıktı. Çözüm: `OcrEngine`'e
instance ömrü boyunca geçerli `_available_cache` eklendi — ilk çağrı
gerçek kontrolü yapar (~140ms), sonraki tüm çağrılar anında döner
(~0ms). Detay: [[test-ve-bagimliliklar]].

## [2026-09-24] [INGEST] | Yeni Gunmetal & Silver uygulama ikonu ve çoklu-çözünürlüklü .ico paketi

Eski mavi şimşek ikonu yerine, uygulamanın dosya dönüştürme kimliğini ve
yeni Gunmetal & Silver tasarım dilini yansıtan profesyonel bir masaüstü ikonu
tasarlandı ve üretildi.
- `assets/icons/app_icon.ico`: Windows standartlarındaki tüm piksel
  ölçülerini (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256) tek bir
  çoklu-çözünürlüklü ICO dosyasında barındırır; `fileconvert.spec` ve
  `setup.iss` ile exe/kısayol/kurulum simgeleri güncellendi.
- `assets/icons/app_icon.png` (512x512) ve ayrık PNG varyantları (`app_icon_16`,
  `_24`, `_32`, `_48`, `_64`, `_128`, `_256`).
- `assets/icons/app_icon.svg`: Vektörel yedek logo dosyası yenilendi.
- `AppBridge.appIconUrl` artık doğrudan yüksek çözünürlüklü ve şeffaf
  `app_icon.png`'yi HeaderBar ve DropZone'a besliyor. Detay: [[paketleme]], [[ui-katmani]].

## [2026-09-24] [REFACTOR] | Açık tema: Jet Stream & Slate 5'li resmî renk paleti entegrasyonu

Açık temadaki eski mavi (`#3B6FD6`, `#DCE6FB`) ve eksik kalan vurgu mekanizmaları
kaldırılarak 5'li resmî paletin tamamı (`jetStream`: `#C1D1CF`, `darkJungleGreen`:
`#171F22`, `graniteGray`: `#636467`, `lightSlateGray`: `#748B91`, `sageGranite`:
`#666B64`) anlamsal rollere eksiksiz bağlandı:
- `jetStream` (`#C1D1CF`): Ana pencere tabanı (`bgPrimary`) ve açık zemin kademeleri.
- `darkJungleGreen` (`#171F22`): Birincil tipografi (`textPrimary`), ana eylem butonu (`accent`, "Dönüştürmeyi Başlat"), aktif seçim çubuğu ve aktif onay kutusu.
- `graniteGray` (`#636467`): İkincil tipografi (`textSecondary`), etiketler ve buton hover sınırları.
- `lightSlateGray` (`#748B91`): Soluk/ikincil metinler (`textMuted`), rozet çerçeveleri, yarı saydam seçim arka planı (`accentDim`).
- `sageGranite` (`#666B64`): Giriş/seçim kutuları, ComboBox, SpinBox ve arama çubuğu sınırları (`borderLight`), hafif çerçeveler (`border`).
`MainCanvas.qml` içindeki gereksiz `accentColor` override'ı temizlenerek her iki
temada da `theme.accent`'e homojen geçiş sağlandı. Detay: [[ui-katmani]].

## [2026-09-24] [REFACTOR] | Koyu tema: Gunmetal & Silver 5'li resmî renk paleti entegrasyonu

Koyu temadaki eski mavi (`#4B8CF5`, `#1E3A7A`) ve belirsiz çerçeve değerleri
kaldırılarak 5'li resmî paletin tamamı (`gunmetal`: `#292C36`, `romanSilver`:
`#848A98`, `coolGrey`: `#8E99AC`, `silverSand`: `#BDC2C7`, `metallicSilver`:
`#A1A7AF`) anlamsal rollere eksiksiz bağlandı:
- `gunmetal` (`#292C36`): Ana taban zemini (`bgPrimary`), kademeli yüzeyler ve açık renkli butonlarda ters metin rengi.
- `silverSand` (`#BDC2C7`): Birincil tipografi (`textPrimary`), ana eylem butonu (`accent`, "Dönüştürmeyi Başlat"), aktif seçim göstergeleri.
- `metallicSilver` (`#A1A7AF`): İkincil tipografi (`textSecondary`), etiketler, buton hover sınırları.
- `coolGrey` (`#8E99AC`): Belirgin kenarlıklar (`borderLight`), arama ve giriş kutuları, rozetler, seçim arka planı (`accentDim`).
- `romanSilver` (`#848A98`): Soluk/açıklama metinleri (`textMuted`), kart ve panel ayracı hafif çerçeveler (`border`).
`ModernButton.qml`, `CategorySidebar.qml` ve `ModernCheckBox.qml` içindeki
kontrastlar Gunmetal/Silver Sand kombinasyonuna uyarlandı. Detay: [[ui-katmani]].

## [2026-09-24] [FIX] | PDF Böl: sayfa aralığı artık TEK PDF üretiyor

Kullanıcı geri bildirimi: 2 PDF'i "1-3" aralığıyla bölünce 6 ayrı dosya
(her sayfa kendi dosyasına) çıktı — beklenti aralığın **tek bir PDF**
olarak birleştirilmesiydi. `PdfSplitConverter._do_convert()` artık
`options.page_range` doluysa seçili sayfaları TEK bir `fitz.open()`
belgesinde birleştirip `ad_sayfa1-2-3.pdf` gibi tek dosya üretiyor;
aralık **boşsa** eski davranış (her sayfa ayrı dosya) korunuyor.
`tests/test_pdf_split_converter.py`'deki ilgili testler yeni davranışa
göre güncellendi. Detay: [[donusturucu-envanteri]].

## [2026-09-24] [REFACTOR] | Emoji'ler kaldırıldı — Icons.js merkezi ikon mekanizması

`ui_qml/` genelinde (Python bridge + QML) ⚡✅❌📁🔄☀️🌙✕✓⚠🔍⚙️🗜️✂️📑📝🖼️📊📄
gibi ham emoji karakterleri kaldırıldı — platforma/fonta göre tutarsız
render eden renkli emoji yerine `ui_qml/qml/Icons.js` (`.pragma library`)
üzerinden Windows sistem fontu **Segoe Fluent Icons**'tan tek renkli
glyph'ler kullanılıyor. `AppBridge` artık codepoint değil semantik ikon
key'i üretiyor (`"convert"`, `"cancel"`, `"document"` vb.) — hangi
glyph'in hangi şekle karşılık geldiğini yalnızca QML tarafı bilir.
`ModernButton.qml`'e `iconGlyph` property'si, `ModernComboBox.qml`'e
model item'ının `"icon"` alanından otomatik glyph render'ı eklendi.
`AppBridge`'e `statusKind` property'si eklendi (`FooterBar.qml` artık
✅/⚠ yerine rengiyle ayırt ediyor, `FileListView.qml`'deki durum
rozeti deseniyle aynı fikir). Detay: [[ui-katmani]].

## [2026-09-24] [REFACTOR] | Eski `ui/` (PySide6 widgets) katmanı kaldırıldı

`main.py` uzun süredir `ui_qml/` (Qt Quick) üzerinden çalışıyordu;
eski PySide6-widgets `ui/` katmanı "yedek" olarak duruyordu ama
`ui_qml/bridge/app_bridge.py` hâlâ `ui/file_discovery.py`'yi import
ediyordu — tam anlamıyla ölü kod değildi. `file_discovery.py`
`ui_qml/bridge/file_discovery.py`'ye taşındı (`tests/test_file_discovery.py`
import'u güncellendi), ardından `ui/` dizini komple silindi
(`main_window.py`, `converter_catalog.py`, `app_settings.py`,
`icon_map.py`, `adapters/`, `widgets/`, `dialogs/`, `styles/`).
`docs/wiki/mimari.md`, `docs/wiki/ui-katmani.md`, `docs/wiki/rules.md`,
`docs/wiki/converter-ekleme.md`, `docs/wiki/test-ve-bagimliliklar.md`,
`docs/wiki/donusturucu-envanteri.md`, `README.md`, `CLAUDE.md` güncel
mimariyi (`ui_qml/`) yansıtacak şekilde güncellendi. Test sayısı
değişmedi (110), CI etkilenmedi. Detay: [[mimari]], [[ui-katmani]].

## [2026-09-16] [INGEST] | Akıllı PDF Analizi (PdfInspector) ve OCR Motoru Entegrasyonu

Taranmış (görüntü tabanlı) ve dijital PDF'lerin dönüşüm kalitesini artırmak için
`core/utils/pdf_inspector.py` ve `core/converters/ocr_engine.py` eklendi.
Dijital PDF'ler doğrudan `pdf2docx` ile 1-2 saniyede kusursuz dönüştürülür.
Taranmış PDF'lerde ise Tesseract OCR varsa metin çıkarılarak düzenlenebilir
Word belgesi üretilir; OCR yoksa LibreOffice'in çizimleri parçalama hatası yerine
`python-docx` ile temiz, bozulmayan sayfa görselleri gömülür. `PdfToTxtConverter`'a
da OCR desteği eklendi. Test sayısı 106'dan 109'a çıktı. Detay: [[donusturucu-envanteri]].

## [2026-09-15] [INGEST] | QML (Qt Quick) modern arayüz mimarisi inşa edildi

`ui_qml/` altında sıfırdan modern, akıcı ve animasyonlu PySide6 QML (Qt Quick)
arayüzü oluşturuldu. Backend (`core/`) katmanına kesinlikle dokunulmadı; eski `ui/`
katmanı yedek olarak korundu. `AppBridge` (`QObject`) ve `FileListModel`
(`QAbstractListModel`) köprüsüyle tüm converter kataloğu, sürükle-bırak,
motor seçimi, sayfa aralığı, birleştirme modu ve kalite kontrolleri QML'e
bağlandı. Açık/Koyu (Light/Dark) tema geçişi dinamikleştirildi ve `QSettings` ile
kalıcı hale getirildi. `main.py` yeni QML motoruna (`QQmlApplicationEngine`)
bağlandı. Test sayısı 102'den 106'ya çıktı. Detay: [[ui-katmani]].

## [2026-09-15] [FIX] | ComboBox popup + QFont uyarısı + canlı tema geçişi

Native Windows stili (`windowsvista`/`windows11`) QSS'i tam
desteklemediği için `QComboBox` popup'ı okunaksız (siyah) çiziliyordu
ve popup boyutlandırma kodu `QFont::setPointSize: Point size <= 0`
uyarısı basıyordu — `main.py`'de `QApplication.setStyle(QStyleFactory.create("Fusion"))`
eklenerek kökten çözüldü. Ayrıca tema geçişi artık restart gerektirmiyor:
`ui/styles/theme.py`'ye `apply_theme(mode)` eklendi (kritik detay:
`PALETTE` artık `DARK_PALETTE`/`LIGHT_PALETTE`'in kendisi değil bir
**kopyası** — `apply_theme()` onu yerinde `clear()`+`update()` ile
değiştiriyor; kopyalanmasaydı bu işlem sabit paletleri de bozardı).
Statik (tema dışı değişmeyen) inline `setStyleSheet()` çağrıları
merkezi QSS'e objectName selector'larıyla taşındı
(`options_panel.py`, `drop_zone.py`, `file_list.py`, `main_window.py`);
duruma göre renklenen (başarı/hata/uyarı) birkaç widget
`retheme()`/`_refresh_engine_display()` ile tema değişince son
durumunu güncel `PALETTE`'ten yeniden okuyor. Detay: [[ui-katmani]].

## [2026-09-13] [INGEST] | PDF Böl: sayfa/aralık seçimi

`PdfSplitConverter` artık `options.page_range` ile "1-3,5,7-9" gibi bir
aralık kabul ediyor — boşsa eski davranış (tüm sayfalar) korunuyor.
`IEngineSelectable`/`IMergeConverter` ile aynı opsiyonel capability
deseninde yeni `IPageRangeSelectable` (`core/interfaces/page_range_interface.py`)
eklendi; `MainWindow` belirli bir converter'ı hardcode etmeden
`isinstance()` ile options panelindeki "Aralık:" alanını gösterip
gizliyor (`OptionsPanelWidget.set_page_range_available()`). Seçilen
sayfalar kaynaktaki gerçek numarasıyla adlandırılıyor (`ad_sayfa3.pdf`),
sıralı yeniden numaralandırma yok. Geçersiz aralık `ValueError` fırlatır,
mevcut `BaseConverter.convert()` try/except'i bunu `error_message`'a
çevirir — ayrı hata yolu eklenmedi. Test sayısı 96'dan 102'ye çıktı.
Detay: [[donusturucu-envanteri]], [[converter-arayuzu]], [[ui-katmani]].

## [2026-09-12] [INGEST] | Ofis format genişletmesi: 9 yeni converter

Word/Excel/PDF/CSV/ODT/ODS arası eksik yaygın dönüşümler eklendi
(Tier A, kullanıcı onayıyla daraltılmış kapsam): `PdfToTxtConverter`
(PyMuPDF), `DocxToTxtConverter` (python-docx), ve `LibreOfficeEngine`
üzerinden 7 tanesi (`XlsxToPdfConverter`, `XlsxToCsvConverter`,
`CsvToXlsxConverter`, `DocxToOdtConverter`, `OdtToDocxConverter`,
`XlsxToOdsConverter`, `OdsToXlsxConverter`) — bu 7'si tek bir taban
sınıftan (`SimpleLibreOfficeConverter`, `core/converters/office_conversions.py`)
türer, her biri ~8 satır. **JSON/XML tamamen kapsam dışı bırakıldı**
(veri-dönüştürme, farklı problem sınıfı — kullanıcı onayladı). CLI
modu (Kademe 3, madde 14) kullanıcı tarafından açıkça reddedildi.
Converter sayısı 10'dan 19'a, test sayısı 46'dan 96'ya çıktı. Detay:
[[donusturucu-envanteri]], [[converter-arayuzu]], [[yol-haritasi]].

## [2026-09-12] [INGEST] | Kademe 2 kalan 3 madde (8, 10, 11) tamamlandı

Daha önce N:1 mimari genişlemesi/LibreOffice eşzamanlılık riski
gerekçesiyle ertelenen 3 madde çözüldü. `IMergeConverter` (yeni
`core/interfaces/merge_interface.py`) + `MergeCapableConverter`
(`core/converters/base.py`) — `IEngineSelectable` ile aynı desende
opsiyonel capability, mevcut 1:1 `convert()` akışına dokunmadı.
`JpgToPdfConverter` genişletildi (`convert_many`), yeni `PdfMergeConverter`
ve `PdfSplitConverter` eklendi. UI'da "Tüm dosyaları TEK çıktıda
birleştir" onay kutusu (ayrı dropdown öğesi değil). Paralel toplu
dönüşüm: `is_parallel_safe` (varsayılan `False`), `convert_batch_parallel()`
yalnızca 6 PyMuPDF-tabanlı converter'da devrede — gerçek PyMuPDF ile
denendi (10 dosya, 1.37x hızlanma, veri bozulması yok). Yan bulgu:
`ConverterRegistry`'nin anahtar çakışması bug'ı bulunup düzeltildi
(üç `.pdf`→`.pdf` converter'ı aynı slotu paylaşıyordu). Test sayısı
31'den 46'ya çıktı. Detay: [[mimari]], [[converter-arayuzu]],
[[donusturucu-envanteri]], [[ui-katmani]], [[yol-haritasi]].

## [2026-09-12] [INGEST] | Kademe 2 güvenli 4 madde tamamlandı

Yol haritasındaki (bkz. [[yol-haritasi]]) 7 Kademe 2 maddesinden N:1
mimari genişlemesi gerektiren (8, 10) ve LibreOffice eşzamanlılık
riski taşıyan (11) kullanıcı kararıyla ertelendi; güvenli 4 madde
uygulandı: `DocxToPdfConverter`, `PdfCompressConverter` (üzerine yazma
korumalı `get_output_path()` override'ı ile), `ui/file_discovery.py`
(klasör sürükle-bırak, alt klasörler dahil), açık/koyu tema
(`LIGHT_PALETTE` + `AppSettings` tema tercihi, yeniden başlatınca
uygulanır — canlı geçiş değil). Test sayısı 18'den 31'e çıktı. Detay:
[[donusturucu-envanteri]], [[ui-katmani]], [[test-ve-bagimliliklar]].

## [2026-09-12] [INGEST] | Kademe 1 tamamlandı

Yol haritasındaki (bkz. [[yol-haritasi]]) 6 hızlı-kazanım maddesi
uygulandı: iptal butonu (tek buton toggle), `PdfToPngConverter`,
dosya türü ikonları (`ui/icon_map.py`), `AppSettings` (QSettings ile
pencere/converter/seçenek kalıcılığı), `.github/workflows/test.yml`
(CI), `fileconvert.spec` (PyInstaller — gerçek bir build ile
`dist/FileConvertPro/FileConvertPro.exe` üretilip başlatılarak
doğrulandı). Test sayısı 14'ten 18'e çıktı. Detay: [[ui-katmani]],
[[donusturucu-envanteri]], [[paketleme]], [[test-ve-bagimliliklar]].

## [2026-09-12] [DOCS] | Yol haritası raporu eklendi

Yeni versiyon için kademeli (hızlı kazanım / orta vadeli / stratejik)
özellik önerileri raporu yazıldı — bkz. [[yol-haritasi]].

## [2026-09-12] [DOCS] | Wiki mekanizması kuruldu

`docs/wiki/` altında bu bilgi tabanı ve proje kökünde `CLAUDE.md`
oluşturuldu — bkz. [[index]].

## [2026-09-12] [REFACTOR] | Backend/frontend ayrımı ve tak-çıkar mimari

`core/` katmanı Qt bağımlılığından tamamen ayrıldı
(`core/conversion_facade.py`, `ui/adapters/qt_conversion_runner.py`).
`BaseConverter` template method ile her converter'daki tekrar eden kod
(~15-20 satır × 5 dosya) tek yere toplandı. `core/converters/discovery.py`
ile otomatik converter keşfi eklendi — `CONV_*` sabitleri, `conv_map`,
hardcoded dropdown `addItem()` çağrıları kaldırıldı. `IEngineSelectable`
opsiyonel capability protokolü ile motor-seçimi UI mantığı belirli bir
dönüşüm türünü hardcode etmekten kurtarıldı. Paylaşılan
`LibreOfficeEngine` ile PPTX/PDF-DOCX'teki ~60 satırlık kod tekrarı
giderildi. `core/` için Qt gerektirmeyen 14 pytest testi eklendi
(`tests/`). Detay: [[mimari]], [[converter-arayuzu]], [[rules]].

## [2026-09-12] [INGEST] | PDF→JPG ve JPG→PDF dönüştürücüleri eklendi

PyMuPDF (`fitz`) ile `PdfToJpgConverter` (çok sayfalı PDF'te her sayfa
ayrı JPG) ve `JpgToPdfConverter` (`.jpg`+`.jpeg` kabul eden, tek sayfalı
PDF üreten) eklendi. Options panel'e JPEG kalite ayarı, özet dialoguna
sayfa sayısı gösterimi eklendi. Detay: [[donusturucu-envanteri]].

## [2026-03-17] [INGEST] | Dosya listesi hover/solukluk düzeltmeleri

Yüklenen dosyaların isim ve boyut etiketlerindeki solukluk giderildi,
hover rengi dengelendi.

## [2026-03-17] [INGEST] | UI düzenlemesi yapıldı

Genel arayüz düzenlemesi (tema, layout).

## [2026-03-17] [INGEST] | Klasör yapısı ve temel kod iskeleti oluşturuldu

Proje temel dizin yapısı (`core/`, `ui/`, `services/`) ve ilk
`PptxToPdfConverter` implementasyonu oluşturuldu.
