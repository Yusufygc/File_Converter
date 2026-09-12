from core.converters.discovery import discover_converter_classes, register_all
from core.converters.registry import ConverterRegistry
from tests._fakes import FakeConverter


def test_registry_register_and_get():
    reg = ConverterRegistry()
    conv = FakeConverter()
    reg.register(conv)

    assert reg.get(".foo", ".bar") is conv
    assert reg.get(".foo", ".missing") is None


def test_registry_all_converters_and_supported_extensions():
    reg = ConverterRegistry()
    reg.register(FakeConverter())

    assert len(reg.all_converters()) == 1
    assert ".foo" in reg.supported_source_extensions()


def test_discovery_finds_all_shipped_converters():
    names = {cls.__name__ for cls in discover_converter_classes()}

    assert names == {
        "PptxToPdfConverter",
        "PdfToDocxConverter",
        "PdfToOdtConverter",
        "PdfToJpgConverter",
        "PdfToPngConverter",
        "JpgToPdfConverter",
    }


def test_register_all_populates_registry_without_duplicates():
    expected_count = len(discover_converter_classes())

    reg = ConverterRegistry()
    register_all(reg)
    register_all(reg)  # iki kez çağırmak yeniden kayıt (overwrite) yapmalı, çoğaltmamalı

    assert len(reg.all_converters()) == expected_count
