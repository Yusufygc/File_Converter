# Dönüştürücü Envanteri

`core/converters/` altında [[converter-ekleme]] tarafından otomatik
keşfedilen 32 converter. Bu tablo teknik envanterdir; kenar çubuğundaki
grupları ve sırası `ui_qml/bridge/converter_catalog.py`'den gelir
(bkz. [[ui-katmani]]). On converter
(Sıkıştır, Böl, Birleştir, Döndür, Sayfa No, Filigran, Şifrele, Şifre
Kaldır, Onar, Aranabilir PDF) aynı `.pdf`→`.pdf` uzantı çiftini paylaşıyor — `ConverterRegistry`'nin iç
anahtarına sınıf adı eklenmesi bunların birbirini ezmesini önlüyor
(bkz. [[mimari]]).

| Converter | Kaynak → Hedef | Motor(lar) | Yetenekler | Özel davranış |
|---|---|---|---|---|
| `PptxToPdfConverter` | `.pptx` → `.pdf` | MS Office (win32com) → LibreOffice fallback | Motor seçimi (`IEngineSelectable`) | Tek gerçek kullanıcı-seçimli motor; `_MsOfficeStrategy`/`_LibreOfficeStrategy` |
| `DocxToPdfConverter` | `.docx` → `.pdf` | Yalnızca LibreOffice | — | Tek-motor deseni; `PdfToDocxConverter`'ın ters yönü |
| `DocxToTxtConverter` | `.docx` → `.txt` | `python-docx` | Paralel-güvenli | LibreOffice gerekmez — yalnızca `document.paragraphs` metnini çıkarır (tablo/başlık kapsanmaz) |
| `DocxToOdtConverter` | `.docx` → `.odt` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı (bkz. aşağıdaki not) |
| `OdtToDocxConverter` | `.odt` → `.docx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `PdfToDocxConverter` | `.pdf` → `.docx` | pdf2docx → OCR (Tesseract) → Görsel Gömme → LibreOffice fallback | Akıllı Belge Analizi (`PdfInspector`) | Dijital PDF'lerde `pdf2docx` (1-2s); taranmış PDF'lerde OCR (Tesseract); OCR yoksa temiz sayfa görseli gömme |
| `PdfToOdtConverter` | `.pdf` → `.odt` | `PdfToDocxConverter` hattı + LibreOffice (DOCX→ODT) | — | PDF önce geçici DOCX'e (pdf2docx/OCR/görsel gömme) çevrilir, sonra LibreOffice ODT yapar. LibreOffice'in PDF içe aktarması çizim yoğun PDF'lerde 15 dk+ sürüp düzenlenemez metin kutuları ürettiği için kullanılmıyor — bkz. [[libreoffice-motoru]] |
| `PdfToJpgConverter` | `.pdf` → `.jpg` | PyMuPDF (`fitz`) | Paralel-güvenli | **Çok sayfalı PDF'te her sayfa ayrı dosya**: `ad_p1.jpg, ad_p2.jpg, ...`; tek sayfada `ad.jpg`. `options.dpi` render çözünürlüğü, `options.quality` JPEG kalitesi |
| `PdfToPngConverter` | `.pdf` → `.png` | PyMuPDF (`fitz`) | Paralel-güvenli | `PdfToJpgConverter` ile aynı rasterizasyon mantığı (çok sayfada `_p{n}` suffix); PNG kayıpsız olduğu için `options.quality` kullanılmaz |
| `PdfToTxtConverter` | `.pdf` → `.txt` | PyMuPDF (`fitz`) + OCR (Tesseract) | Paralel-güvenli, OCR Destekli | Dijital PDF'lerde doğrudan metin çıkarımı; taranmış PDF'lerde OCR motoru varsa otomatik OCR ile metin çıkarır |
| `PdfCompressConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli | Kaynak/hedef uzantı **aynı** — `get_output_path()` override edilir (`{stem}_sikistirilmis.pdf`), aksi halde varsayılan çıktı klasöründe kaynağın üzerine yazardı. Sayfaları görsele çevirmez, `doc.save(garbage=4, deflate=True, ...)` ile akış temizliği yapar |
| `PdfSplitConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli, `IPageRangeSelectable` | `options.page_range` boşsa her sayfayı ayrı dosyaya böler: `ad_sayfa1.pdf, ad_sayfa2.pdf, ...` (tek sayfada bile — kaynakla çakışmayı önler). Aralık verilirse ("1-3,5,7-9") o sayfalar **TEK bir PDF'te** birleştirilip `ad_sayfa1-2-3-5-7-8-9.pdf` gibi adlandırılır — kullanıcı bir aralık verdiğinde onu tek parça bekliyor, ayrıca her sayfayı bölmüyor (bkz. [[converter-arayuzu]]) |
| `PdfMergeConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Birleştirme (`IMergeConverter`), Paralel-güvenli | Birden fazla PDF'i tek dosyada birleştirir; tek dosya modunda "birleştirme" kendisinin `{stem}_birlesik.pdf` kopyasını üretir (dejenere ama tutarlı) |
| `XlsxToPdfConverter` | `.xlsx` → `.pdf` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `XlsxToCsvConverter` | `.xlsx` → `.csv` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `CsvToXlsxConverter` | `.csv` → `.xlsx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı. CSV import filtresi bazı delimiter/encoding kombinasyonlarında yanlış algılayabilir — ilk sürüm auto-detect ile gidiyor, sorun çıkarsa `convert_extra_args` ile `--infilter` eklenebilir |
| `XlsxToOdsConverter` | `.xlsx` → `.ods` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `OdsToXlsxConverter` | `.ods` → `.xlsx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `PptxToOdpConverter` | `.pptx` → `.odp` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı; gerçek LO ile PPTX→ODP→PPTX gidiş-dönüş doğrulandı, `--infilter` gerekmedi |
| `OdpToPptxConverter` | `.odp` → `.pptx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `OdpToPdfConverter` | `.odp` → `.pdf` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `PdfRotateConverter` | `.pdf` → `.pdf` | PyMuPDF | Paralel-güvenli, `IPageRangeSelectable`, `IOptionsProvider` (`angle`) | Yalnızca `/Rotate` değiştirir (kayıpsız), mevcut rotasyona eklenir; aralık boşsa tüm sayfalar. Çıktı `_dondurulmus.pdf` |
| `PdfPageNumbersConverter` | `.pdf` → `.pdf` | PyMuPDF | Paralel-güvenli, `IOptionsProvider` (`position`, `format`, `start`) | Konum görünen (döndürülmüş) sayfaya göre hesaplanıp `derotation_matrix` ile çevrilir — `/Rotate`'li sayfalarda da doğru köşe. Çıktı `_numarali.pdf` |
| `PdfWatermarkConverter` | `.pdf` → `.pdf` | PyMuPDF (`TextWriter`) | Paralel-güvenli, `IOptionsProvider` (`text`*, `opacity`, `font_size`) | Ortada 45° yarı saydam metin. `fitz.Font("helv")` nesnesi Türkçe karakter içerir (base-14 `fontname="helv"` içermez). Çıktı `_filigranli.pdf` |
| `PdfProtectConverter` | `.pdf` → `.pdf` | PyMuPDF | Paralel-güvenli, `IOptionsProvider` (`password`*) | AES-256, user=owner parola. Zaten şifreliyse hata. Çıktı `_sifreli.pdf` |
| `PdfUnlockConverter` | `.pdf` → `.pdf` | PyMuPDF | Paralel-güvenli, `IOptionsProvider` (`password`) | Açılış parolası varsa doğrular ("Parola yanlış"); yalnızca izin kilitli PDF'te parolasız çalışır; şifresizse hata. Çıktı `_sifresiz.pdf` |
| `PdfRepairConverter` | `.pdf` → `.pdf` | PyMuPDF | Paralel-güvenli | MuPDF açılışta bozuk xref'i yeniden kurar; `garbage=4, clean=True` ile kalıcı yazılır. Çıktı `_onarilmis.pdf` |
| `PdfExtractImagesConverter` | `.pdf` → (`.png` nominal) | PyMuPDF | Paralel-güvenli | Gömülü görselleri yeniden kodlamadan kendi formatında yazar: `ad_gorsel1.jpg, ...`; aynı xref bir kez. Görsel yoksa hata. Kategori `images` |
| `PdfOcrConverter` | `.pdf` → `.pdf` | Tesseract (`OcrEngine.ocr_page_to_pdf`) + PyMuPDF | **Sıralı** (dış süreç) | Aranabilir PDF: metni <20 karakter olan sayfalar 300 DPI OCR'lanıp Tesseract PDF'i orijinal boyuta `show_pdf_page` ile yerleşir; dijital sayfalar olduğu gibi kopyalanır. Hiç OCR gerekmezse hata. Çıktı `_aranabilir.pdf` |
| `PdfToMarkdownConverter` | `.pdf` → `.md` | `pymupdf4llm` | Paralel-güvenli, `IPageRangeSelectable` | Başlık/liste/tablo korunur; metinsiz (taranmış) PDF'te hata, önce Aranabilir PDF önerilir |
| `PdfToXlsxConverter` | `.pdf` → `.xlsx` | PyMuPDF `find_tables()` + `openpyxl` | Paralel-güvenli | Her tablo ayrı sayfa `S{sayfa}_T{n}`; çizgisiz serbest düzen tablolar bulunamayabilir. Tablo yoksa hata |
| `JpgToPdfConverter` | `.jpg` → `.pdf` | PyMuPDF (`fitz`) | Birleştirme (`IMergeConverter`), Paralel-güvenli | `accepted_extensions` override: `.jpg` **ve** `.jpeg` kabul eder. Birleştirme modunda birden fazla görsel tek çok sayfalı PDF'e sarılır |

**`SimpleLibreOfficeConverter`** (`core/converters/office_conversions.py`):
yukarıdaki 7 converter, aralarında `LibreOfficeEngine.convert_to()`'yu
çağırmak dışında hiçbir mantık farkı olmadığı için ortak bir tabandan
türer — her biri yalnızca `source_extension`/`target_extension`/
`display_name` override eden ~8 satır. Taban sınıf kasıtlı olarak bu
üçünü implemente etmez (abstract kalır), böylece `discovery.py`
tarafından yanlışlıkla somut bir converter sanılıp parametre almadan
örneklenmeye çalışılmaz — bkz. [[converter-arayuzu]].

## Motor Tespit Sırası

- **PPTX→PDF**: Windows + `pywin32` kuruluysa MS Office; değilse
  `soffice`/`libreoffice` PATH'te veya bilinen kurulum yollarında aranır
  (bkz. [[libreoffice-motoru]]).
- **PDF→DOCX**: `pdf2docx` paketi varsa öncelikli (saf Python, dış süreç
  gerektirmez); yoksa LibreOffice headless.
- **DOCX→PDF, PDF→ODT, DOCX↔ODT, XLSX→PDF, XLSX↔CSV, XLSX↔ODS**: tek
  motor, alternatif yok — LibreOffice şart.
- **PDF→JPG, PDF→PNG, PDF→TXT, PDF Sıkıştır, PDF Böl, PDF Birleştir,
  JPG→PDF**: tek motor, alternatif yok — PyMuPDF şart. Bu 7 converter
  aynı zamanda `is_parallel_safe=True` — dış süreç kullanmadıkları için
  toplu dönüşümde `convert_batch_parallel()` ile eşzamanlı
  çalıştırılabilirler (bkz. [[mimari]]).
- **DOCX→TXT**: `python-docx`, dış süreç yok, `is_parallel_safe=True`.
- **PPTX↔ODP, ODP→PDF**: tek motor LibreOffice.
- **PDF Döndür/Sayfa No/Filigran/Şifrele/Şifre Kaldır/Onar/Görsel Çıkar**:
  PyMuPDF, `PyMuPdfToolConverter` tabanı, `is_parallel_safe=True`
  (bkz. [[converter-arayuzu]]).
- **Aranabilir PDF**: Tesseract şart (yoksa converter kullanılamaz), sıralı.
- **PDF→Markdown**: `pymupdf4llm`; **PDF→Excel**: PyMuPDF + `openpyxl`.

`*` = `OptionSpec(required=True)` — boşsa dönüşüm başlamadan hata.

## Yöntem Etiketleri

Tablodaki "Motor(lar)" sütunu teknik içeriktir; UI'da (`active_engine_name`)
kütüphane adları değil `core/user_texts.py` etiketleri görünür:
pakete gömülü kütüphaneler "Yerleşik", OCR "Metin tanıma",
harici programlar "LibreOffice"/"Microsoft Office", kullanılamıyorsa
"Kullanılamıyor" — bkz. [[hata-yonetimi]].

## Kurulmamışsa Ne Olur

Her converter'ın `unavailable_hint` property'si (bkz. [[converter-arayuzu]])
kullanıcıya teknik terimsiz bir kurulum ipucu gösterir (harici program
için indirme bağlantısı, gömülü bileşen için "yeniden kurun" — bkz.
[[hata-yonetimi]]); `AppBridge.startConversion()` `is_available` `False`
ise dönüşümü hiç başlatmadan bu metni "Gerekli Program Eksik"
bildirimiyle (`notificationRequested`) gösterir.

## İlgili Sayfalar

- [[converter-arayuzu]] — bu tablodaki tüm converter'ların uyduğu sözleşme
- [[libreoffice-motoru]] — paylaşılan LibreOffice detayları
- [[converter-ekleme]] — buraya yeni bir satır eklemek için rehber
