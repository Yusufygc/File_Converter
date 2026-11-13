# Hata Yönetimi ve Kullanıcı Metinleri

Kullanıcıya gösterilen her metin (hata, kurulum ipucu, yöntem etiketi)
**Türkçe ve teknik terimsizdir**; teknik ayrıntı (exception metni,
traceback, harici program çıktısı) yalnızca günlük dosyasına gider.
Karar: 2026-11-13, kullanıcı isteği ("UI'da backend'e ait terimler
olmasın") — bkz. [[log]].

## Önceki Durum (neden değişti)

- `BaseConverter` her exception'ı `str(exc)` ile UI'a taşıyordu:
  "code=2: cannot open broken document", LibreOffice stderr'i, dosya yolları.
- `unavailable_hint` metinleri `pip install pymupdf`, `sudo apt install`,
  `brew install`, `winget install` komutları içeriyordu — exe kullanıcısı
  pip kuramaz, kütüphaneler zaten pakette.
- `active_engine_name` "PyMuPDF", "pdf2docx + OCR", "pymupdf4llm" gibi
  kütüphane adları gösteriyordu.
- Çıktı klasörü oluşturma `try` dışındaydı: izin/disk hatası toplu işi
  düşürüyor, worker sinyal vermeden ölüyor, UI "dönüştürülüyor"da kalıyordu.
- Paralel facade `except Exception: continue` ile gerçek hataları
  sessizce yutuyordu (dosya sonuç listesinden kayboluyordu).
- `main.py` yakalanmamış hatada exception metnini ve traceback'i pencerede gösteriyordu.

## Katmanlar

| Katman | Dosya | Sorumluluk |
|---|---|---|
| Hata sınıfları | `core/errors.py` | `ConversionError(user_message, detail=)` + alt sınıflar; `to_user_error(exc)` çevirisi |
| Ortak metinler | `core/user_texts.py` | `ENGINE_*` etiketleri, `HINT_*` kurulum ipuçları |
| Şablon metot | `core/converters/base.py` | `convert()`/`convert_many()` her şeyi `try` içinde yapar, `_user_error_message()` ile çevirip loglar |
| Güvenlik ağı | `core/conversion_facade.py` | `_safe_convert()` — `BaseConverter` dışı converter'dan sızan hatayı başarısız sonuca çevirir; paralel modda yalnızca `CancelledError` atlanır |
| İş parçacığı | `ui_qml/bridge/conversion_worker.py` | `run()` hiçbir durumda sinyalsiz bitmez (`_all_failed()`) |
| Günlük | `core/utils/logging_setup.py`, `main.py` | `%LOCALAPPDATA%\FileConvert\logs\fileconvert.log` (1 MB × 3, dönen); yakalanmamış hata penceresi yalnızca günlük yolunu gösterir |

## Hata Sınıfları (`core/errors.py`)

| Sınıf | Ne zaman | Varsayılan mesaj |
|---|---|---|
| `InvalidOptionError` (aynı zamanda `ValueError`) | Kullanıcı girdisi geçersiz: sayfa aralığı, boş parola/metin | "Girilen seçenek geçersiz." |
| `PasswordProtectedError` | Girdi PDF parolalı | "Dosya parola korumalı. Önce 'PDF Şifre Kaldır'…" |
| `WrongPasswordError` | Parola doğrulanamadı | "Parola yanlış." |
| `NothingToConvertError` | İçerik yok (tablo, görsel, metin) | "Dosyada dönüştürülecek içerik bulunamadı." |
| `CorruptFileError` | Bozuk dosya; PyMuPDF `FileDataError`/`EmptyFileError` adla tanınır | "Dosya bozuk veya okunamıyor." |
| `FileAccessError` | `PermissionError`, `FileNotFoundError`, disk dolu (`ENOSPC`) | "Dosyaya erişilemedi…" |
| `ExternalToolError` | LibreOffice/PowerPoint dönüşümü başarısız (stderr/COM hatası `detail`'de) | "Dönüştürme programı dosyayı işleyemedi." |
| `ToolTimeoutError` | `subprocess.TimeoutExpired` | "İşlem çok uzun sürdü…" |
| `MissingComponentError` | `ImportError`, hiçbir yöntem yok | "…FileConvert'ü yeniden kurmayı deneyin." |

Tanınmayan exception → `UNEXPECTED_ERROR_MESSAGE` ("Beklenmeyen bir hata
oluştu. Ayrıntılar günlük dosyasına kaydedildi.") + `logging.error(exc_info=...)`
ile tam traceback. Tanınan hatalar `detail` ile `warning` seviyesinde loglanır.

## Kurallar (yeni kod yazarken)

- `_do_convert` içinde kullanıcının anlaması gereken bir durum varsa
  **`ConversionError` alt sınıfı** fırlat; `ValueError`/`RuntimeError`
  yalnızca programlama hatası (olmaması gereken durum) içindir — onlar
  genel mesaja düşer.
- Mesaja kütüphane adı, dosya yolu, exception metni koyma; teknik bilgi
  `detail=` parametresine.
- `active_engine_name`/`unavailable_hint` için metin yazma, `core/user_texts.py`
  sabitlerini kullan. Kullanıcının kendisinin kurabileceği programlar
  (LibreOffice, Microsoft Office, Tesseract) adıyla anılır + indirme
  bağlantısı; pakete gömülü kütüphaneler "Yerleşik" olarak görünür.
- Harici bir programın "çıktı yok" durumu `FileNotFoundError` ile
  bildirilmez — `to_user_error()` onu "kaynak dosya taşınmış" sanar;
  `ExternalToolError` kullan.
- `tests/test_errors.py::test_user_facing_texts_have_no_backend_terms`
  keşfedilen tüm converter'ların `display_name`/`active_engine_name`/
  `unavailable_hint` metinlerinde `pip`, `winget`, kütüphane adları vb.
  arar — yeni converter bu testi geçmelidir.

## İlgili Sayfalar

- [[converter-arayuzu]] — `BaseConverter` şablon metodu
- [[converter-ekleme]] — yeni converter'da hata/metin kuralları
- [[ui-katmani]] — mesajların UI'da göründüğü yerler (SummaryModal, FileListView ipucu, bildirimler)
- [[rules]] — kodlama kuralları
- [[paketleme]] — konsolsuz exe'de günlük dosyasının önemi
