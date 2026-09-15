# LibreOffice Motoru

`core/converters/libreoffice_engine.py` → `LibreOfficeEngine` sınıfı.
Önceden `pptx_to_pdf.py` ve `pdf_to_docx.py` içinde birebir kopyalanmış
~60 satırlık tespit + subprocess mantığının ortaklandığı yer.

## Ne Yapar

```python
class LibreOfficeEngine:
    def is_available(self) -> bool: ...
    def convert_to(self, source_path, output_path, target_ext, extra_args=None) -> None: ...
```

- `_detect()`: `libreoffice`/`soffice`'i PATH'te (`shutil.which`) veya
  bilinen kurulum yollarında (`C:\Program Files\LibreOffice\...`, macOS/Linux
  yolları) arar.
- `convert_to()`: `soffice --headless --invisible --nologo --norestore
  --convert-to <ext> --outdir <dir> <source>` çalıştırır, çıktının beklenen
  yerde olduğunu doğrular (yoksa kaynak dizine fallback bakar), gerekiyorsa
  istenen `output_path`'e taşır.

## `--infilter=writer_pdf_import` Neden Gerekli

PDF→DOCX/ODT dönüşümünde (`pdf_to_docx.py`), LibreOffice'e PDF'i bir Writer
belgesi olarak import etmesi söylenmezse `"no export filter"` hatası verir.
Bu yüzden `_LibreOfficePdfStrategy.convert()`, `extra_args=["--infilter=writer_pdf_import"]`
ile çağırır. PPTX→PDF (`_LibreOfficeStrategy`) buna ihtiyaç duymaz (Impress
belgesi zaten doğru filtreyle açılır).

## Kimler Kullanıyor

- `PptxToPdfConverter._LibreOfficeStrategy` — MS Office yoksa fallback
- `PdfToDocxConverter._LibreOfficePdfStrategy` — pdf2docx yoksa fallback
- `PdfToOdtConverter` — tek motor, doğrudan bağımlı

## Alternatif Motorlar (LibreOffice'e ihtiyaç duymayanlar)

- **MS Office (win32com)**: yalnızca Windows + Office kurulu + `pywin32`.
  PPTX→PDF'te tercih edilir (daha hızlı, LibreOffice kurulumu gerektirmez).
- **pdf2docx**: saf Python, PDF→DOCX'te tercih edilir.
- **PyMuPDF (fitz)**: PDF→JPG ve JPG→PDF'te LibreOffice'e hiç ihtiyaç
  duymaz — bkz. [[donusturucu-envanteri]].

## İlgili Sayfalar

- [[donusturucu-envanteri]] — hangi converter'ın hangi motoru kullandığı
- [[converter-ekleme]] — yeni bir LibreOffice-tabanlı converter eklerken bu sınıfı yeniden kullanma
