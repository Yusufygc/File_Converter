# Dönüştürücü Envanteri

`core/converters/` altında [[converter-ekleme]] tarafından otomatik
keşfedilen 6 converter. Sıra, `ui/converter_catalog.py`'deki
`_PREFERRED_ORDER` ile aynı (varsayılan dropdown sırası).

| Converter | Kaynak → Hedef | Motor(lar) | `IEngineSelectable` | Özel davranış |
|---|---|---|---|---|
| `PptxToPdfConverter` | `.pptx` → `.pdf` | MS Office (win32com) → LibreOffice fallback | ✅ Evet | Tek gerçek kullanıcı-seçimli motor; `_MsOfficeStrategy`/`_LibreOfficeStrategy` |
| `PdfToDocxConverter` | `.pdf` → `.docx` | pdf2docx → LibreOffice fallback | ❌ Hayır (otomatik seçer) | `pdf2docx` yalnızca `.docx` üretir, ODT'ye düşemez |
| `PdfToOdtConverter` | `.pdf` → `.odt` | Yalnızca LibreOffice | ❌ Hayır | — |
| `PdfToJpgConverter` | `.pdf` → `.jpg` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | **Çok sayfalı PDF'te her sayfa ayrı dosya**: `ad_p1.jpg, ad_p2.jpg, ...`; tek sayfada `ad.jpg`. `options.dpi` render çözünürlüğü, `options.quality` JPEG kalitesi |
| `PdfToPngConverter` | `.pdf` → `.png` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | `PdfToJpgConverter` ile aynı rasterizasyon mantığı (çok sayfada `_p{n}` suffix); PNG kayıpsız olduğu için `options.quality` kullanılmaz |
| `JpgToPdfConverter` | `.jpg` → `.pdf` | PyMuPDF (`fitz`) | ❌ Hayır (tek motor) | `accepted_extensions` override: `.jpg` **ve** `.jpeg` kabul eder (kaynak halen `.jpg`) |

## Motor Tespit Sırası

- **PPTX→PDF**: Windows + `pywin32` kuruluysa MS Office; değilse
  `soffice`/`libreoffice` PATH'te veya bilinen kurulum yollarında aranır
  (bkz. [[libreoffice-motoru]]).
- **PDF→DOCX**: `pdf2docx` paketi varsa öncelikli (saf Python, dış süreç
  gerektirmez); yoksa LibreOffice headless.
- **PDF→ODT, PDF→JPG, JPG→PDF**: tek motor, alternatif yok — sırasıyla
  LibreOffice ve PyMuPDF şart.

## Kurulmamışsa Ne Olur

Her converter'ın `unavailable_hint` property'si (bkz. [[converter-arayuzu]])
kullanıcıya kurulum komutunu gösterir; `MainWindow._start_conversion()`
`is_available` `False` ise dönüşümü hiç başlatmadan bu metni bir
`QMessageBox`'ta gösterir.

## İlgili Sayfalar

- [[converter-arayuzu]] — bu tablodaki tüm converter'ların uyduğu sözleşme
- [[libreoffice-motoru]] — paylaşılan LibreOffice detayları
- [[converter-ekleme]] — buraya altıncı bir satır eklemek için rehber
