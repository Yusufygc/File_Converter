"""
iLovePDF genişletmesi Paket 2 — PyMuPDF tabanlı PDF araçlarını gerçek
PyMuPDF ile uçtan uca test eder (Döndür, Sayfa Numarası, Filigran,
Şifrele, Şifre Kaldır, Onar, Görsel Çıkar) ve ortak option şemasını
(`OptionSpec`, `ConversionOptions.extra`) doğrular.
"""

import fitz
import pytest

from core.converters.pdf_extract_images import PdfExtractImagesConverter
from core.converters.pdf_page_numbers import PdfPageNumbersConverter
from core.converters.pdf_protect import PdfProtectConverter, PdfUnlockConverter
from core.converters.pdf_repair import PdfRepairConverter
from core.converters.pdf_rotate import PdfRotateConverter
from core.converters.pdf_watermark import PdfWatermarkConverter
from core.interfaces.converter_interface import ConversionOptions
from core.interfaces.option_schema_interface import IOptionsProvider, OptionSpec
from core.interfaces.page_range_interface import IPageRangeSelectable


def _make_pdf(path, page_count: int = 3, rotation: int = 0) -> None:
    doc = fitz.open()
    for i in range(page_count):
        page = doc.new_page()
        page.insert_text((72, 72), f"page {i + 1}")
        if rotation:
            page.set_rotation(rotation)
    doc.save(str(path))
    doc.close()


def _opts(tmp_path, **extra):
    return ConversionOptions(output_dir=tmp_path / "out", extra=extra)


# ── Option şeması ─────────────────────────────────────────────────────

def test_option_spec_rejects_unknown_kind_and_empty_choice():
    with pytest.raises(ValueError):
        OptionSpec(key="x", label="X", kind="slider")
    with pytest.raises(ValueError):
        OptionSpec(key="x", label="X", kind="choice")


def test_get_extra_treats_empty_string_as_missing():
    opts = ConversionOptions(extra={"a": "", "b": 0, "c": None})
    assert opts.get_extra("a", "def") == "def"
    assert opts.get_extra("b", 5) == 0
    assert opts.get_extra("c", 7) == 7
    assert opts.get_extra("yok", 1) == 1


@pytest.mark.parametrize(
    "cls,suffix",
    [
        (PdfRotateConverter, "_dondurulmus"),
        (PdfPageNumbersConverter, "_numarali"),
        (PdfWatermarkConverter, "_filigranli"),
        (PdfProtectConverter, "_sifreli"),
        (PdfUnlockConverter, "_sifresiz"),
        (PdfRepairConverter, "_onarilmis"),
    ],
)
def test_output_never_collides_with_source(cls, suffix, tmp_path):
    src = tmp_path / "belge.pdf"
    conv = cls()
    out = conv.get_output_path(src, ConversionOptions())
    assert out != src
    assert out.name == f"belge{suffix}.pdf"
    assert conv.is_parallel_safe is True
    assert conv.active_engine_name == "Yerleşik"


# ── Döndür ─────────────────────────────────────────────────────────────

def test_rotate_all_pages(tmp_path):
    src = tmp_path / "d.pdf"
    _make_pdf(src, 2)
    conv = PdfRotateConverter()
    assert isinstance(conv, IPageRangeSelectable)
    assert isinstance(conv, IOptionsProvider)

    result = conv.convert(src, _opts(tmp_path, angle=270))

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    assert [p.rotation for p in doc] == [270, 270]
    doc.close()


def test_rotate_page_range_only_and_accumulates(tmp_path):
    src = tmp_path / "d.pdf"
    _make_pdf(src, 3, rotation=90)
    opts = _opts(tmp_path, angle=180)
    opts.page_range = "2"

    result = PdfRotateConverter().convert(src, opts)

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    assert [p.rotation for p in doc] == [90, 270, 90]
    doc.close()


# ── Sayfa numarası ──────────────────────────────────────────────────────

@pytest.mark.parametrize("rotation", [0, 90])
def test_page_numbers_written_on_each_page(tmp_path, rotation):
    src = tmp_path / "n.pdf"
    _make_pdf(src, 3, rotation=rotation)

    result = PdfPageNumbersConverter().convert(
        src, _opts(tmp_path, position="bottom-right", format="n_of_total", start=5)
    )

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    texts = [p.get_text() for p in doc]
    doc.close()
    assert "5 / 7" in texts[0]
    assert "7 / 7" in texts[2]


