# Dönüştürücü Envanteri

`core/converters/` altında [[converter-ekleme]] tarafından otomatik
keşfedilen 19 converter. Sıra, `ui/converter_catalog.py`'deki
`_PREFERRED_ORDER` ile aynı (varsayılan dropdown sırası). Üç converter
(`PdfCompressConverter`, `PdfSplitConverter`, `PdfMergeConverter`) aynı
`.pdf`→`.pdf` uzantı çiftini paylaşıyor — `ConverterRegistry`'nin iç
anahtarına sınıf adı eklenmesi bunların birbirini ezmesini önlüyor
(bkz. [[mimari]]).

| Converter | Kaynak → Hedef | Motor(lar) | Yetenekler | Özel davranış |
|---|---|---|---|---|
| `PptxToPdfConverter` | `.pptx` → `.pdf` | MS Office (win32com) → LibreOffice fallback | Motor seçimi (`IEngineSelectable`) | Tek gerçek kullanıcı-seçimli motor; `_MsOfficeStrategy`/`_LibreOfficeStrategy` |
| `DocxToPdfConverter` | `.docx` → `.pdf` | Yalnızca LibreOffice | — | `PdfToOdtConverter` ile aynı tek-motor deseni; `PdfToDocxConverter`'ın ters yönü |
| `DocxToTxtConverter` | `.docx` → `.txt` | `python-docx` | Paralel-güvenli | LibreOffice gerekmez — yalnızca `document.paragraphs` metnini çıkarır (tablo/başlık kapsanmaz) |
| `DocxToOdtConverter` | `.docx` → `.odt` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı (bkz. aşağıdaki not) |
| `OdtToDocxConverter` | `.odt` → `.docx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `PdfToDocxConverter` | `.pdf` → `.docx` | pdf2docx → OCR (Tesseract) → Görsel Gömme → LibreOffice fallback | Akıllı Belge Analizi (`PdfInspector`) | Dijital PDF'lerde `pdf2docx` (1-2s); taranmış PDF'lerde OCR (Tesseract); OCR yoksa temiz sayfa görseli gömme |
| `PdfToOdtConverter` | `.pdf` → `.odt` | Yalnızca LibreOffice | — | — |
| `PdfToJpgConverter` | `.pdf` → `.jpg` | PyMuPDF (`fitz`) | Paralel-güvenli | **Çok sayfalı PDF'te her sayfa ayrı dosya**: `ad_p1.jpg, ad_p2.jpg, ...`; tek sayfada `ad.jpg`. `options.dpi` render çözünürlüğü, `options.quality` JPEG kalitesi |
| `PdfToPngConverter` | `.pdf` → `.png` | PyMuPDF (`fitz`) | Paralel-güvenli | `PdfToJpgConverter` ile aynı rasterizasyon mantığı (çok sayfada `_p{n}` suffix); PNG kayıpsız olduğu için `options.quality` kullanılmaz |
| `PdfToTxtConverter` | `.pdf` → `.txt` | PyMuPDF (`fitz`) + OCR (Tesseract) | Paralel-güvenli, OCR Destekli | Dijital PDF'lerde doğrudan metin çıkarımı; taranmış PDF'lerde OCR motoru varsa otomatik OCR ile metin çıkarır |
| `PdfCompressConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli | Kaynak/hedef uzantı **aynı** — `get_output_path()` override edilir (`{stem}_sikistirilmis.pdf`), aksi halde varsayılan çıktı klasöründe kaynağın üzerine yazardı. Sayfaları görsele çevirmez, `doc.save(garbage=4, deflate=True, ...)` ile akış temizliği yapar |
| `PdfSplitConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli, `IPageRangeSelectable` | Her sayfayı ayrı dosyaya böler: `ad_sayfa1.pdf, ad_sayfa2.pdf, ...` (tek sayfada bile — kaynakla çakışmayı önler). `options.page_range` ile "1-3,5,7-9" gibi bir aralık verilirse yalnızca o sayfalar, kaynaktaki gerçek sayfa numarasıyla adlandırılarak üretilir (bkz. [[converter-arayuzu]]) |
| `PdfMergeConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Birleştirme (`IMergeConverter`), Paralel-güvenli | Birden fazla PDF'i tek dosyada birleştirir; tek dosya modunda "birleştirme" kendisinin `{stem}_birlesik.pdf` kopyasını üretir (dejenere ama tutarlı) |
| `XlsxToPdfConverter` | `.xlsx` → `.pdf` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `XlsxToCsvConverter` | `.xlsx` → `.csv` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `CsvToXlsxConverter` | `.csv` → `.xlsx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı. CSV import filtresi bazı delimiter/encoding kombinasyonlarında yanlış algılayabilir — ilk sürüm auto-detect ile gidiyor, sorun çıkarsa `convert_extra_args` ile `--infilter` eklenebilir |
| `XlsxToOdsConverter` | `.xlsx` → `.ods` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
| `OdsToXlsxConverter` | `.ods` → `.xlsx` | Yalnızca LibreOffice | — | `SimpleLibreOfficeConverter` alt sınıfı |
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

## Kurulmamışsa Ne Olur

Her converter'ın `unavailable_hint` property'si (bkz. [[converter-arayuzu]])
kullanıcıya kurulum komutunu gösterir; `MainWindow._start_conversion()`
`is_available` `False` ise dönüşümü hiç başlatmadan bu metni bir
`QMessageBox`'ta gösterir.

## İlgili Sayfalar

- [[converter-arayuzu]] — bu tablodaki tüm converter'ların uyduğu sözleşme
- [[libreoffice-motoru]] — paylaşılan LibreOffice detayları
- [[converter-ekleme]] — buraya yeni bir satır eklemek için rehber
