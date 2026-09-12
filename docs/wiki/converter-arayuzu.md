# Converter Arayüzü

`core/interfaces/converter_interface.py` ve `core/converters/base.py`,
tüm dönüştürücülerin uyduğu sözleşmeyi tanımlar.

## `IConverter` (ABC)

Zorunlu üyeler:
- `source_extension -> str`, `target_extension -> str`, `display_name -> str`
- `is_available -> bool` — gerekli motor/araç sistemde var mı
- `active_engine_name -> str` — UI'da gösterilecek motor adı
- `validate(source_path) -> bool`
- `convert(source_path, options) -> ConversionResult`

Varsayılanlı (override edilebilir) üyeler:
- `accepted_extensions -> List[str]` — varsayılan `[source_extension]`;
  birden çok uzantı kabul eden converter'lar override eder (örn. `JpgToPdfConverter` → `[".jpg", ".jpeg"]`)
- `get_output_path(source_path, options) -> Path` — `output_dir / (stem + target_extension)`
- `is_parallel_safe -> bool` — varsayılan `False`. Yalnızca dış süreç/
  paylaşımlı durum kullanmayan (PyMuPDF tabanlı) converter'lar `True`
  döner — `convert_batch_parallel()`'ın (bkz. [[mimari]]) hangi
  converter'larda kullanılacağını belirler. LibreOffice/MS Office
  gibi harici süreçler paralel çalıştırıldığında profil/soket
  çakışması riski taşıdığı için varsayılan sıralı kalır.

`is_available`/`active_engine_name`'in **abstract** olması bilinçli bir
tasarım kararı: önceden UI bu üyelerin var olduğunu zımnen varsayıyordu
(`getattr` ile savunmacı okunan `accepted_extensions` hariç), şimdi arayüz
bunu garanti ediyor — yeni bir converter yazan biri bunları implemente
etmeden `IConverter`'ı somutlaştıramaz.

## `BaseConverter` (template method)

`core/converters/base.py`. `IConverter`'ı implemente eder, ortak akışı
(`validate` → `is_available` kontrolü → zamanlama → try/except →
`ConversionResult` üretimi) tek yerde toplar. Alt sınıflar yalnızca:

```python
def _do_convert(self, source_path, output_path, options) -> Optional[ConvertOutcome]:
    ...  # asıl dönüşüm mantığı, hata durumunda Exception fırlatır

@property
def unavailable_hint(self) -> str:
    ...  # is_available False iken kullanıcıya gösterilecek kurulum ipucu
```

`ConvertOutcome(output_path=None, page_count=0)` — `_do_convert()`'in
döndürdüğü opsiyonel sonuç. `None` dönerse şablon metodun hesapladığı
`output_path` ve `page_count=0` kullanılır. Çok sayfalı çıktı üreten
`PdfToJpgConverter` gibi durumlarda gerçek ilk-sayfa yolu ve toplam sayfa
sayısı burada override edilir.

`BaseConverter.validate()` da somut: `accepted_extensions`'a bakarak
dosya uzantısını kontrol eder — her converter'da ayrı ayrı yazılmaz.

Şu an tüm converter'lar (bkz. [[donusturucu-envanteri]]) `BaseConverter`
veya onu extend eden `MergeCapableConverter`'dan türer.

## `IEngineSelectable` (opsiyonel capability)

`core/interfaces/engine_interface.py`. `typing.Protocol` (yapısal/duck-typing
sözleşme, `runtime_checkable`). Birden fazla motor arasında **kullanıcının
elle seçim yapabildiği** converter'lar için:

```python
active_engine -> Any
available_engines() -> List[Any]
set_preferred_engine(engine: Any) -> bool
```

UI, bir converter'ın motor seçimi sunup sunmadığını
`isinstance(converter, IEngineSelectable)` ile anlar — belirli bir
dönüşüm türünü (`CONV_PPTX_PDF` gibi) hardcode etmez. Şu an yalnızca
`PptxToPdfConverter` bunu implemente eder (gerçek kullanıcı seçimi sunan
tek converter budur; `PdfToDocxConverter` motoru otomatik seçer, salt
okunur gösterir).

## `IMergeConverter` (opsiyonel capability)

`core/interfaces/merge_interface.py`. `IEngineSelectable` ile aynı desen —
birden fazla dosyayı **TEK bir çıktıda** birleştirebilen converter'lar için:

