"""
QML Bridge Unit Tests
=====================
AppBridge ve FileListModel'in core katmanıyla doğru entegrasyonunu doğrular.
Tüm Qt importları test fonksiyonları içine alınmıştır (test_00'ın sys.modules
kontrolünü collection aşamasında etkilememesi için).
"""

from pathlib import Path
import pytest


@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_file_list_model_basic_operations(qapp, tmp_path):
    from core.interfaces.converter_interface import ConversionResult
    from ui_qml.bridge.file_list_model import FileListModel

    model = FileListModel()
    assert model.count() == 0

    f1 = tmp_path / "test1.pdf"
    f2 = tmp_path / "test2.pdf"
    f1.write_text("dummy")
    f2.write_text("dummy2")

    added = model.add_files([f1, f2])
    assert added == 2
    assert model.count() == 2
    assert model.all_paths() == [f1, f2]

    # Duplicate add
    added_dup = model.add_files([f1])
    assert added_dup == 0
    assert model.count() == 2

    # Status update
    model.mark_converting(f1)
    res = ConversionResult(source_path=f1, success=True, elapsed_seconds=0.5, output_path=tmp_path / "test1.docx")
    model.mark_result(res)

    # Remove single
    assert model.remove_at(0) is True
    assert model.count() == 1
    assert model.all_paths() == [f2]

    # Clear
    model.clear()
    assert model.count() == 0


def test_app_bridge_initialization(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    assert len(bridge.converters) >= 5
    assert bridge.currentConverterIndex >= 0
    assert bridge.currentConverter is not None
    assert bridge.themeMode in ("dark", "light")


def test_app_bridge_theme_toggle(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    initial_theme = bridge.themeMode
    bridge.toggleTheme()
    new_theme = bridge.themeMode
    assert new_theme != initial_theme
    bridge.toggleTheme()
    assert bridge.themeMode == initial_theme


def test_app_bridge_add_files_from_urls(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    bridge.selectConverter(0)  # first converter e.g. pptx to pdf
    accepted_ext = bridge.currentConverter["acceptedExts"][0]

    valid_file = tmp_path / f"sample{accepted_ext}"
    valid_file.write_text("dummy")
    invalid_file = tmp_path / "sample.randomext"
    invalid_file.write_text("dummy")

    bridge.clearFiles()
    bridge.addFilesFromUrls([str(valid_file), str(invalid_file)])

    assert bridge.fileCount == 1
    assert bridge.fileListModel.all_paths() == [valid_file]


def test_app_bridge_categorized_converters(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    cats = bridge.categorizedConverters
    # Niyete göre 5 grup, katalog sırasıyla; "Diğer" yalnızca kataloğa girmemiş converter varsa çıkar
    assert [c["id"] for c in cats] == ["to_pdf", "from_pdf", "pdf_edit", "pdf_secure", "office"]
    from_pdf = next(c for c in cats if c["id"] == "from_pdf")
    assert all(item["sourceExt"] == ".pdf" for item in from_pdf["items"])

    total_items = sum(len(c["items"]) for c in cats)
    assert total_items == len(bridge.converters)
    for cat in cats:
        for item in cat["items"]:
            assert "index" in item
            assert "displayName" in item
            assert "icon" in item
            assert "badge" in item
            assert "shortName" in item



def _select_by_class(bridge, cls_name):
    for item in bridge.converters:
        if item["className"] == cls_name:
            bridge.selectConverter(item["index"])
            return item
    raise AssertionError(f"{cls_name} bulunamadı")


def test_option_specs_published_and_extra_reaches_options(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    item = _select_by_class(bridge, "PdfWatermarkConverter")
    keys = [s["key"] for s in item["optionSpecs"]]
    assert keys == ["text", "opacity", "font_size"]
    assert bridge.currentConverter["optionSpecs"][0]["required"] is True

    bridge.setExtraOption("text", "GİZLİ")
    bridge.setExtraOption("bilinmeyen", "yok sayılır")
    opts = bridge._build_options()
    assert opts.extra["text"] == "GİZLİ"
    assert opts.extra["opacity"] == 30  # şema varsayılanı
    assert "bilinmeyen" not in opts.extra


def test_extra_options_reset_on_converter_change_and_not_persisted(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    _select_by_class(bridge, "PdfProtectConverter")
    bridge.setExtraOption("password", "cok-gizli")
    _select_by_class(bridge, "PdfRotateConverter")
    assert bridge._build_options().extra == {"angle": 90}

    _select_by_class(bridge, "PdfProtectConverter")
    assert bridge._build_options().extra == {"password": None}
    stored = [bridge._settings._qs.value(k) for k in bridge._settings._qs.allKeys()]
    assert "cok-gizli" not in [str(v) for v in stored]


def test_converters_without_schema_publish_empty_specs(qapp):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    item = _select_by_class(bridge, "PdfCompressConverter")
    assert item["optionSpecs"] == []
    assert bridge._build_options().extra == {}



# ── Dosya-önce akışı ─────────────────────────────────────────────────

def _touch(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"x")
    return path


def test_dropping_incompatible_file_selects_first_matching_tool(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    _select_by_class(bridge, "DocxToPdfConverter")
    bridge.addFilesFromUrls([str(_touch(tmp_path, "a.pdf"))])

    assert bridge.currentConverter["className"] == "PdfToDocxConverter"  # katalogda .pdf kabul eden ilk araç
    assert bridge.fileCount == 1
    assert bridge.fileTypeFilter == ".pdf" and bridge.fileTypeLabel == "PDF"


def test_compatible_tool_switch_keeps_files_incompatible_clears(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    bridge.clearFiles()
    bridge.addFilesFromUrls([str(_touch(tmp_path, "a.pdf")), str(_touch(tmp_path, "b.pdf"))])
    _select_by_class(bridge, "PdfMergeConverter")
    assert bridge.fileCount == 2  # PDF aracından PDF aracına geçiş listeyi boşaltmaz

    _select_by_class(bridge, "XlsxToCsvConverter")
    assert bridge.fileCount == 0 and bridge.fileTypeFilter == ""


def test_mixed_drop_keeps_majority_type_and_reports_rest(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    bridge.clearFiles()
    files = [_touch(tmp_path, n) for n in ("a.pdf", "b.pdf", "c.pdf", "d.docx", "e.docx", "f.zip")]
    bridge.addFilesFromUrls([str(f) for f in files])

    assert bridge.fileTypeFilter == ".pdf" and bridge.fileCount == 3
    assert bridge.statusKind == "warning"
    assert "Word" in bridge.statusMessage and "desteklenmeyen" in bridge.statusMessage


def test_existing_list_type_wins_over_new_majority(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    bridge.clearFiles()
    bridge.addFilesFromUrls([str(_touch(tmp_path, "a.pdf"))])
    bridge.addFilesFromUrls([str(_touch(tmp_path, n)) for n in ("x.docx", "y.docx")])

    assert bridge.fileTypeFilter == ".pdf" and bridge.fileCount == 1


def test_jpeg_and_jpg_are_the_same_type(qapp, tmp_path):
    from ui_qml.bridge.app_bridge import AppBridge

    bridge = AppBridge()
    bridge.clearFiles()
    bridge.addFilesFromUrls([str(_touch(tmp_path, "a.jpeg")), str(_touch(tmp_path, "b.JPG"))])

    assert bridge.currentConverter["className"] == "JpgToPdfConverter"
    assert bridge.fileCount == 2 and bridge.fileTypeFilter == ".jpg"
