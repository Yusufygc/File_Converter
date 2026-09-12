# Mimari

FileConvert Pro, backend (`core/`) ve frontend'i (`ui/`) **fiziksel dizin
sınırıyla** ayırır: `core/` hiçbir zaman Qt (PySide6) import etmez, `ui/`
ise Qt'ye %100 bağımlıdır. Bu ayrım convention değil, test edilen bir
invarianttır — bkz. `tests/test_00_core_has_no_qt_dependency.py`.

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
    pptx_to_pdf.py, pdf_to_docx.py, pdf_to_jpg.py, jpg_to_pdf.py, ...
  conversion_facade.py       convert_batch()/convert_batch_parallel()/merge_files()
                              — senkron, Qt'siz backend API'si

ui/                        Frontend — %100 PySide6
  main_window.py            Composition root / controller
  converter_catalog.py       registry'den dropdown listesi üretir
  adapters/
    qt_conversion_runner.py   ConversionWorker/MergeWorker — QThread'de çalıştırır
  widgets/, dialogs/, styles/
```

**Registry anahtarı**: `ConverterRegistry`'nin iç anahtarı yalnızca
`(source_ext, target_ext)` değil, sınıf adını da içerir —
`PdfCompressConverter`/`PdfSplitConverter`/`PdfMergeConverter` üçü de
`.pdf`→`.pdf` olduğu için sınıf adı olmadan birbirini ezerlerdi (bulunan
gerçek bir bug). Kamuya açık `register()`/`get()`/`all_converters()`
imzaları değişmedi.

## Veri Akışı (bir dönüşüm isteği)

1. Kullanıcı `OptionsPanelWidget` dropdown'ından bir `IConverter` seçer
   (`converter_type_changed` sinyali → `IConverter` nesnesinin kendisi taşınır,
   string sabit değil — bkz. [[converter-arayuzu]]).
2. `MainWindow._on_converter_type_changed()` bunu `self._active_converter`
   yapar, `DropZoneWidget`'ın kabul ettiği uzantıları günceller,
   `isinstance(converter, IMergeConverter)` ise birleştirme onay
   kutusunu gösterir.
3. Kullanıcı dosya sürükler/seçer → `FileListWidget`.
4. "Dönüştür" → `MainWindow._start_conversion()`, iki yoldan biri:
   - **Normal (1:N)**: `QtConversionRunner.start_batch_conversion()` →
     `ConversionWorker` (QThread) → `converter.is_parallel_safe`'e göre
     `convert_batch()` (sıralı) veya `convert_batch_parallel()`
     (`ThreadPoolExecutor`, yalnızca PyMuPDF-tabanlı converter'lar) →
     her dosya için `converter.convert(path, options)` → `ConversionResult`.
   - **Birleştirme (N:1)**: birleştirme kutusu işaretliyse
     `QtConversionRunner.start_merge_conversion()` → `MergeWorker` →
     `core.conversion_facade.merge_files()` → `converter.convert_many(paths, options)`
     → TEK bir `ConversionResult`, `BatchConversionResult(results=[result])`'a
     sarılır (`SummaryDialog` değişmeden çalışır).
5. Sonuçlar sinyallerle (`progress`, `file_completed`, `batch_completed`/`merge_completed`)
   UI thread'ine taşınır, `SummaryDialog` gösterilir.

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
