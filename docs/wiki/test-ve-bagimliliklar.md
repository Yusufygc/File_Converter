# Test ve Bağımlılıklar

## Testler (`tests/`)

`core/` katmanı Qt'siz olduğu için testler PySide6 başlatmadan,
milisaniyeler içinde çalışır (96 test ~2s) — bkz. [[mimari]].

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
- `tests/test_file_discovery.py` — `ui_qml/bridge/file_discovery.collect_files()`'ı
  (Qt'siz, saf pathlib mantığı) iç içe klasör yapısıyla test eder.
- `tests/test_pdf_merge_converter.py`, `tests/test_pdf_split_converter.py`,
  `tests/test_jpg_to_pdf_converter.py` — gerçek PyMuPDF ile; birleştirme
  (`convert_many`) ve bölme davranışları, çıktı adının kaynakla
  çakışmadığı, `isinstance(conv, IMergeConverter)` kontrolleri.
- `tests/test_pdf_to_txt_converter.py` — gerçek PyMuPDF ile metin
  çıkarma, çok sayfalı PDF'te sayfa ayracının doğru eklendiği.
- `tests/test_docx_to_txt_converter.py` — gerçek `python-docx` ile
  paragraf metni çıkarma.
- `tests/test_office_conversions.py` — `office_conversions.py`'deki 7
  `SimpleLibreOfficeConverter` alt sınıfı için `pytest.mark.parametrize`
  ile ortak, LibreOffice binary'sine ihtiyaç duymayan kontroller
  (`validate`, `is_available` tipi, uzantı/ad doğruluğu,
  `is_parallel_safe=False`) — `test_docx_to_pdf_converter.py`'deki
  "gerçek dönüşüm testi yok" prensibiyle aynı.

- `tests/test_packaging.py` — `core/` altındaki her klasörün
  `__init__.py` içerdiğini ve PyInstaller'ın `collect_submodules('core.converters')`'ının
  diskteki her converter modülünü bulduğunu doğrular (bkz. [[paketleme]]).

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

- **LibreOffice** — PPTX→PDF fallback, PDF→DOCX fallback, PDF→ODT,
  DOCX↔ODT ve tüm XLSX/CSV/ODS ailesinin (bkz. [[donusturucu-envanteri]]'ndeki
  `SimpleLibreOfficeConverter` alt sınıfları) tek motoru. Kurulu
  değilse `LibreOfficeEngine.is_available()` `False` döner, ilgili
  converter kullanıcıya kurulum linki gösterir (bkz. [[libreoffice-motoru]]).
- **Microsoft Office** — yalnızca Windows'ta, `pywin32` üzerinden
  PPTX→PDF'te tercih edilen motor; kurulu değilse otomatik LibreOffice'e düşer.
- **Tesseract OCR** — taranmış (görüntü tabanlı) PDF'lerden metin
  çıkarımı için (`core/converters/ocr_engine.py`, bkz. [[log]]).
  `pytesseract` (pip) yalnızca sarmalayıcı — gerçek motor `winget install
  --id UB-Mannheim.TesseractOCR -e` ile sistem geneline kurulur.
  `OcrEngine._find_tesseract_binary()` önce `PATH`'te (`shutil.which`),
  bulamazsa `C:\Program Files\Tesseract-OCR\tesseract.exe` gibi bilinen
  yollarda arar; kurulu değilse `is_available()` `False` döner,
  `PdfToDocxConverter`/`PdfToTxtConverter` OCR'siz (görsel gömme/motor
  hatası) yoluna düşer. Türkçe dil paketi (`tur.traineddata`) varsayılan
  kurulumda **gelmez** — eklenmezse `OcrEngine` otomatik `eng`'e düşer.

PyMuPDF ve pdf2docx saf Python paketleri olduğu için harici kurulum
gerektirmez — `pip install`'la gelir.

## İlgili Sayfalar

- [[mimari]] — Qt'siz `core/`'un test edilebilirliğe katkısı
- [[rules]] — test yazma kuralı
- [[donusturucu-envanteri]] — hangi converter hangi harici araca bağımlı
- [[paketleme]] — bu bağımlılıkların dağıtılabilir exe'ye paketlenmesi
