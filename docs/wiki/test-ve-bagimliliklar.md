# Test ve Bağımlılıklar

## Testler (`tests/`)

`core/` katmanı Qt'siz olduğu için testler PySide6 başlatmadan,
milisaniyeler içinde çalışır (46 test ~1s) — bkz. [[mimari]].

```bash
python -m pytest tests/ -v
```

- `tests/_fakes.py` → `FakeConverter(BaseConverter)` — gerçek harici motor
  (LibreOffice, PyMuPDF) gerektirmeyen, testlerde paylaşılan sahte converter.
- `tests/test_00_core_has_no_qt_dependency.py` — `core` import edildiğinde
  `sys.modules`'da `PySide6` olmadığını doğrular (dosya adı `00_` öneki ile
  bilerek ilk çalışacak şekilde sıralanmış).
- `tests/test_base_converter.py` — `validate`/`is_available`/hata sarmalama
  davranışını `FakeConverter` ile test eder.
- `tests/test_conversion_facade.py` — `convert_batch()`'in progress/callback/
  iptal mantığını; `convert_batch_parallel()`'ın tüm dosyaları işlediğini
  ve iptalde henüz başlamamış işleri durdurduğunu (yapay gecikmeli
  `_SlowFakeConverter` ile — aksi halde iptal penceresi deterministik
  yakalanamaz) test eder.
- `tests/test_registry_and_discovery.py` — `discover_converter_classes()`'in
  tüm converter'ları bulduğunu (sabit sayı değil, `discover_converter_classes()`'in
  kendisinden türetilen beklenen sayıyla karşılaştırır — yeni converter
  eklendiğinde test kırılmaz), `register_all()`'ın idempotent olduğunu,
  aynı uzantı çiftini paylaşan farklı converter'ların (`tests/_fakes.py`'deki
  `AnotherFakeConverter`) birbirini ezmediğini doğrular.
- `tests/test_pdf_to_png_converter.py` — gerçek `PdfToPngConverter`'ı
  gerçek PyMuPDF ile uçtan uca test eder (diğerlerinin aksine
  `FakeConverter` kullanmaz) — tek/çok sayfalı PDF, geçersiz dosya reddi.
- `tests/test_pdf_compress_converter.py` — gerçek `PdfCompressConverter`;
  çıktı dosya adının kaynaktan **farklı** olduğunu (üzerine yazma
  koruması) ve sayfa sayısının korunduğunu doğrular.
- `tests/test_docx_to_pdf_converter.py` — `DocxToPdfConverter`'ın
  LibreOffice binary'sine ihtiyaç duymayan kısımları (`validate`,
  `is_available`, `unavailable_hint`) — gerçek dönüşüm testi yok
  (`PdfToDocxConverter`/`PdfToOdtConverter` için de yok, CI'da
  LibreOffice garantili değil).
- `tests/test_file_discovery.py` — `ui/file_discovery.collect_files()`'ı
  (Qt'siz, saf pathlib mantığı) iç içe klasör yapısıyla test eder.
- `tests/test_pdf_merge_converter.py`, `tests/test_pdf_split_converter.py`,
  `tests/test_jpg_to_pdf_converter.py` — gerçek PyMuPDF ile; birleştirme
  (`convert_many`) ve bölme davranışları, çıktı adının kaynakla
  çakışmadığı, `isinstance(conv, IMergeConverter)` kontrolleri.

`conftest.py` (proje kökü), `pytest`'in çağırılma biçiminden bağımsız
olarak proje kökünü `sys.path`'e ekler.

**Kural**: `core/`'a eklenen her yeni mantık için buraya Qt gerektirmeyen
bir test eklenir — bkz. [[rules]].

## CI (GitHub Actions)

`.github/workflows/test.yml` — her `push`/`pull_request`'te `ubuntu-latest`
üzerinde `pip install -r requirements-dev.txt` + `pytest tests/ -v` çalışır.
Testler hiç Qt import etmediği ve `pywin32` Linux'ta ortam işaretiyle
atlandığı için Linux runner yeterli — mimarinin "Qt'siz `core/`" iddiasını
her push'ta otomatik doğrular (bkz. [[mimari]]).

## Python Bağımlılıkları

- `requirements.txt` — çalışma zamanı: `PySide6`, `pdf2docx`, `PyMuPDF`,
  `python-docx`, `pywin32` (yalnızca `sys_platform == "win32"`).
- `requirements-dev.txt` — `requirements.txt` + `pytest` + `pyinstaller`
  (bkz. [[paketleme]]).

```bash
pip install -r requirements.txt        # çalıştırmak için
pip install -r requirements-dev.txt    # geliştirmek/test için
```

## Harici Araç Bağımlılıkları (pip ile gelmez)

- **LibreOffice** — PPTX→PDF fallback, PDF→DOCX fallback, PDF→ODT'nin
  tek motoru. Kurulu değilse `LibreOfficeEngine.is_available()` `False`
  döner, ilgili converter kullanıcıya kurulum linki gösterir
  (bkz. [[libreoffice-motoru]]).
- **Microsoft Office** — yalnızca Windows'ta, `pywin32` üzerinden
  PPTX→PDF'te tercih edilen motor; kurulu değilse otomatik LibreOffice'e düşer.

PyMuPDF ve pdf2docx saf Python paketleri olduğu için harici kurulum
gerektirmez — `pip install`'la gelir.

## İlgili Sayfalar

- [[mimari]] — Qt'siz `core/`'un test edilebilirliğe katkısı
- [[rules]] — test yazma kuralı
- [[donusturucu-envanteri]] — hangi converter hangi harici araca bağımlı
- [[paketleme]] — bu bağımlılıkların dağıtılabilir exe'ye paketlenmesi
