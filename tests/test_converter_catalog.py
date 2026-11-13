"""
Kenar çubuğu kataloğu (`ui_qml/bridge/converter_catalog.py`): her keşfedilen
converter bir gruba atanmış mı, gruplar dengeli mi, sıra deterministik mi.
Qt gerektirmez.
"""

from core.converters.discovery import discover_converter_classes
from ui_qml.bridge import converter_catalog as catalog


def test_every_discovered_converter_has_a_catalog_entry():
    names = {cls.__name__ for cls in discover_converter_classes()}
    missing = names - set(catalog.CATALOG)
    assert missing == set(), (
        f"Katalogda olmayan converter(lar): {missing}. ui_qml/bridge/converter_catalog.py "
        "_ENTRIES tablosuna grup/kısa ad/ikon satırı ekleyin (yoksa 'Diğer' grubunda görünür)."
    )
    stale = set(catalog.CATALOG) - names
    assert stale == set(), f"Katalogda artık var olmayan converter(lar): {stale}"


def test_catalog_entries_point_to_known_groups_and_groups_are_balanced():
    group_ids = {g.id for g in catalog.GROUPS}
    sizes = {g: 0 for g in group_ids}
    for entry in catalog.CATALOG.values():
        assert entry.group in group_ids
        assert entry.short_name and entry.icon
        sizes[entry.group] += 1
    # Hiçbir grup boş ya da tek başına listenin yarısından büyük olmasın (eski "Belgeler 11" sorunu)
    assert all(1 <= n <= 10 for n in sizes.values()), sizes


def test_unknown_converter_falls_back_to_other_group_last():
    entry = catalog.entry_for("YeniConverter", "Yeni → Biçim")
    assert entry.group == catalog.OTHER_GROUP.id and entry.short_name == "Yeni → Biçim"
    known = catalog.sort_key("PdfToDocxConverter", "PDF → DOCX")
    assert catalog.sort_key("YeniConverter", "Yeni") > known


def test_type_labels_and_aliases():
    assert catalog.normalize_ext(".JPEG") == ".jpg"
    assert catalog.type_label(".docx") == "Word"
    assert catalog.type_label(".xyz") == "XYZ"
    assert catalog.ordered_type_labels({".jpeg", ".pdf", ".jpg", ".docx"}) == ["PDF", "Word", "JPG"]
