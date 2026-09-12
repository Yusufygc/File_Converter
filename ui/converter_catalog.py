"""
Converter Catalog
===================
`registry.all_converters()`'dan UI dropdown listesini JENERİK olarak
üretir. Önceden `options_panel.py` + `main_window.py`'de her dönüşüm
türü için elle yazılan `CONV_*` sabitleri + `addItem()` çağrıları +
`conv_map` dict'i yerine geçer — yeni bir converter registry'ye
kaydolur kaydolmaz (bkz. `core/converters/discovery.py`) burada da
otomatik olarak görünür, bu dosyaya dokunmaya gerek kalmaz.

`_PREFERRED_ORDER` yalnızca dropdown'daki GÖRÜNÜM SIRASINI belirler —
fonksiyonel bir kayıt gerekliliği değildir. Listede olmayan bir
converter alfabetik olarak sona eklenir; yani yeni bir converter bu
listeye eklenmese de dropdown'da doğru biçimde görünmeye devam eder.
"""

from __future__ import annotations

from typing import List, Tuple, Union

from core.interfaces.converter_interface import IConverter, IConverterRegistry

# 2-eleman (source_ext, target_ext) çoğu durumda yeterli. 3-eleman
# (source_ext, target_ext, class_name) yalnızca aynı uzantı çiftini
# paylaşan birden fazla converter olduğunda (örn. üç ayrı .pdf→.pdf
# converter'ı: sıkıştır/böl/birleştir) ayırt etmek için gerekir.
_PREFERRED_ORDER: List[Union[Tuple[str, str], Tuple[str, str, str]]] = [
    (".pptx", ".pdf"),
    (".docx", ".pdf"),
    (".pdf", ".docx"),
    (".pdf", ".odt"),
    (".pdf", ".jpg"),
    (".pdf", ".png"),
    (".pdf", ".pdf", "PdfCompressConverter"),
    (".pdf", ".pdf", "PdfSplitConverter"),
    (".pdf", ".pdf", "PdfMergeConverter"),
    (".jpg", ".pdf"),
]


def _sort_key(converter: IConverter):
    two = (converter.source_extension, converter.target_extension)
    three = (*two, converter.__class__.__name__)
    if three in _PREFERRED_ORDER:
        return (0, _PREFERRED_ORDER.index(three))
    if two in _PREFERRED_ORDER:
        return (0, _PREFERRED_ORDER.index(two))
    return (1, converter.display_name)


def catalog_entries(registry: IConverterRegistry) -> List[IConverter]:
    """Dropdown'da gösterilecek converter listesi, kararlı bir sırayla."""
    return sorted(registry.all_converters(), key=_sort_key)
