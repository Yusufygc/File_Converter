# Dönüştürücü Envanteri

`core/converters/` altında [[converter-ekleme]] tarafından otomatik
keşfedilen 8 converter. Sıra, `ui/converter_catalog.py`'deki
`_PREFERRED_ORDER` ile aynı (varsayılan dropdown sırası).

| Converter | Kaynak → Hedef | Motor(lar) | `IEngineSelectable` | Özel davranış |
|---|---|---|---|---|
| `PptxToPdfConverter` | `.pptx` → `.pdf` | MS Office (win32com) → LibreOffice fallback | ✅ Evet | Tek gerçek kullanıcı-seçimli motor; `_MsOfficeStrategy`/`_LibreOfficeStrategy` |
| `DocxToPdfConverter` | `.docx` → `.pdf` | Yalnızca LibreOffice | ❌ Hayır | `PdfToOdtConverter` ile aynı tek-motor deseni; `PdfToDocxConverter`'ın ters yönü |
| `PdfToDocxConverter` | `.pdf` → `.docx` | pdf2docx → LibreOffice fallback | ❌ Hayır (otomatik seçer) | `pdf2docx` yalnızca `.docx` üretir, ODT'ye düşemez |
| `PdfToOdtConverter` | `.pdf` → `.odt` | Yalnızca LibreOffice | ❌ Hayır | — |
| `PdfToJpgConverter` | `.pdf` → `.jpg` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | **Çok sayfalı PDF'te her sayfa ayrı dosya**: `ad_p1.jpg, ad_p2.jpg, ...`; tek sayfada `ad.jpg`. `options.dpi` render çözünürlüğü, `options.quality` JPEG kalitesi |
| `PdfToPngConverter` | `.pdf` → `.png` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | `PdfToJpgConverter` ile aynı rasterizasyon mantığı (çok sayfada `_p{n}` suffix); PNG kayıpsız olduğu için `options.quality` kullanılmaz |
| `PdfCompressConverter` | `.pdf` → `.pdf` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | Kaynak/hedef uzantı **aynı** — `get_output_path()` override edilir (`{stem}_sikistirilmis.pdf`), aksi halde varsayılan çıktı klasöründe kaynağın üzerine yazardı. Sayfaları görsele çevirmez, `doc.save(garbage=4, deflate=True, ...)` ile akış temizliği yapar |
| `JpgToPdfConverter` | `.jpg` → `.pdf` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | `accepted_extensions` override: `.jpg` **ve** `.jpeg` kabul eder (kaynak halen `.jpg`) |

## Motor Tespit Sırası

- **PPTX→PDF**: Windows + `pywin32` kuruluysa MS Office; değilse
  `soffice`/`libreoffice` PATH'te veya bilinen kurulum yollarında aranır
  (bkz. [[libreoffice-motoru]]).
- **PDF→DOCX**: `pdf2docx` paketi varsa öncelikli (saf Python, dış süreç
  gerektirmez); yoksa LibreOffice headless.
- **DOCX→PDF, PDF→ODT**: tek motor, alternatif yok — LibreOffice şart.
- **PDF→JPG, PDF→PNG, PDF Sıkıştır, JPG→PDF**: tek motor, alternatif
  yok — PyMuPDF şart.

## Kurulmamışsa Ne Olur

Her converter'ın `unavailable_hint` property'si (bkz. [[converter-arayuzu]])
kullanıcıya kurulum komutunu gösterir; `MainWindow._start_conversion()`
`is_available` `False` ise dönüşümü hiç başlatmadan bu metni bir
`QMessageBox`'ta gösterir.

## İlgili Sayfalar

- [[converter-arayuzu]] — bu tablodaki tüm converter'ların uyduğu sözleşme
- [[libreoffice-motoru]] — paylaşılan LibreOffice detayları
- [[converter-ekleme]] — buraya yeni bir satır eklemek için rehber
