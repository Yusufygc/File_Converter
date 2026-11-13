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

Hata akışı: `convert()`/`convert_many()` ön kontroller dahil her adımı
`try` içinde yapar; yakalanan exception `core/errors.py`
`to_user_error()` ile kullanıcı mesajına çevrilir, teknik ayrıntı
günlüğe yazılır — `error_message` hiçbir zaman ham `str(exc)` değildir
(bkz. [[hata-yonetimi]]).

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

## `IPageRangeSelectable` (opsiyonel capability)

`core/interfaces/page_range_interface.py`. `IEngineSelectable`/
`IMergeConverter` ile aynı desen — kaynağın yalnızca belirli sayfalarını/
aralıklarını işleyebilen converter'lar için:

```python
parse_page_range(page_range: str, page_count: int) -> List[int]
```

UI, bir converter'ın sayfa aralığı girişi sunup sunmadığını
`isinstance(converter, IPageRangeSelectable)` ile anlar — options
panelinde "Aralık:" alanı olarak görünür (bkz. [[ui-katmani]]). Şu an
`PdfSplitConverter`, `PdfRotateConverter` ve `PdfToMarkdownConverter`
implemente eder (ortak ayrıştırıcı: `core/converters/page_range.py`
`parse_page_range()`). `PdfSplitConverter` için: `page_range` boşsa
(`ConversionOptions.page_range is None`) tüm sayfalar bölünür (eski
davranış), doluysa yalnızca `parse_page_range()`'in döndürdüğü sayfa
numaraları — kaynaktaki gerçek numarasıyla — ayrı dosyalara yazılır.
`parse_page_range()`, geçersiz format veya belge dışı sayfa numarasında
`ValueError` fırlatır; bu, `BaseConverter.convert()`'ın var olan
try/except'i tarafından yakalanıp `ConversionResult.error_message`'a
dönüşür — ayrı bir hata yolu eklenmedi.

## `IOptionsProvider` + `OptionSpec` (opsiyonel capability)

`core/interfaces/option_schema_interface.py`. Araca özgü kullanıcı
parametresi isteyen converter'lar (PDF Döndür, Sayfa Numarası, Filigran,
Şifrele, Şifre Kaldır) her parametre için `ConversionOptions`'a ayrı bir
alan + bridge property + QML kontrolü eklemek yerine **şema bildirir**:

```python
@property
def option_specs(self) -> List[OptionSpec]:
    return [OptionSpec(key="angle", label="Açı", kind="choice", default=90,
                       choices=[(90, "90° saat yönü"), (180, "180°"), (270, "90° saat tersi")])]
```

- `OptionSpec.kind`: `text` | `password` | `choice` | `int` (`OPTION_KINDS`).
  Yeni tür eklenirse `ui_qml/qml/components/DynamicOptionField.qml` da güncellenir.
- Değerler `ConversionOptions.extra: Dict[str, Any]` ile taşınır;
  converter `options.get_extra(key, default)` ile okur (boş string ve
  `None` "yok" sayılır).
- `required=True` alanlar `BaseConverter.convert()` içinde
  (`_missing_required_options()`) `_do_convert`'ten **önce** kontrol
  edilir — "Zorunlu alan boş: Parola" hata sonucu; her converter'da tekrar yazılmaz.
- UI tarafı: [[ui-katmani]] — `optionSpecs` + `setExtraOption()`.

Karar (2026-11-13, kullanıcı onaylı): tipli alan yerine genel şema —
yeni parametreli araç eklemek UI kodu gerektirmez (OCP). Ortak/çok
converter'ın kullandığı değerler (`dpi`, `quality`, `page_range`)
tipli alan olarak kalır; `extra` yalnızca tek araca özgü değerler için.

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

İkinci örnek: `core/converters/pymupdf_tool_base.py` `PyMuPdfToolConverter` —
`.pdf`→`.pdf` PyMuPDF araçlarının (Döndür, Sayfa No, Filigran, Şifrele,
Şifre Kaldır, Onar, Aranabilir PDF, Görsel Çıkar) motor tespiti, kurulum
ipucu, `is_parallel_safe=True` ve sonekli çıktı yolu (`output_suffix`
sınıf niteliği, örn. `_dondurulmus`) — kaynak ile hedef uzantı aynı
olduğunda sonek olmadan kaynağın üzerine yazılırdı.

## Value Object'ler

- `ConversionOptions(output_dir, dpi=150, quality=90, overwrite_existing=True, page_range=None, extra={})` —
  `extra` araca özgü `IOptionsProvider` değerleri (yukarıya bkz.);
  `dpi` LibreOffice render'ı ve PDF→JPG rasterizasyon çözünürlüğü için;
  `quality` yalnızca PDF→JPG'nin JPEG sıkıştırması için kullanılır;
  `page_range` yalnızca `IPageRangeSelectable` destekleyen converter'lar
  (şu an `PdfSplitConverter`) tarafından okunur, diğerleri yok sayar.
- `ConversionResult(source_path, output_path, success, error_message, page_count, elapsed_seconds)`
- `BatchConversionResult(results: List[ConversionResult])` — `total`/`success_count`/`failure_count`/`all_succeeded` property'leri

## İlgili Sayfalar

- [[mimari]] — bu arayüzün genel mimarideki yeri
- [[converter-ekleme]] — bu arayüzü kullanarak yeni converter yazma
- [[donusturucu-envanteri]] — mevcut implementasyonlar
