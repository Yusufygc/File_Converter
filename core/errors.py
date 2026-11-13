"""
Dönüşüm Hataları
==================
Kullanıcıya gösterilecek hata metni ile teknik ayrıntıyı birbirinden ayırır.

Önceden `BaseConverter` her exception'ı `str(exc)` ile doğrudan UI'a
taşıyordu: kütüphane iç mesajları ("code=2: cannot open broken document"),
LibreOffice stderr çıktısı, dosya yolları kullanıcıya görünüyordu. Artık:

- Converter'lar bilinen hata durumlarında `ConversionError` alt sınıfı
  fırlatır: `user_message` Türkçe ve teknik terimsizdir, `detail` yalnızca
  günlük dosyasına yazılır.
- Beklenmeyen exception'lar `to_user_error()` ile tanınan sınıflara
  (izin, disk, zaman aşımı, bozuk dosya...) çevrilir; tanınmayanlar genel
  bir mesaja düşer ve tam traceback günlüğe yazılır.

`core/` Qt import etmez; bu modül de etmez (bkz. docs/wiki/rules.md).

SRP : Hata sınıflandırma ve kullanıcı mesajı üretiminden sorumlu.
OCP : Yeni bir hata türü, mevcut converter'lara dokunmadan alt sınıf
      olarak eklenir.
"""

from __future__ import annotations

import errno
import subprocess
from typing import Optional


class ConversionError(Exception):
    """Kullanıcıya gösterilebilir mesaj taşıyan dönüşüm hatası (taban)."""

    default_message = "Dönüşüm tamamlanamadı."

    def __init__(self, user_message: Optional[str] = None, *, detail: Optional[str] = None):
        self.user_message = user_message or self.default_message
        self.detail = detail
        super().__init__(self.user_message)


class InvalidOptionError(ConversionError, ValueError):
    """
    Kullanıcının girdiği bir seçenek (aralık, parola, metin...) geçersiz.
    `ValueError` da sayılır: `IPageRangeSelectable.parse_page_range()`
    sözleşmesi geçersiz girişte `ValueError` vaat ediyor.
    """

    default_message = "Girilen seçenek geçersiz."


class PasswordProtectedError(ConversionError):
    default_message = "Dosya parola korumalı. Önce 'PDF Şifre Kaldır' aracını kullanın."


class WrongPasswordError(ConversionError):
    default_message = "Parola yanlış."


class NothingToConvertError(ConversionError):
    """Dosyada işlenecek içerik yok (tablo, görsel, metin...)."""

    default_message = "Dosyada dönüştürülecek içerik bulunamadı."


class CorruptFileError(ConversionError):
    default_message = "Dosya bozuk veya okunamıyor."


class FileAccessError(ConversionError):
    default_message = (
        "Dosyaya erişilemedi. Dosya başka bir programda açık olabilir "
        "ya da klasöre yazma izniniz olmayabilir."
    )


class ExternalToolError(ConversionError):
    """Harici program (LibreOffice, Microsoft Office) dönüşümü tamamlayamadı."""

    default_message = "Dönüştürme programı dosyayı işleyemedi."


class ToolTimeoutError(ConversionError):
    default_message = "İşlem çok uzun sürdü ve durduruldu. Dosya çok büyük veya karmaşık olabilir."


class MissingComponentError(ConversionError):
    default_message = "Uygulamanın bir bileşeni eksik. FileConvert'ü yeniden kurmayı deneyin."


UNEXPECTED_ERROR_MESSAGE = (
    "Beklenmeyen bir hata oluştu. Ayrıntılar günlük dosyasına kaydedildi."
)

# PyMuPDF'in bozuk/boş dosya exception'ları. Sınıf adıyla tanınır: bu modül
# hata sınıflandırması için PyMuPDF'i import etmek zorunda kalmasın.
_CORRUPT_EXCEPTION_NAMES = {"FileDataError", "EmptyFileError"}


def to_user_error(exc: BaseException) -> ConversionError:
    """
    Herhangi bir exception'ı kullanıcıya gösterilebilir `ConversionError`'a
    çevirir. Orijinal exception metni `detail`'e konur (günlük için).
    """
    if isinstance(exc, ConversionError):
        return exc

    detail = f"{type(exc).__name__}: {exc}"

    if isinstance(exc, subprocess.TimeoutExpired):
        return ToolTimeoutError(detail=detail)
    if isinstance(exc, PermissionError):
        return FileAccessError(detail=detail)
    if isinstance(exc, FileNotFoundError):
        return FileAccessError("Dosya bulunamadı. Taşınmış veya silinmiş olabilir.", detail=detail)
    if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
        return FileAccessError("Diskte yeterli boş alan yok.", detail=detail)
    if isinstance(exc, MemoryError):
        return ConversionError("Bellek yetersiz. Daha küçük dosyalarla deneyin.", detail=detail)
    if isinstance(exc, ImportError):
        return MissingComponentError(detail=detail)
    if any(cls.__name__ in _CORRUPT_EXCEPTION_NAMES for cls in type(exc).__mro__):
        return CorruptFileError(detail=detail)
    return ConversionError(UNEXPECTED_ERROR_MESSAGE, detail=detail)


def is_unexpected(error: ConversionError) -> bool:
    """Tanınmayan (genel mesaja düşmüş) bir hata mı — tam traceback loglanmalı."""
    return error.user_message == UNEXPECTED_ERROR_MESSAGE
