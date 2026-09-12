# UI Katmanı

`ui/` — %100 PySide6, [[mimari]]'de tarif edilen backend/frontend
ayrımının Qt'ye bağımlı yarısı.

## `MainWindow` (`ui/main_window.py`)

Composition root / controller. Sorumlulukları:
- **Dependency composition**: `ConverterRegistry` oluşturur,
  `core.converters.discovery.register_all()` ile otomatik doldurur,
  `ui.converter_catalog.catalog_entries()` ile sıralı listeyi alır.
- Pencere inşası (`_build_header/_build_body/_build_toolbar/_build_footer`).
- Sinyal bağlama (`_connect_signals`).
- Aktif converter durumu (`self._active_converter`) ve motor yönetimi
  (`_populate_engines`, `_on_engine_changed` — `IEngineSelectable`
  kontrolüyle, bkz. [[converter-arayuzu]]).
- Dönüşüm başlatma (`_start_conversion` → `QtConversionRunner`).

## `ui/converter_catalog.py`

`registry.all_converters()`'dan dropdown listesini **jenerik** üretir.
`_PREFERRED_ORDER` yalnızca görünüm sırası (bkz. [[converter-ekleme]]).
Önceden bu işi `CONV_*` string sabitleri + elle yazılmış `addItem()`
çağrıları + `conv_map` dict'i yapıyordu — hepsi kaldırıldı.

## `ui/adapters/qt_conversion_runner.py`

`ConversionWorker(QThread)` + `QtConversionRunner`. `core.conversion_facade.convert_batch()`'i
arka planda çalıştırıp `progress`/`file_completed`/`batch_completed`
sinyalleriyle UI thread'ine rapor eder. Önceden `services/conversion_service.py`
içindeydi — backend/frontend ayrımını netleştirmek için buraya taşındı.

## Widget'lar (`ui/widgets/`)

- `DropZoneWidget` — sürükle-bırak + tıkla-seç; `accepted_extensions`
  listesini `set_accepted_extensions()` ile dinamik günceller.
- `FileListWidget` / `FileItemWidget` — dosya listesi, durum ikonları.
  **Bilinen sınırlama**: ikon her zaman `file_pptx.svg` — dosya türüne
  göre değişmiyor (bkz. [[rules]] altında not edilen kapsam-dışı kararlar).
- `OptionsPanelWidget` — dönüşüm türü/motor/çıktı klasörü/DPI/kalite
  formu. `converter_type_changed` sinyali artık bir `IConverter` nesnesi
  taşır (string değil).

## `ui/dialogs/summary_dialog.py`

Toplu dönüşüm bitince özet gösterir. `page_count > 1` olan sonuçlarda
"(N sayfa)" ekler — çok sayfalı PDF→JPG çıktısı için.

## `ui/styles/theme.py`

`PALETTE` dict + `MAIN_STYLE` (tek parça QSS string). Koyu tema, merkezi
renk sabitleri.

## İlgili Sayfalar

- [[mimari]] — bu katmanın genel akıştaki yeri
- [[converter-arayuzu]] — `IEngineSelectable` kontrolünün dayandığı sözleşme
