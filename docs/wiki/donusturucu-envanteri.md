# Dönüştürücü Envanteri

`core/converters/` altında [[converter-ekleme]] tarafından otomatik
keşfedilen 10 converter. Sıra, `ui/converter_catalog.py`'deki
`_PREFERRED_ORDER` ile aynı (varsayılan dropdown sırası). Üç converter
(`PdfCompressConverter`, `PdfSplitConverter`, `PdfMergeConverter`) aynı
`.pdf`→`.pdf` uzantı çiftini paylaşıyor — `ConverterRegistry`'nin iç
anahtarına sınıf adı eklenmesi bunların birbirini ezmesini önlüyor
(bkz. [[mimari]]).

| Converter | Kaynak → Hedef | Motor(lar) | Yetenekler | Özel davranış |
|---|---|---|---|---|
| `PptxToPdfConverter` | `.pptx` → `.pdf` | MS Office (win32com) → LibreOffice fallback | Motor seçimi (`IEngineSelectable`) | Tek gerçek kullanıcı-seçimli motor; `_MsOfficeStrategy`/`_LibreOfficeStrategy` |
| `DocxToPdfConverter` | `.docx` → `.pdf` | Yalnızca LibreOffice | — | `PdfToOdtConverter` ile aynı tek-motor deseni; `PdfToDocxConverter`'ın ters yönü |
| `PdfToDocxConverter` | `.pdf` → `.docx` | pdf2docx → LibreOffice fallback | — (otomatik seçer) | `pdf2docx` yalnızca `.docx` üretir, ODT'ye düşemez |
| `PdfToOdtConverter` | `.pdf` → `.odt` | Yalnızca LibreOffice | — | — |
| `PdfToJpgConverter` | `.pdf` → `.jpg` | PyMuPDF (`fitz`) | Paralel-güvenli | **Çok sayfalı PDF'te her sayfa ayrı dosya**: `ad_p1.jpg, ad_p2.jpg, ...`; tek sayfada `ad.jpg`. `options.dpi` render çözünürlüğü, `options.quality` JPEG kalitesi |
| `PdfToPngConverter` | `.pdf` → `.png` | PyMuPDF (`fitz`) | Paralel-güvenli | `PdfToJpgConverter` ile aynı rasterizasyon mantığı (çok sayfada `_p{n}` suffix); PNG kayıpsız olduğu için `options.quality` kullanılmaz |
| `PdfCompressConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli | Kaynak/hedef uzantı **aynı** — `get_output_path()` override edilir (`{stem}_sikistirilmis.pdf`), aksi halde varsayılan çıktı klasöründe kaynağın üzerine yazardı. Sayfaları görsele çevirmez, `doc.save(garbage=4, deflate=True, ...)` ile akış temizliği yapar |
| `PdfSplitConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Paralel-güvenli | Her sayfayı ayrı dosyaya böler: `ad_sayfa1.pdf, ad_sayfa2.pdf, ...` (tek sayfada bile — kaynakla çakışmayı önler). Sayfa aralığı seçimi (örn. "1-5") desteklenmiyor |
| `PdfMergeConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | Birleştirme (`IMergeConverter`), Paralel-güvenli | Birden fazla PDF'i tek dosyada birleştirir; tek dosya modunda "birleştirme" kendisinin `{stem}_birlesik.pdf` kopyasını üretir (dejenere ama tutarlı) |
| `JpgToPdfConverter` | `.jpg` → `.pdf` | PyMuPDF (`fitz`) | Birleştirme (`IMergeConverter`), Paralel-güvenli | `accepted_extensions` override: `.jpg` **ve** `.jpeg` kabul eder. Birleştirme modunda birden fazla görsel tek çok sayfalı PDF'e sarılır |

## Motor Tespit Sırası

- **PPTX→PDF**: Windows + `pywin32` kuruluysa MS Office; değilse
  `soffice`/`libreoffice` PATH'te veya bilinen kurulum yollarında aranır
  (bkz. [[libreoffice-motoru]]).
- **PDF→DOCX**: `pdf2docx` paketi varsa öncelikli (saf Python, dış süreç
  gerektirmez); yoksa LibreOffice headless.
- **DOCX→PDF, PDF→ODT**: tek motor, alternatif yok — LibreOffice şart.
- **PDF→JPG, PDF→PNG, PDF Sıkıştır, PDF Böl, PDF Birleştir, JPG→PDF**:
  tek motor, alternatif yok — PyMuPDF şart. Bu 6 converter aynı zamanda
  `is_parallel_safe=True` — dış süreç kullanmadıkları için toplu
  dönüşümde `convert_batch_parallel()` ile eşzamanlı çalıştırılabilirler
  (bkz. [[mimari]]).

## Kurulmamışsa Ne Olur

Her converter'ın `unavailable_hint` property'si (bkz. [[converter-arayuzu]])
kullanıcıya kurulum komutunu gösterir; `MainWindow._start_conversion()`
`is_available` `False` ise dönüşümü hiç başlatmadan bu metni bir
`QMessageBox`'ta gösterir.

## İlgili Sayfalar

- [[converter-arayuzu]] — bu tablodaki tüm converter'ların uyduğu sözleşme
- [[libreoffice-motoru]] — paylaşılan LibreOffice detayları
- [[converter-ekleme]] — buraya yeni bir satır eklemek için rehber
