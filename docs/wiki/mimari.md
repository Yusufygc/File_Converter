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
  converters/
    base.py                  BaseConverter (template method)
    discovery.py              Otomatik converter keşfi
    registry.py                ConverterRegistry
    libreoffice_engine.py       Paylaşılan LibreOffice motoru
    pptx_to_pdf.py, pdf_to_docx.py, pdf_to_jpg.py, jpg_to_pdf.py
  conversion_facade.py       convert_batch() — senkron, Qt'siz backend API'si

ui/                        Frontend — %100 PySide6
  main_window.py            Composition root / controller
  converter_catalog.py       registry'den dropdown listesi üretir
  adapters/
    qt_conversion_runner.py   convert_batch()'i QThread'de çalıştırır
  widgets/, dialogs/, styles/
```

## Veri Akışı (bir dönüşüm isteği)

1. Kullanıcı `OptionsPanelWidget` dropdown'ından bir `IConverter` seçer
   (`converter_type_changed` sinyali → `IConverter` nesnesinin kendisi taşınır,
   string sabit değil — bkz. [[converter-arayuzu]]).
2. `MainWindow._on_converter_type_changed()` bunu `self._active_converter`
   yapar, `DropZoneWidget`'ın kabul ettiği uzantıları günceller.
3. Kullanıcı dosya sürükler/seçer → `FileListWidget`.
4. "Dönüştür" → `MainWindow._start_conversion()` → `QtConversionRunner.start_batch_conversion()`.
5. `QtConversionRunner`, bir `QThread` (`ConversionWorker`) içinde
   `core.conversion_facade.convert_batch()`'i çağırır — asıl iş mantığı
   burada, Qt bilgisi olmadan çalışır.
6. Her dosya için `converter.convert(path, options)` → `BaseConverter`
   template method'u → `ConversionResult`.
7. Sonuçlar sinyallerle (`progress`, `file_completed`, `batch_completed`)
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