```python
convert_many(source_paths: List[Path], options: ConversionOptions) -> ConversionResult
```

Bu, mevcut `IConverter.convert(source_path, options)`'ın 1:1
varsayımını **hiç değiştirmeden** N:1 (çoklu girdi → tek çıktı)
senaryosunu ekler. UI, `isinstance(converter, IMergeConverter)` ile bir
converter'ın birleştirme modu sunup sunmadığını anlar — options
panelinde "Tüm dosyaları TEK çıktıda birleştir" onay kutusu olarak
görünür (bkz. [[ui-katmani]]).

Somutlaştığı yer: `core/converters/base.py`'daki `MergeCapableConverter(BaseConverter)`.
**Bilinçli olarak `BaseConverter`'ın kendisine değil, ayrı bir alt
sınıfa eklenmiştir**: `convert_many`'i doğrudan `BaseConverter`'a koymak
TÜM converter'lara bu metodu miras bırakırdı (çağrılmasa bile *var
olurdu*) — bu da `isinstance(x, IMergeConverter)` kontrolünü her
converter için `True` yapıp capability deseni bozardı. `MergeCapableConverter`,
`BaseConverter.convert()` ile birebir aynı şablon-metot deseniyle
`convert_many()`'i sağlar; alt sınıflar yalnızca `_do_convert_many(source_paths, output_path, options) -> Optional[ConvertOutcome]`
implemente eder. Şu an `JpgToPdfConverter` ve `PdfMergeConverter` bunu
extend eder (bkz. [[donusturucu-envanteri]]).

## Factory-Tarzı Taban Sınıflar: "Abstract Kalarak Keşiften Kaçınma"

`core/converters/office_conversions.py`'deki `SimpleLibreOfficeConverter(BaseConverter)`
— XLSX↔PDF/CSV/ODS, DOCX↔ODT gibi 7 converter'ın tamamı `LibreOfficeEngine.convert_to()`'yu
çağırmak dışında hiçbir mantık farkı taşımıyor, yalnızca kaynak/hedef
uzantı ve görünen ad değişiyor. Bunun için genel bir desen:

- Ortak taban (`is_available`/`active_engine_name`/`unavailable_hint`/`_do_convert`)
  tek yerde çözülür, **ama** `source_extension`/`target_extension`/
  `display_name`'i **kasıtlı olarak implemente etmez** — bu üçü
  `IConverter`'dan abstract kalır.
- Sonuç: taban sınıf `inspect.isabstract()` için hâlâ `True` döner,
  `core/converters/discovery.py` bunu (parametre almadan `cls()` ile
  örneklemeye çalışıp `TypeError` ile çökmeden) otomatik atlar —
  yalnızca gerçek alt sınıflar (her biri 3 property override eden
  ~8 satır) somutlaşır ve kaydolur.

Bu, `IEngineSelectable`/`IMergeConverter` gibi bir capability protokolü
değil — sıradan bir DRY tekniği, ama `discovery.py`'nin "her concrete
`IConverter` alt sınıfını otomatik kaydet" varsayımıyla dikkatli
etkileşmesi gerektiği için burada belgeleniyor: **yeni bir parametrize
edilebilir taban sınıf yazarken, `source_extension`/`target_extension`/
`display_name`'den en az birini kasıtlı olarak abstract bırakmazsan
discovery bunu somut bir converter sanıp `cls()` ile örneklemeye
çalışır ve çöker.**

## Value Object'ler

- `ConversionOptions(output_dir, dpi=150, quality=90, overwrite_existing=True)` —
  `dpi` LibreOffice render'ı ve PDF→JPG rasterizasyon çözünürlüğü için;
  `quality` yalnızca PDF→JPG'nin JPEG sıkıştırması için kullanılır.
- `ConversionResult(source_path, output_path, success, error_message, page_count, elapsed_seconds)`
- `BatchConversionResult(results: List[ConversionResult])` — `total`/`success_count`/`failure_count`/`all_succeeded` property'leri

## İlgili Sayfalar

- [[mimari]] — bu arayüzün genel mimarideki yeri
- [[converter-ekleme]] — bu arayüzü kullanarak yeni converter yazma
- [[donusturucu-envanteri]] — mevcut implementasyonlar
