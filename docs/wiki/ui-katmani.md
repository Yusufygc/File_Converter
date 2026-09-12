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
- Dönüşüm başlatma/iptal (`_start_conversion` → `QtConversionRunner`).
  Dönüştür butonu tek bir buton — `_on_convert_button_clicked()`
  `self._converting` durumuna göre başlatma/iptal arasında dallanır
  (ayrı bir iptal butonu yerine); `_set_converting_state()` metni ve
  `objectName`'i (`primaryBtn` ↔ `dangerBtn`) değiştirir.
  `QtConversionRunner.cancel()` çağrılır, `self._cancel_requested`
  bayrağı `_on_batch_done()`'da "İptal edildi" durum mesajını üretmek
  için kullanılır (worker'ın private durumuna reach-through yapılmaz).
- Ayarları kalıcı saklama (`self._settings: AppSettings`) —
  `_restore_settings()` (`__init__` sonrası, combo doldurulduktan sonra)
  ve `closeEvent()` (kapanışta kaydeder).

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

## `ui/app_settings.py`

`AppSettings` — `QSettings`'i sarmalar (pencere geometrisi, aktif
converter kimliği `(source_ext, target_ext)`, çıktı klasörü, DPI/kalite/
üzerine-yaz). Tamamen UI-katmanına özel; `core/`'a sızmaz. `main.py`'de
zaten ayarlanan org/app adını kullanır. `OptionsPanelWidget`'ın
`select_converter()`/`set_output_dir()`/`set_quality_options()` genel
API'leriyle konuşur — `MainWindow` widget'ın private state'ine
dokunmaz.

## `ui/icon_map.py`

Dosya uzantısından ikon yoluna eşleme (`icon_path_for()`). Önceden
`FileItemWidget` her zaman `file_pptx.svg` gösteriyordu — artık kaynak
uzantısına göre (`.pptx`, `.pdf`, `.jpg`/`.jpeg`) doğru ikon seçiliyor,
bilinmeyen bir uzantı `file_generic.svg`'ye düşüyor (crash etmez, yeni
converter eklerken özel ikon eklemek zorunlu değil).

## Widget'lar (`ui/widgets/`)

- `DropZoneWidget` — sürükle-bırak + tıkla-seç; `accepted_extensions`
  listesini `set_accepted_extensions()` ile dinamik günceller.
- `FileListWidget` / `FileItemWidget` — dosya listesi, durum ikonları
  (`ui/icon_map.py` ile dosya türüne göre).
- `OptionsPanelWidget` — dönüşüm türü/motor/çıktı klasörü/DPI/kalite
  formu. `converter_type_changed` sinyali artık bir `IConverter` nesnesi
  taşır (string değil). `select_converter()`/`set_output_dir()`/
  `set_quality_options()` — `AppSettings` restore akışı için genel API.

## `ui/dialogs/summary_dialog.py`

Toplu dönüşüm bitince özet gösterir. `page_count > 1` olan sonuçlarda
"(N sayfa)" ekler — çok sayfalı PDF→JPG çıktısı için.

## `ui/styles/theme.py`

`PALETTE` dict + `MAIN_STYLE` (tek parça QSS string). Koyu tema, merkezi
renk sabitleri.

## İlgili Sayfalar

- [[mimari]] — bu katmanın genel akıştaki yeri
- [[converter-arayuzu]] — `IEngineSelectable` kontrolünün dayandığı sözleşme
