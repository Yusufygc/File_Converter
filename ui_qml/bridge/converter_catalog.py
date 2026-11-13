"""
Dönüştürücü Kataloğu (Kenar Çubuğu Grupları)
==============================================
Kenar çubuğundaki gruplar, grup içi sıra, kısa ad ve ikon bu TEK tablodan
gelir. Önceden `AppBridge._categorize_converter()` sınıf adı/uzantı
kurallarıyla (`"Compress" in cls_name`, `s_ext in (".xlsx", ...)`) grup
tahmin ediyordu; gruplar iki eksene (dosya türü + işlem) dağılmıştı ve
PDF ile başlayan bir iş dört ayrı grupta aranıyordu.

Gruplar kullanıcının NİYETİNE göre (2026-11-13, kullanıcı onaylı):
PDF'e dönüştür / PDF'ten dönüştür / PDF düzenle / PDF güvenlik ve bakım /
ofis biçimleri arası.

Yeni converter eklenince buraya bir satır eklenir. Eklenmezse uygulama
çökmez: converter "Diğer" grubunda, adıyla görünür ve
`tests/test_converter_catalog.py` eksik satırı yakalar.

Qt'siz düz veri (bridge katmanında ama Qt import etmez).
SRP : Yalnızca converter → grup/ad/ikon eşlemesinden sorumlu.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Group:
    id: str
    title: str
    icon: str


@dataclass(frozen=True)
class CatalogEntry:
    group: str
    short_name: str
    icon: str


GROUPS: Tuple[Group, ...] = (
    Group("to_pdf", "PDF'e Dönüştür", "document"),
    Group("from_pdf", "PDF'ten Dönüştür", "convert"),
    Group("pdf_edit", "PDF Düzenle", "merge"),
    Group("pdf_secure", "Güvenlik ve Bakım", "lock"),
    Group("office", "Ofis Biçimleri", "table"),
)
OTHER_GROUP = Group("other", "Diğer", "document")

# Sıra önemlidir: grup içi görünüm sırası ve dosya bırakılınca otomatik
# seçilecek aracın önceliği (bir türü kabul eden İLK satır seçilir: .pdf → PDF → Word).
_ENTRIES: Tuple[Tuple[str, CatalogEntry], ...] = (
    # PDF'e dönüştür
    ("DocxToPdfConverter", CatalogEntry("to_pdf", "Word → PDF", "document")),
    ("PptxToPdfConverter", CatalogEntry("to_pdf", "PowerPoint → PDF", "document")),
    ("OdpToPdfConverter", CatalogEntry("to_pdf", "ODP → PDF", "document")),
    ("XlsxToPdfConverter", CatalogEntry("to_pdf", "Excel → PDF", "table")),
    ("JpgToPdfConverter", CatalogEntry("to_pdf", "JPG → PDF", "image")),
    # PDF'ten dönüştür
    ("PdfToDocxConverter", CatalogEntry("from_pdf", "PDF → Word", "document")),
    ("PdfToOdtConverter", CatalogEntry("from_pdf", "PDF → ODT", "document")),
    ("PdfToXlsxConverter", CatalogEntry("from_pdf", "PDF → Excel", "table")),
    ("PdfToJpgConverter", CatalogEntry("from_pdf", "PDF → JPG", "image")),
    ("PdfToPngConverter", CatalogEntry("from_pdf", "PDF → PNG", "image")),
    ("PdfToTxtConverter", CatalogEntry("from_pdf", "PDF → TXT", "note")),
    ("PdfToMarkdownConverter", CatalogEntry("from_pdf", "PDF → Markdown", "note")),
    ("PdfExtractImagesConverter", CatalogEntry("from_pdf", "Görselleri Çıkar", "image")),
    # PDF düzenle
    ("PdfMergeConverter", CatalogEntry("pdf_edit", "Birleştir", "merge")),
    ("PdfSplitConverter", CatalogEntry("pdf_edit", "Böl", "split")),
    ("PdfRotateConverter", CatalogEntry("pdf_edit", "Döndür", "rotate")),
    ("PdfPageNumbersConverter", CatalogEntry("pdf_edit", "Sayfa Numarası", "page_number")),
    ("PdfWatermarkConverter", CatalogEntry("pdf_edit", "Filigran", "watermark")),
    # PDF güvenlik ve bakım
    ("PdfProtectConverter", CatalogEntry("pdf_secure", "Şifrele", "lock")),
    ("PdfUnlockConverter", CatalogEntry("pdf_secure", "Şifre Kaldır", "unlock")),
    ("PdfCompressConverter", CatalogEntry("pdf_secure", "Sıkıştır", "compress")),
    ("PdfRepairConverter", CatalogEntry("pdf_secure", "Onar", "repair")),
    ("PdfOcrConverter", CatalogEntry("pdf_secure", "Aranabilir PDF", "ocr")),
    # Ofis biçimleri arası
    ("DocxToOdtConverter", CatalogEntry("office", "Word → ODT", "document")),
    ("OdtToDocxConverter", CatalogEntry("office", "ODT → Word", "document")),
    ("DocxToTxtConverter", CatalogEntry("office", "Word → TXT", "note")),
    ("PptxToOdpConverter", CatalogEntry("office", "PowerPoint → ODP", "document")),
    ("OdpToPptxConverter", CatalogEntry("office", "ODP → PowerPoint", "document")),
    ("XlsxToOdsConverter", CatalogEntry("office", "Excel → ODS", "table")),
    ("OdsToXlsxConverter", CatalogEntry("office", "ODS → Excel", "table")),
    ("XlsxToCsvConverter", CatalogEntry("office", "Excel → CSV", "table")),
    ("CsvToXlsxConverter", CatalogEntry("office", "CSV → Excel", "table")),
)

CATALOG: Dict[str, CatalogEntry] = dict(_ENTRIES)
_ORDER: Dict[str, int] = {name: i for i, (name, _) in enumerate(_ENTRIES)}
_GROUP_ORDER: Dict[str, int] = {g.id: i for i, g in enumerate(GROUPS)}

# Ekranda gösterilen tür adları (kullanıcı uzantı yerine bunu okur).
_TYPE_LABELS: Dict[str, str] = {
    ".pdf": "PDF", ".docx": "Word", ".pptx": "PowerPoint", ".xlsx": "Excel",
    ".odt": "ODT", ".odp": "ODP", ".ods": "ODS", ".csv": "CSV", ".jpg": "JPG",
}  # fmt: skip

# Aynı türün farklı yazımları (".jpeg" bir JPG'dir).
_EXT_ALIASES: Dict[str, str] = {".jpeg": ".jpg"}


def entry_for(class_name: str, display_name: str) -> CatalogEntry:
    """Katalog satırı; yoksa 'Diğer' grubunda görünen adıyla."""
    return CATALOG.get(class_name) or CatalogEntry(OTHER_GROUP.id, display_name, "document")


def sort_key(class_name: str, display_name: str) -> Tuple[int, int, str]:
    """Grup sırası, grup içi sıra; katalogda olmayanlar en sonda alfabetik."""
    entry = CATALOG.get(class_name)
    if entry is None:
        return (len(GROUPS), 0, display_name)
    return (_GROUP_ORDER[entry.group], _ORDER[class_name], "")


def groups_with_other() -> List[Group]:
    return [*GROUPS, OTHER_GROUP]


def normalize_ext(ext: str) -> str:
    ext = ext.lower()
    return _EXT_ALIASES.get(ext, ext)


def type_label(ext: Optional[str]) -> str:
    """'.pdf' → 'PDF'; bilinmeyen uzantı büyük harfle."""
    if not ext:
        return ""
    ext = normalize_ext(ext)
    return _TYPE_LABELS.get(ext, ext.lstrip(".").upper())


def ordered_type_labels(exts) -> List[str]:
    """Uzantılardan tekil tür adları; bilinen türler tanıtım sırasıyla (PDF, Word, ...), kalanlar sonda."""
    normalized = {normalize_ext(e) for e in exts}
    known = [_TYPE_LABELS[e] for e in _TYPE_LABELS if e in normalized]
    rest = sorted(type_label(e) for e in normalized if e not in _TYPE_LABELS)
    return known + rest
