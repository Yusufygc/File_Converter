"""
Hata mekanizması (`core/errors.py`, `core/user_texts.py`) testleri:
exception → kullanıcı mesajı çevirisi, UI'a sızan teknik terim denetimi,
facade'in converter dışına sızan hataları yakalaması.
"""

import errno
import logging
import subprocess

import pytest

from core.conversion_facade import convert_batch, convert_batch_parallel, merge_files
from core.converters.discovery import discover_converter_classes
from core.errors import (
    UNEXPECTED_ERROR_MESSAGE,
    ConversionError,
    CorruptFileError,
    FileAccessError,
    InvalidOptionError,
    MissingComponentError,
    ToolTimeoutError,
    to_user_error,
)
from core.interfaces.converter_interface import ConversionOptions
from tests._fakes import FakeConverter

# UI'da görünmemesi gereken geliştirici/kütüphane terimleri.
_BACKEND_TERMS = [
    "pip ", "apt ", "brew ", "winget", "pymupdf", "pdf2docx", "python-docx",
    "openpyxl", "pymupdf4llm", "pywin32", "Traceback", "Exception", "Error:",
]


# ── to_user_error ─────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "exc,expected_cls,fragment",
    [
        (PermissionError("[WinError 32] used by another process"), FileAccessError, "başka bir programda"),
        (FileNotFoundError(2, "No such file"), FileAccessError, "bulunamadı"),
        (OSError(errno.ENOSPC, "No space left"), FileAccessError, "boş alan"),
        (subprocess.TimeoutExpired(cmd="soffice", timeout=120), ToolTimeoutError, "uzun sürdü"),
        (ImportError("No module named 'fitz'"), MissingComponentError, "yeniden kur"),
        (MemoryError(), ConversionError, "Bellek"),
        (RuntimeError("code=2: cannot open broken document"), ConversionError, UNEXPECTED_ERROR_MESSAGE),
    ],
)
def test_to_user_error_classifies_and_hides_technical_text(exc, expected_cls, fragment):
    error = to_user_error(exc)
    assert isinstance(error, expected_cls)
    assert fragment in error.user_message
    assert str(exc) not in error.user_message or not str(exc)
    assert error.detail and type(exc).__name__ in error.detail


def test_to_user_error_recognizes_pymupdf_corrupt_file_by_name():
    class FileDataError(RuntimeError):  # PyMuPDF'teki sınıfla aynı ad
        pass

    error = to_user_error(FileDataError("cannot open broken document"))
    assert isinstance(error, CorruptFileError)
    assert "bozuk" in error.user_message


def test_conversion_error_passes_through_unchanged():
    original = InvalidOptionError("Sayfa aralığı boş.")
    assert to_user_error(original) is original
    assert isinstance(original, ValueError)  # parse_page_range sözleşmesi


def test_real_corrupt_pdf_gives_user_message(tmp_path):
    from core.converters.pdf_to_png import PdfToPngConverter

    bad = tmp_path / "bozuk.pdf"
    bad.write_bytes(b"bu bir pdf degil")
    result = PdfToPngConverter().convert(bad, ConversionOptions(output_dir=tmp_path))

    assert result.success is False
    assert result.error_message == CorruptFileError.default_message


def test_output_dir_failure_is_reported_not_raised(tmp_path):
    blocker = tmp_path / "dosya"
    blocker.write_text("klasör değil")
    src = tmp_path / "input.foo"
    src.write_text("x")

    # Çıktı klasörü bir dosyanın altında: mkdir hata verir. Önceden bu,
    # try bloğunun dışında olduğu için toplu dönüşümü düşürüyordu.
    result = FakeConverter().convert(src, ConversionOptions(output_dir=blocker / "alt"))

    assert result.success is False
    assert result.error_message


def test_unexpected_error_is_logged_with_traceback(tmp_path, caplog):
    src = tmp_path / "input.foo"
    src.write_text("x")
    with caplog.at_level(logging.ERROR):
        FakeConverter(raise_error=True).convert(src, ConversionOptions(output_dir=tmp_path))
    assert any(r.exc_info for r in caplog.records)
    assert "boom" in caplog.text


# ── Facade güvenlik ağı ───────────────────────────────────────────────

class _ExplodingConverter(FakeConverter):
    """BaseConverter şablonunu atlayan, `convert()`'i doğrudan patlayan converter."""

    def convert(self, source_path, options):
        raise RuntimeError("internal bug")

    def convert_many(self, source_paths, options):
        raise RuntimeError("internal bug")


@pytest.mark.parametrize("batch_fn", [convert_batch, convert_batch_parallel])
def test_facade_turns_leaked_exceptions_into_failed_results(tmp_path, batch_fn):
    files = [tmp_path / f"f{i}.foo" for i in range(3)]
    for f in files:
        f.write_text("x")

    batch = batch_fn(files, _ExplodingConverter(), ConversionOptions(output_dir=tmp_path))

    assert batch.total == 3
    assert batch.failure_count == 3
    assert all(r.error_message == UNEXPECTED_ERROR_MESSAGE for r in batch.results)


def test_merge_facade_turns_leaked_exception_into_failed_result(tmp_path):
    src = tmp_path / "a.foo"
    src.write_text("x")
    result = merge_files(_ExplodingConverter(), [src], ConversionOptions(output_dir=tmp_path))
    assert result.success is False
    assert result.error_message == UNEXPECTED_ERROR_MESSAGE


# ── UI'a giden metinlerde teknik terim yok ───────────────────────────

@pytest.mark.parametrize("cls", discover_converter_classes(), ids=lambda c: c.__name__)
def test_user_facing_texts_have_no_backend_terms(cls):
    conv = cls()
    for text in (conv.display_name, conv.active_engine_name, conv.unavailable_hint):
        lowered = text.lower()
        for term in _BACKEND_TERMS:
            assert term.lower() not in lowered, f"{cls.__name__}: '{term}' → {text!r}"
