# Test ve Bağımlılıklar

## Testler (`tests/`)

`core/` katmanı Qt'siz olduğu için testler PySide6 başlatmadan,
milisaniyeler içinde çalışır (14 test ~0.5s) — bkz. [[mimari]].

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
  iptal mantığını test eder.
- `tests/test_registry_and_discovery.py` — `discover_converter_classes()`'in
  gerçek 5 converter'ı bulduğunu, `register_all()`'ın idempotent olduğunu
  doğrular.

`conftest.py` (proje kökü), `pytest`'in çağırılma biçiminden bağımsız
olarak proje kökünü `sys.path`'e ekler.

**Kural**: `core/`'a eklenen her yeni mantık için buraya Qt gerektirmeyen
bir test eklenir — bkz. [[rules]].

## Python Bağımlılıkları

- `requirements.txt` — çalışma zamanı: `PySide6`, `pdf2docx`, `PyMuPDF`,
  `python-docx`, `pywin32` (yalnızca `sys_platform == "win32"`).
- `requirements-dev.txt` — `requirements.txt` + `pytest`.

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
