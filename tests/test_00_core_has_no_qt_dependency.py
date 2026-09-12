"""
`core/` katmanının backend/frontend ayrımının kanıtı: yalnızca `core`
içindeki modülleri import ettiğimizde PySide6 hiç yüklenmemeli.
Dosya adı `test_00_...` — pytest dosyaları alfabetik sırayla çalıştırdığı
için diğer testler (ki hiçbiri zaten Qt import etmez) bu kontrolü bozmadan
önce çalışır.
"""

import sys


def test_importing_core_does_not_import_qt():
    from core.converters.registry import ConverterRegistry
    from core.converters.discovery import register_all
    from core.conversion_facade import convert_batch

    reg = ConverterRegistry()
    register_all(reg)

    assert len(reg.all_converters()) >= 5
    assert not any(m.startswith("PySide6") for m in sys.modules), (
        "core/ katmanı Qt import etmemeli — backend/frontend ayrımı bozuldu"
    )
