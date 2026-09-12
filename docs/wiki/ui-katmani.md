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
- Tema butonu (`_theme_btn`, header'da `🌙`/`☀️`) — `_on_theme_toggle_clicked()`
  tercihi `AppSettings.save_theme_mode()` ile kaydeder, "yeniden
  başlatınca uygulanır" mesajı gösterir (canlı geçiş yok, bkz. `ui/styles/theme.py`).
- Birleştirme modu — `isinstance(active_converter, IMergeConverter)` ise
  options panelindeki onay kutusu görünür olur. İşaretliyse
  `_start_conversion()`, `start_batch_conversion()` yerine
  `QtConversionRunner.start_merge_conversion()`'ı çağırır
  (`self._last_conversion_was_merge` bayrağı, `_on_batch_done()`'ın
  doğru durum mesajını seçmesi için — iptal mesajıyla karışmasın diye).

## `ui/converter_catalog.py`

`registry.all_converters()`'dan dropdown listesini **jenerik** üretir.
`_PREFERRED_ORDER` yalnızca görünüm sırası (bkz. [[converter-ekleme]]).
Önceden bu işi `CONV_*` string sabitleri + elle yazılmış `addItem()`
çağrıları + `conv_map` dict'i yapıyordu — hepsi kaldırıldı.

## `ui/adapters/qt_conversion_runner.py`

- `ConversionWorker(QThread)` + `QtConversionRunner.start_batch_conversion()` —
  `converter.is_parallel_safe`'e göre `core.conversion_facade.convert_batch()`
  (sıralı) veya `convert_batch_parallel()` (`ThreadPoolExecutor`) çağırır,
  `progress`/`file_completed`/`batch_completed` sinyalleriyle UI thread'ine
  rapor eder. Önceden `services/conversion_service.py` içindeydi —
  backend/frontend ayrımını netleştirmek için buraya taşındı.
- `MergeWorker(QThread)` + `QtConversionRunner.start_merge_conversion()` —
  `core.conversion_facade.merge_files()`'ı çağırır, tek `ConversionResult`'ı
  `BatchConversionResult(results=[result])`'a sararak `merge_completed`
  sinyaliyle yayınlar (`SummaryDialog` değişmeden çalışır).
  `cancel()` no-op'tur — birleştirme tek parça bir işlemdir, yarıda
  kesilemez; `QtConversionRunner.cancel()`'ın worker türünden bağımsız
  çağırdığı `.cancel()`'ın hata fırlatmamasını sağlar.

## `ui/app_settings.py`

`AppSettings` — `QSettings`'i sarmalar (pencere geometrisi, aktif
converter kimliği `(source_ext, target_ext)`, çıktı klasörü, DPI/kalite/
üzerine-yaz, tema tercihi). Tamamen UI-katmanına özel; `core/`'a sızmaz.
`ORG_NAME`/`APP_NAME`/`THEME_MODE_KEY` modül sabitlerini de burada
tanımlar — `main.py` (QApplication kurulumu) ve `ui/styles/theme.py`
(tema tercihini `QApplication`'dan bağımsız okumak için) buradan alır,
iki yerde ayrı hardcoded string yok. `OptionsPanelWidget`'ın
`select_converter()`/`set_output_dir()`/`set_quality_options()` genel
API'leriyle konuşur — `MainWindow` widget'ın private state'ine
dokunmaz.

## `ui/icon_map.py`

Dosya uzantısından ikon yoluna eşleme (`icon_path_for()`). Önceden
`FileItemWidget` her zaman `file_pptx.svg` gösteriyordu — artık kaynak
uzantısına göre (`.pptx`, `.pdf`, `.jpg`/`.jpeg`) doğru ikon seçiliyor,
bilinmeyen bir uzantı `file_generic.svg`'ye düşüyor (crash etmez, yeni
converter eklerken özel ikon eklemek zorunlu değil).

## `ui/file_discovery.py`

`collect_files(directory, accepted_extensions) -> List[Path]` — saf
`pathlib`/`rglob` mantığı, **Qt'den bağımsız** (`ui/icon_map.py`'nin de
izlediği "UI-katmanında yaşayan ama Qt'siz saf mantık" deseni — bu
yüzden `tests/`'teki hızlı, Qt'siz test paketine katılabiliyor).
`DropZoneWidget.dropEvent()` bir klasör sürüklendiğinde bunu çağırır
(alt klasörler dahil tarar); `dragEnterEvent()` de bir klasörü kabul
edecek şekilde güncellendi.

## Widget'lar (`ui/widgets/`)

- `DropZoneWidget` — sürükle-bırak + tıkla-seç; `accepted_extensions`
  listesini `set_accepted_extensions()` ile dinamik günceller. Bir
  klasör sürüklendiğinde `ui/file_discovery.collect_files()` ile
  içindeki (alt klasörler dahil) uygun dosyaları toplar.
- `FileListWidget` / `FileItemWidget` — dosya listesi, durum ikonları
  (`ui/icon_map.py` ile dosya türüne göre).
- `OptionsPanelWidget` — dönüşüm türü/motor/çıktı klasörü/DPI/kalite
  formu. `converter_type_changed` sinyali artık bir `IConverter` nesnesi
  taşır (string değil). `select_converter()`/`set_output_dir()`/
  `set_quality_options()` — `AppSettings` restore akışı için genel API.
  `set_merge_mode_available()`/`is_merge_mode()` — birleştirme onay
  kutusunu yönetir (bkz. [[converter-arayuzu]]'ndeki `IMergeConverter`).

## `ui/dialogs/summary_dialog.py`

Toplu dönüşüm bitince özet gösterir. `page_count > 1` olan sonuçlarda
"(N sayfa)" ekler — çok sayfalı PDF→JPG çıktısı için.

## `ui/styles/theme.py`

`DARK_PALETTE`/`LIGHT_PALETTE` dict'leri + `build_style(palette) -> str`
(parametrize edilmiş QSS üretimi). Modül **import edilir edilmez**
(`QSettings(ORG_NAME, APP_NAME)` ile, `QApplication` gerektirmeden)
kayıtlı tema tercihine göre `PALETTE`/`MAIN_STYLE` seçilir. Diğer tüm
dosyalardaki `from ui.styles.theme import PALETTE` importları bu
tek-seferlik çözümlemeyi olduğu gibi alır — Python'un modül önbelleği
sayesinde tutarlılık garanti edilir. **Canlı (restart'sız) tema geçişi
desteklenmez**: birçok widget dosyası `PALETTE[...]`'i inşa anında
inline `setStyleSheet()` içine gömüyor; bunu QSS'e taşımak ayrı bir
refactor gerektirir, bilinçli olarak kapsam dışı bırakıldı.

## İlgili Sayfalar

- [[mimari]] — bu katmanın genel akıştaki yeri
- [[converter-arayuzu]] — `IEngineSelectable` kontrolünün dayandığı sözleşme