def test_page_numbers_rejects_unknown_position(tmp_path):
    src = tmp_path / "n.pdf"
    _make_pdf(src, 1)
    result = PdfPageNumbersConverter().convert(src, _opts(tmp_path, position="orta"))
    assert result.success is False
    assert "konum" in result.error_message.lower()


# ── Filigran ───────────────────────────────────────────────────────────

def test_watermark_requires_text(tmp_path):
    src = tmp_path / "w.pdf"
    _make_pdf(src, 1)
    result = PdfWatermarkConverter().convert(src, _opts(tmp_path, text=""))
    assert result.success is False
    assert "Metin" in result.error_message


def test_watermark_adds_turkish_text(tmp_path):
    src = tmp_path / "w.pdf"
    _make_pdf(src, 2)

    result = PdfWatermarkConverter().convert(src, _opts(tmp_path, text="GİZLİ ŞĞ", opacity=40))

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    for page in doc:
        assert "GİZLİ ŞĞ" in page.get_text()
    doc.close()


# ── Şifrele / Şifre kaldır ────────────────────────────────────────────

def test_protect_then_unlock_roundtrip(tmp_path):
    src = tmp_path / "s.pdf"
    _make_pdf(src, 2)

    protected = PdfProtectConverter().convert(src, _opts(tmp_path, password="abc123"))
    assert protected.success, protected.error_message
    doc = fitz.open(str(protected.output_path))
    assert doc.needs_pass
    assert doc.authenticate("abc123")
    doc.close()

    wrong = PdfUnlockConverter().convert(protected.output_path, _opts(tmp_path, password="yanlis"))
    assert wrong.success is False
    assert "yanlış" in wrong.error_message

    unlocked = PdfUnlockConverter().convert(protected.output_path, _opts(tmp_path, password="abc123"))
    assert unlocked.success, unlocked.error_message
    doc = fitz.open(str(unlocked.output_path))
    assert not doc.needs_pass
    assert "page 1" in doc[0].get_text()
    doc.close()


def test_protect_requires_password(tmp_path):
    src = tmp_path / "s.pdf"
    _make_pdf(src, 1)
    result = PdfProtectConverter().convert(src, _opts(tmp_path))
    assert result.success is False
    assert "Parola" in result.error_message


def test_unlock_rejects_unencrypted_pdf(tmp_path):
    src = tmp_path / "s.pdf"
    _make_pdf(src, 1)
    result = PdfUnlockConverter().convert(src, _opts(tmp_path))
    assert result.success is False
    assert "şifreli değil" in result.error_message


# ── Onar ───────────────────────────────────────────────────────────────

def test_repair_rebuilds_broken_xref(tmp_path):
    src = tmp_path / "bozuk.pdf"
    _make_pdf(src, 2)
    raw = src.read_bytes()
    # xref ofsetini boz: MuPDF açılışta tabloyu yeniden kurmak zorunda kalır.
    idx = raw.rfind(b"startxref")
    src.write_bytes(raw[:idx] + b"startxref\n999999\n%%EOF\n")

    result = PdfRepairConverter().convert(src, _opts(tmp_path))

    assert result.success, result.error_message
    doc = fitz.open(str(result.output_path))
    assert doc.page_count == 2
    assert not doc.is_repaired
    doc.close()


# ── Görsel çıkar ───────────────────────────────────────────────────────

def test_extract_images_deduplicates_by_xref(tmp_path):
    png = tmp_path / "kare.png"
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 8, 8), False)
    pix.clear_with(200)
    pix.save(str(png))

    src = tmp_path / "g.pdf"
    doc = fitz.open()
    for _ in range(2):
        page = doc.new_page()
        page.insert_image(fitz.Rect(50, 50, 150, 150), filename=str(png))
    doc.save(str(src))
    doc.close()

    result = PdfExtractImagesConverter().convert(src, _opts(tmp_path))

    assert result.success, result.error_message
    assert result.page_count == 1  # aynı görsel iki sayfada tek xref
    assert result.output_path.name.startswith("g_gorsel1.")
    assert result.output_path.exists()


def test_extract_images_errors_when_none(tmp_path):
    src = tmp_path / "bos.pdf"
    _make_pdf(src, 1)
    result = PdfExtractImagesConverter().convert(src, _opts(tmp_path))
    assert result.success is False
    assert "görsel" in result.error_message
