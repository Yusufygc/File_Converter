# Mimari

FileConvert, backend (`core/`) ve frontend'i (`ui_qml/`) **fiziksel
dizin sınırıyla** ayırır: `core/` hiçbir zaman Qt (PySide6) import etmez,
`ui_qml/` ise Qt Quick (QML) ve PySide6'ya %100 bağımlıdır. Bu ayrım
convention değil, test edilen bir invarianttır — bkz.
`tests/test_00_core_has_no_qt_dependency.py`.

Not: Uygulama başlangıçta PySide6 **widgets** tabanlı bir `ui/` katmanıyla
başlamıştı; bu tamamen kaldırılıp yerini `ui_qml/` (Qt Quick) aldı —
bkz. [[log]]. Aşağıdaki katman şeması güncel/aktif mimariyi yansıtır.

## Katmanlar

```
core/                     Backend — framework-agnostic, senkron
  interfaces/
    converter_interface.py   IConverter, IConverterRegistry, value object'ler
    engine_interface.py      IEngineSelectable (opsiyonel capability)
    merge_interface.py       IMergeConverter (opsiyonel capability, N:1)
  converters/
    base.py                  BaseConverter + MergeCapableConverter (template method)
    discovery.py              Otomatik converter keşfi
    registry.py                ConverterRegistry (anahtar: source+target+sınıf adı)
    libreoffice_engine.py       Paylaşılan LibreOffice motoru
    ocr_engine.py               Tesseract OCR + PyMuPDF köprüsü
    pptx_to_pdf.py, pdf_to_docx.py, pdf_to_jpg.py, jpg_to_pdf.py, ...
  conversion_facade.py       convert_batch()/convert_batch_parallel()/merge_files()
                              — senkron, Qt'siz backend API'si

ui_qml/                    Frontend — Qt Quick (QML) + PySide6 köprüsü
  bridge/
    app_bridge.py             AppBridge (QObject) — converter kataloğu,
                               kategori/ikon ataması, dönüşüm orkestrasyonu
    app_settings.py            QmlAppSettings — QSettings sarmalayıcı
    conversion_worker.py       QmlConversionWorker/QmlMergeWorker (QThread)
    file_list_model.py         FileListModel (QAbstractListModel)
    file_discovery.py          collect_files() — saf pathlib, Qt'siz
  qml/
    Main.qml                   Kök pencere
    Theme.qml                  Açık/koyu tema renk sabitleri
    Icons.js                   Merkezi ikon glyph tablosu (bkz. [[ui-katmani]])
    components/                HeaderBar, CategorySidebar, MainCanvas,
                                OptionsCard, SettingsView, FileListView,
                                SummaryModal, ModernButton, ModernComboBox, ...
```

**Registry anahtarı**: `ConverterRegistry`'nin iç anahtarı yalnızca
`(source_ext, target_ext)` değil, sınıf adını da içerir —
`PdfCompressConverter`/`PdfSplitConverter`/`PdfMergeConverter` üçü de
`.pdf`→`.pdf` olduğu için sınıf adı olmadan birbirini ezerlerdi (bulunan
gerçek bir bug). Kamuya açık `register()`/`get()`/`all_converters()`
imzaları değişmedi.

## Veri Akışı (bir dönüşüm isteği)

1. Kullanıcı `CategorySidebar`/`OptionsCard`'daki dropdown'dan bir
   converter seçer → QML `bridge.selectConverter(index)` çağırır.
2. `AppBridge.selectConverter()` bunu `self._active_index`/
   `self._active_converter` yapar, `currentConverterChanged` sinyaliyle
   QML'e bildirir; `DropZoneWidget`'ın kabul ettiği uzantılar,
   `IMergeConverter`/`IPageRangeSelectable`/`IEngineSelectable`
   `isinstance()` kontrolleriyle QML tarafında ilgili seçenekler
   (birleştirme kutusu, aralık alanı, motor combobox'ı) gösterilir/gizlenir.
3. Kullanıcı dosya sürükler/seçer → `FileListModel` (QML `FileListView`).
4. "Dönüştür" → `AppBridge.startConversion()`, iki yoldan biri:
   - **Normal (1:N)**: `QmlConversionWorker` (QThread) →
     `converter.is_parallel_safe`'e göre `core.conversion_facade.convert_batch()`
     (sıralı) veya `convert_batch_parallel()` (`ThreadPoolExecutor`,
     yalnızca PyMuPDF-tabanlı converter'lar) → her dosya için
     `converter.convert(path, options)` → `ConversionResult`.
   - **Birleştirme (N:1)**: birleştirme kutusu işaretliyse
     `QmlMergeWorker` → `core.conversion_facade.merge_files()` →
     `converter.convert_many(paths, options)` → TEK bir `ConversionResult`,
     `BatchConversionResult(results=[result])`'a sarılır (`SummaryModal`
     değişmeden çalışır).
5. Sonuçlar Qt sinyalleriyle (`progress`, `file_completed`,
   `batch_completed`/`merge_completed`) `AppBridge`'e taşınır,
   `statusMessage`/`statusKind`/`summaryData` property'leri güncellenir,
   `showSummaryModal` `true` olunca QML `SummaryModal` görünür olur.

## Neden bu ayrım

`core/`'un Qt'siz olması iki şey sağlar: (1) `tests/` altındaki testler
milisaniyeler içinde, PySide6 başlatmadan çalışır: bkz. [[test-ve-bagimliliklar]];
(2) backend teorik olarak bir CLI veya farklı bir UI framework'üyle de
kullanılabilir — `conversion_facade.convert_batch()` tek giriş noktasıdır.

## İlgili Sayfalar

- [[converter-arayuzu]] — `IConverter`/`BaseConverter` sözleşmesi
- [[converter-ekleme]] — yeni dönüşüm türü ekleme rehberi
- [[ui-katmani]] — UI bileşenlerinin detayı
- [[rules]] — bu mimariyi koruyan kurallar
